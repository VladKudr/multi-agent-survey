"""Simulation runner for executing agent surveys with user LLM config."""

import asyncio
from datetime import datetime
from typing import Any, List
from uuid import UUID

import structlog

from config.database import get_db_context
from config.yaml_loader import get_config_loader
from llm.gateway import LLMResponse, get_llm_gateway
from llm.prompt_builder import AgentPromptBuilder, PromptBuilder
from llm.response_parser import ResponseParser
from models.simulation import SimulationResult, SimulationRun
from schemas.agent import AgentConfig, AgentResponse
from schemas.llm_config import LLMConfigWithKey
from schemas.simulation import SimulationProgressEvent, SimulationStatus
from schemas.survey import SurveyResponse
from services.llm_config_service import LLMConfigService
from services.survey_service import SurveyService

logger = structlog.get_logger()


class SimulationRunner:
    """Runner for executing agent simulations with user-specific LLM config."""

    def __init__(self, user_llm_config: LLMConfigWithKey | None = None):
        """Initialize runner with optional user LLM config.
        
        Args:
            user_llm_config: User's LLM configuration. If None, uses system defaults.
        """
        self.user_llm_config = user_llm_config
        self.llm_gateway = get_llm_gateway(user_config=user_llm_config)
        self.config_loader = get_config_loader()
        self.response_parser = ResponseParser()

    async def run_simulation(
        self,
        simulation_id: str,
        organization_id: str,
        survey: SurveyResponse,
        agent_configs: List[AgentConfig],
        max_parallel: int = 4,
        temperature_override: float | None = None,
        progress_callback: Any | None = None,
    ) -> dict:
        """Run simulation for all agents.

        Args:
            simulation_id: Simulation run ID
            organization_id: Organization ID
            survey: Survey to run
            agent_configs: List of agent configs
            max_parallel: Max parallel executions
            temperature_override: Override temperature
            progress_callback: Callback for progress updates

        Returns:
            Results summary
        """
        total_agents = len(agent_configs)
        completed = 0
        failed = 0

        logger.info(
            "simulation_started",
            simulation_id=simulation_id,
            total_agents=total_agents,
            provider=self.user_llm_config.provider if self.user_llm_config else "default",
            model=self.user_llm_config.model if self.user_llm_config else "default",
        )

        # Create semaphore for limiting parallelism
        semaphore = asyncio.Semaphore(max_parallel)

        async def run_agent_with_limit(agent_config: AgentConfig) -> None:
            """Run agent with semaphore limit."""
            nonlocal completed, failed
            async with semaphore:
                try:
                    await self._process_agent(
                        simulation_id=simulation_id,
                        organization_id=organization_id,
                        survey=survey,
                        agent_config=agent_config,
                        temperature_override=temperature_override,
                    )
                    completed += 1
                except Exception as e:
                    logger.error(
                        "agent_processing_failed",
                        simulation_id=simulation_id,
                        agent_id=agent_config.id,
                        error=str(e),
                    )
                    failed += 1

                # Send progress update
                if progress_callback:
                    await progress_callback(
                        SimulationProgressEvent(
                            type="progress",
                            simulation_id=simulation_id,
                            status=SimulationStatus.RUNNING,
                            completed_agents=completed,
                            total_agents=total_agents,
                            current_agent=agent_config.id,
                            message=f"Processed {agent_config.company_name}",
                        )
                    )

        # Run all agents
        await asyncio.gather(*[run_agent_with_limit(ac) for ac in agent_configs])

        logger.info(
            "simulation_completed",
            simulation_id=simulation_id,
            completed=completed,
            failed=failed,
        )

        return {
            "simulation_id": simulation_id,
            "total_agents": total_agents,
            "completed": completed,
            "failed": failed,
        }

    async def _process_agent(
        self,
        simulation_id: str,
        organization_id: str,
        survey: SurveyResponse,
        agent_config: AgentConfig,
        temperature_override: float | None = None,
    ) -> None:
        """Process single agent for all questions."""
        prompt_builder = AgentPromptBuilder(agent_config)
        system_prompt = PromptBuilder.build_system_prompt(agent_config)

        async with get_db_context() as db:
            for question in survey.questions:
                try:
                    result = await self._process_question(
                        system_prompt=system_prompt,
                        prompt_builder=prompt_builder,
                        question=question,
                        agent_config=agent_config,
                        organization_id=organization_id,
                        temperature_override=temperature_override,
                    )

                    # Save result
                    db_result = SimulationResult(
                        simulation_run_id=simulation_id,
                        agent_id=agent_config.id,
                        question_id=question.get("id") or question.get("text", "")[:50],
                        response_type=result.response_type,
                        response_value=result.response_value,
                        reasoning=result.reasoning,
                        answer_text=result.answer_text,
                        tokens_used=result.tokens_used,
                        response_time_ms=result.response_time_ms,
                    )
                    db.add(db_result)

                except Exception as e:
                    logger.error(
                        "question_processing_failed",
                        simulation_id=simulation_id,
                        agent_id=agent_config.id,
                        question=question.get("text", "")[:50],
                        error=str(e),
                    )
                    raise

    async def _process_question(
        self,
        system_prompt: str,
        prompt_builder: AgentPromptBuilder,
        question: dict,
        agent_config: AgentConfig,
        organization_id: str,
        temperature_override: float | None = None,
    ) -> AgentResponse:
        """Process single question for an agent."""
        q_type = question.get("type")
        q_text = question.get("text", "")

        # Build user prompt based on question type
        if q_type in ["likert_scale", "rating"]:
            user_prompt = PromptBuilder.build_quantitative_prompt(
                question_text=q_text,
                min_value=question.get("min_value", 1),
                max_value=question.get("max_value", 5),
                min_label=question.get("min_label"),
                max_label=question.get("max_label"),
            )
            is_quantitative = True
            # Use lower temperature for quantitative
            effective_temperature = temperature_override or 0.3
            max_tokens = 300
        else:
            user_prompt = prompt_builder.build_qualitative_prompt(
                question_text=q_text,
                min_words=question.get("min_words", 150),
                max_words=question.get("max_words", 400),
            )
            is_quantitative = False
            effective_temperature = temperature_override or 0.7
            max_tokens = 800

        # Call LLM
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        llm_response = await self.llm_gateway.generate(
            messages=messages,
            temperature=effective_temperature,
            max_tokens=max_tokens,
            organization_id=organization_id,
            response_format={"type": "json_object"},
        )

        # Parse response
        if is_quantitative:
            parsed = self.response_parser.parse_quantitative_response(
                llm_response.content, agent_config.id
            )
        else:
            parsed = self.response_parser.parse_qualitative_response(
                llm_response.content, agent_config.id
            )

        # Add metadata
        parsed.tokens_used = llm_response.tokens_total
        parsed.response_time_ms = llm_response.response_time_ms

        return parsed


