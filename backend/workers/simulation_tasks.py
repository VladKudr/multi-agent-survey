"""Celery tasks for simulation execution."""

import asyncio
from datetime import datetime
from uuid import UUID

import structlog

from config.database import get_db_context
from config.yaml_loader import get_config_loader
from llm.simulation_runner import run_simulation_with_user_config
from models.simulation import SimulationRun
from schemas.simulation import SimulationStatus
from services.simulation_service import SimulationService
from services.survey_service import SurveyService
from workers.celery_app import celery_app, get_event_loop

logger = structlog.get_logger()


@celery_app.task(bind=True, max_retries=3)
def run_simulation_task(self, simulation_id: str, organization_id: str, user_id: str) -> dict:
    """Celery task to run a simulation with user's LLM config.

    Args:
        self: Celery task instance
        simulation_id: Simulation run UUID
        organization_id: Organization UUID
        user_id: User UUID (for LLM config)

    Returns:
        Result summary dict
    """
    loop = get_event_loop()
    return loop.run_until_complete(
        _run_simulation_async(self, simulation_id, organization_id, user_id)
    )


async def _run_simulation_async(
    task_instance, simulation_id: str, organization_id: str, user_id: str
) -> dict:
    """Async implementation of simulation task."""
    sim_uuid = UUID(simulation_id)
    org_uuid = UUID(organization_id)

    async with get_db_context() as db:
        sim_service = SimulationService()
        survey_service = SurveyService()
        config_loader = get_config_loader()

        try:
            # Update status to running
            await sim_service.update_status(
                db, sim_uuid, SimulationStatus.RUNNING, task_instance.request.id
            )

            # Get simulation details
            simulation = await sim_service.get_simulation(db, org_uuid, sim_uuid)

            # Get survey
            survey = await survey_service.get_survey(
                db, org_uuid, simulation.survey_id
            )

            # Load agent configs
            agent_configs = []
            for agent_id in simulation.agent_ids:
                try:
                    config = config_loader.load_config(agent_id)
                    agent_configs.append(config)
                except Exception as e:
                    logger.error(
                        "agent_config_load_failed",
                        simulation_id=simulation_id,
                        agent_id=agent_id,
                        error=str(e),
                    )

            if not agent_configs:
                raise ValueError("No valid agent configs found")

            # Run simulation with user config
            results = await run_simulation_with_user_config(
                simulation_id=simulation_id,
                organization_id=organization_id,
                survey=survey,
                agent_configs=agent_configs,
                user_id=user_id,
                max_parallel=4,
            )

            # Update status to completed
            await sim_service.update_status(db, sim_uuid, SimulationStatus.COMPLETED)

            # Update completed/failed counts
            result = await db.execute(
                select(SimulationRun).where(SimulationRun.id == sim_uuid)
            )
            sim_run = result.scalar_one()
            sim_run.completed_agents = results["completed"]
            sim_run.failed_agents = results["failed"]
            await db.flush()

            logger.info(
                "simulation_task_completed",
                simulation_id=simulation_id,
                results=results,
            )

            return {
                "status": "completed",
                "simulation_id": simulation_id,
                **results,
            }

        except Exception as e:
            logger.error(
                "simulation_task_failed",
                simulation_id=simulation_id,
                error=str(e),
                error_type=type(e).__name__,
            )

            # Update status to failed
            await sim_service.update_status(db, sim_uuid, SimulationStatus.FAILED)

            # Retry on certain errors
            if task_instance.request.retries < 3:
                raise task_instance.retry(exc=e, countdown=60)

            raise


@celery_app.task
def cleanup_old_simulations(days: int = 7) -> int:
    """Clean up old simulation results.

    Args:
        days: Age in days to consider old

    Returns:
        Number of records deleted
    """
    loop = get_event_loop()
    return loop.run_until_complete(_cleanup_old_simulations_async(days))


async def _cleanup_old_simulations_async(days: int) -> int:
    """Async implementation of cleanup task."""
    from datetime import timedelta

    from sqlalchemy import delete

    from models.simulation import SimulationResult, SimulationRun

    cutoff_date = datetime.utcnow() - timedelta(days=days)

    async with get_db_context() as db:
        # Delete old results first
        result = await db.execute(
            delete(SimulationResult).where(
                SimulationResult.created_at < cutoff_date
            )
        )
        deleted_results = result.rowcount

        # Delete old runs
        result = await db.execute(
            delete(SimulationRun).where(
                SimulationRun.created_at < cutoff_date,
                SimulationRun.status.in_(["completed", "failed", "cancelled"]),
            )
        )
        deleted_runs = result.rowcount

        await db.commit()

        logger.info(
            "old_simulations_cleaned",
            deleted_results=deleted_results,
            deleted_runs=deleted_runs,
            cutoff_date=cutoff_date.isoformat(),
        )

        return deleted_results + deleted_runs


@celery_app.task
def calculate_simulation_analytics(simulation_id: str) -> dict:
    """Calculate analytics for completed simulation.

    Args:
        simulation_id: Simulation UUID

    Returns:
        Analytics results
    """
    loop = get_event_loop()
    return loop.run_until_complete(
        _calculate_analytics_async(simulation_id)
    )


async def _calculate_analytics_async(simulation_id: str) -> dict:
    """Async implementation of analytics calculation."""
    from services.nlp_service import NLPService

    async with get_db_context() as db:
        nlp_service = NLPService()
        sim_uuid = UUID(simulation_id)

        try:
            # Get results
            result = await db.execute(
                select(SimulationRun).where(SimulationRun.id == sim_uuid)
            )
            simulation = result.scalar_one_or_none()

            if not simulation:
                return {"error": "Simulation not found"}

            # Extract qualitative responses
            qualitative_texts = [
                r.answer_text
                for r in simulation.results
                if r.answer_text and r.response_type == "qualitative"
            ]

            themes = None
            if qualitative_texts:
                themes = await nlp_service.extract_themes(qualitative_texts)

            # Update summary
            summary = simulation.results_summary or {}
            summary["qualitative_themes"] = themes
            simulation.results_summary = summary
            await db.flush()

            return {
                "simulation_id": simulation_id,
                "themes_extracted": len(themes) if themes else 0,
                "themes": themes,
            }

        except Exception as e:
            logger.error(
                "analytics_calculation_failed",
                simulation_id=simulation_id,
                error=str(e),
            )
            return {"error": str(e)}
