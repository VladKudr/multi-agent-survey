"""Simulation service for managing simulation runs."""

from datetime import datetime
from typing import List
from uuid import UUID

import structlog
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.simulation import SimulationResult, SimulationRun
from schemas.simulation import (
    PaginatedSimulationResponse,
    SimulationCreate,
    SimulationListItem,
    SimulationResponse,
    SimulationResultDetail,
    SimulationResultSummary,
    SimulationStatus,
)

logger = structlog.get_logger()


class SimulationService:
    """Service for simulation run operations."""

    async def create_simulation(
        self,
        db: AsyncSession,
        organization_id: UUID,
        data: SimulationCreate,
    ) -> SimulationResponse:
        """Create a new simulation run.

        Args:
            db: Database session
            organization_id: Organization ID
            data: Simulation creation data

        Returns:
            Created simulation response
        """
        simulation = SimulationRun(
            organization_id=organization_id,
            survey_id=data.survey_id,
            name=data.name,
            description=data.description,
            agent_ids=data.agent_ids,
            total_agents=len(data.agent_ids),
            status=SimulationStatus.PENDING.value,
            completed_agents=0,
            failed_agents=0,
        )

        db.add(simulation)
        await db.flush()

        logger.info(
            "simulation_created",
            simulation_id=str(simulation.id),
            organization_id=str(organization_id),
            survey_id=str(data.survey_id),
            agent_count=len(data.agent_ids),
        )

        return SimulationResponse.model_validate(simulation)

    async def get_simulation(
        self,
        db: AsyncSession,
        organization_id: UUID,
        simulation_id: UUID,
    ) -> SimulationResponse:
        """Get simulation by ID.

        Args:
            db: Database session
            organization_id: Organization ID
            simulation_id: Simulation UUID

        Returns:
            Simulation response
        """
        result = await db.execute(
            select(SimulationRun).where(
                SimulationRun.id == simulation_id,
                SimulationRun.organization_id == organization_id,
            )
        )
        simulation = result.scalar_one_or_none()

        if not simulation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Simulation not found",
            )

        return SimulationResponse.model_validate(simulation)

    async def list_simulations(
        self,
        db: AsyncSession,
        organization_id: UUID,
        page: int = 1,
        limit: int = 20,
        status: SimulationStatus | None = None,
    ) -> PaginatedSimulationResponse:
        """List simulations with pagination.

        Args:
            db: Database session
            organization_id: Organization ID
            page: Page number
            limit: Items per page
            status: Filter by status

        Returns:
            Paginated simulation response
        """
        query = select(SimulationRun).where(
            SimulationRun.organization_id == organization_id
        )

        if status:
            query = query.where(SimulationRun.status == status.value)

        # Count total
        total_result = await db.execute(
            select(SimulationRun.id).where(
                SimulationRun.organization_id == organization_id
            )
        )
        total = len(total_result.scalars().all())

        # Paginate
        query = query.order_by(SimulationRun.created_at.desc())
        query = query.offset((page - 1) * limit).limit(limit)
        result = await db.execute(query)
        simulations = result.scalars().all()

        items = [SimulationListItem.model_validate(s) for s in simulations]

        return PaginatedSimulationResponse(
            items=items,
            total_count=total,
            page=page,
            limit=limit,
        )

    async def get_simulation_results(
        self,
        db: AsyncSession,
        organization_id: UUID,
        simulation_id: UUID,
        page: int = 1,
        limit: int = 50,
    ) -> tuple[List[SimulationResultDetail], int]:
        """Get detailed results for a simulation.

        Args:
            db: Database session
            organization_id: Organization ID
            simulation_id: Simulation UUID
            page: Page number
            limit: Items per page

        Returns:
            Tuple of (results list, total count)
        """
        # Verify simulation exists and belongs to org
        sim_result = await db.execute(
            select(SimulationRun.id).where(
                SimulationRun.id == simulation_id,
                SimulationRun.organization_id == organization_id,
            )
        )
        if not sim_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Simulation not found",
            )

        # Get results
        query = (
            select(SimulationResult)
            .where(SimulationResult.simulation_run_id == simulation_id)
            .order_by(SimulationResult.created_at)
        )

        # Count total
        count_result = await db.execute(
            select(SimulationResult.id).where(
                SimulationResult.simulation_run_id == simulation_id
            )
        )
        total = len(count_result.scalars().all())

        # Paginate
        query = query.offset((page - 1) * limit).limit(limit)
        result = await db.execute(query)
        results = result.scalars().all()

        items = [SimulationResultDetail.model_validate(r) for r in results]

        return items, total

    async def get_results_summary(
        self,
        db: AsyncSession,
        organization_id: UUID,
        simulation_id: UUID,
    ) -> SimulationResultSummary:
        """Get summary of simulation results.

        Args:
            db: Database session
            organization_id: Organization ID
            simulation_id: Simulation UUID

        Returns:
            Results summary
        """
        # Verify simulation exists
        sim_result = await db.execute(
            select(SimulationRun).where(
                SimulationRun.id == simulation_id,
                SimulationRun.organization_id == organization_id,
            )
        )
        simulation = sim_result.scalar_one_or_none()

        if not simulation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Simulation not found",
            )

        # Get all results
        results_result = await db.execute(
            select(SimulationResult).where(
                SimulationResult.simulation_run_id == simulation_id
            )
        )
        results = results_result.scalars().all()

        # Calculate summaries
        quantitative_summary = {}
        agent_breakdown = {}
        total_tokens = 0

        for r in results:
            total_tokens += r.tokens_used

            # Quantitative summary by question
            if r.response_type == "quantitative" and r.response_value is not None:
                if r.question_id not in quantitative_summary:
                    quantitative_summary[r.question_id] = {
                        "values": [],
                        "count": 0,
                        "sum": 0,
                    }
                quantitative_summary[r.question_id]["values"].append(r.response_value)
                quantitative_summary[r.question_id]["count"] += 1
                quantitative_summary[r.question_id]["sum"] += r.response_value

            # Agent breakdown
            if r.agent_id not in agent_breakdown:
                agent_breakdown[r.agent_id] = {
                    "responses": 0,
                    "tokens_used": 0,
                    "avg_response_time_ms": 0,
                }
            agent_breakdown[r.agent_id]["responses"] += 1
            agent_breakdown[r.agent_id]["tokens_used"] += r.tokens_used

        # Calculate means and std for quantitative
        for q_id, stats in quantitative_summary.items():
            values = stats.pop("values")
            stats["mean"] = stats["sum"] / stats["count"] if stats["count"] > 0 else 0
            stats["min"] = min(values) if values else 0
            stats["max"] = max(values) if values else 0

        return SimulationResultSummary(
            simulation_id=simulation_id,
            total_responses=len(results),
            quantitative_summary=quantitative_summary,
            qualitative_themes=None,  # Populated by NLP service
            agent_breakdown=agent_breakdown,
            total_tokens_used=total_tokens,
            total_cost_estimate=None,  # TODO: Calculate from token usage
        )

    async def update_status(
        self,
        db: AsyncSession,
        simulation_id: UUID,
        status: SimulationStatus,
        celery_task_id: str | None = None,
    ) -> None:
        """Update simulation status.

        Args:
            db: Database session
            simulation_id: Simulation UUID
            status: New status
            celery_task_id: Optional Celery task ID
        """
        result = await db.execute(
            select(SimulationRun).where(SimulationRun.id == simulation_id)
        )
        simulation = result.scalar_one_or_none()

        if not simulation:
            return

        simulation.status = status.value

        if celery_task_id:
            simulation.celery_task_id = celery_task_id

        if status == SimulationStatus.RUNNING and not simulation.started_at:
            simulation.started_at = datetime.utcnow()
        elif status in [SimulationStatus.COMPLETED, SimulationStatus.FAILED]:
            simulation.completed_at = datetime.utcnow()

        await db.flush()

        logger.info(
            "simulation_status_updated",
            simulation_id=str(simulation_id),
            status=status.value,
        )