async def run_simulation_with_user_config(
    simulation_id: str,
    organization_id: str,
    survey: SurveyResponse,
    agent_configs: List[AgentConfig],
    user_id: str,
    max_parallel: int = 4,
) -> dict:
    """Run simulation with user's LLM configuration.
    
    This is a helper function that loads the user's LLM config and runs the simulation.
    
    Args:
        simulation_id: Simulation run ID
        organization_id: Organization ID
        survey: Survey to run
        agent_configs: List of agent configs
        user_id: User ID to load LLM config for
        max_parallel: Max parallel executions
        
    Returns:
        Results summary
    """
    async with get_db_context() as db:
        # Load user's LLM config
        llm_service = LLMConfigService()
        user_config = await llm_service.get_config(
            db=db,
            user_id=UUID(user_id),
            include_api_key=True,
        )
        
        if not user_config:
            raise ValueError(f"User {user_id} does not have LLM configuration")
        
        if not user_config.api_key:
            raise ValueError(f"User {user_id} LLM configuration is missing API key")
        
        # Create runner with user config
        runner = SimulationRunner(user_llm_config=user_config)
        
        # Run simulation
        results = await runner.run_simulation(
            simulation_id=simulation_id,
            organization_id=organization_id,
            survey=survey,
            agent_configs=agent_configs,
            max_parallel=max_parallel,
        )
        
        # Increment request count
        await llm_service.increment_request_count(db, UUID(user_id))
        
        return results
