"""Simulation API routes."""

from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Query,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth import get_current_active_user
from config.database import get_db
from models.user import User
from schemas.simulation import (
    PaginatedSimulationResponse,
    SimulationCreate,
    SimulationProgressEvent,
    SimulationResponse,
    SimulationResultSummary,
    SimulationStatus,
)
from services.agent_service import AgentService
from services.llm_config_service import LLMConfigService
from services.simulation_service import SimulationService
from workers.simulation_tasks import run_simulation_task

router = APIRouter(prefix="/simulations", tags=["Simulations"])


def get_simulation_service() -> SimulationService:
    """Get simulation service instance."""
    return SimulationService()


def get_agent_service() -> AgentService:
    """Get agent service instance."""
    return AgentService()


def get_llm_config_service() -> LLMConfigService:
    """Get LLM config service instance."""
    return LLMConfigService()


@router.post(
    "",
    response_model=SimulationResponse,
    status_code=status.HTTP_202_ACCEPTED,
    description="Create and start a new simulation run",
)
async def create_simulation(
    data: SimulationCreate,
    background_tasks: BackgroundTasks,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
    service: SimulationService = Depends(get_simulation_service),
    agent_service: AgentService = Depends(get_agent_service),
    llm_service: LLMConfigService = Depends(get_llm_config_service),
) -> SimulationResponse:
    """Create and queue a simulation run."""
    # Validate agent IDs
    invalid_agents = await agent_service.validate_agent_ids(data.agent_ids)
    if invalid_agents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid agent IDs: {invalid_agents}",
        )

    # Check if user has LLM config
    user_config = await llm_service.get_config(
        db=db,
        user_id=current_user.id,
        include_api_key=False,
    )
    if not user_config:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User does not have LLM configuration. Please configure LLM settings first.",
        )
    
    if not user_config.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="LLM configuration is inactive. Please check your settings.",
        )

    # Create simulation
    simulation = await service.create_simulation(
        db=db,
        organization_id=current_user.organization_id,
        data=data,
    )

    # Queue Celery task with user_id for LLM config
    run_simulation_task.delay(
        str(simulation.id),
        str(current_user.organization_id),
        str(current_user.id),
    )

    return simulation


@router.get(
    "",
    response_model=PaginatedSimulationResponse,
    description="List simulation runs",
)
async def list_simulations(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
    service: SimulationService = Depends(get_simulation_service),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    status: SimulationStatus | None = Query(None, description="Filter by status"),
) -> PaginatedSimulationResponse:
    """List simulations with pagination."""
    return await service.list_simulations(
        db=db,
        organization_id=current_user.organization_id,
        page=page,
        limit=limit,
        status=status,
    )


@router.get(
    "/{simulation_id}",
    response_model=SimulationResponse,
    description="Get simulation by ID",
)
async def get_simulation(
    simulation_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
    service: SimulationService = Depends(get_simulation_service),
) -> SimulationResponse:
    """Get simulation details."""
    return await service.get_simulation(
        db=db,
        organization_id=current_user.organization_id,
        simulation_id=simulation_id,
    )


@router.get(
    "/{simulation_id}/results",
    description="Get simulation results",
)
async def get_simulation_results(
    simulation_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
    service: SimulationService = Depends(get_simulation_service),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=200, description="Items per page"),
) -> dict:
    """Get detailed simulation results."""
    items, total = await service.get_simulation_results(
        db=db,
        organization_id=current_user.organization_id,
        simulation_id=simulation_id,
        page=page,
        limit=limit,
    )

    return {
        "items": items,
        "total_count": total,
        "page": page,
        "limit": limit,
    }


@router.get(
    "/{simulation_id}/summary",
    response_model=SimulationResultSummary,
    description="Get simulation results summary",
)
async def get_simulation_summary(
    simulation_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
    service: SimulationService = Depends(get_simulation_service),
) -> SimulationResultSummary:
    """Get simulation results summary with analytics."""
    return await service.get_results_summary(
        db=db,
        organization_id=current_user.organization_id,
        simulation_id=simulation_id,
    )


@router.websocket("/{simulation_id}/ws")
async def simulation_websocket(
    websocket: WebSocket,
    simulation_id: UUID,
    token: str,
    db: AsyncSession = Depends(get_db),
    service: SimulationService = Depends(get_simulation_service),
):
    """WebSocket for real-time simulation progress updates."""
    # TODO: Validate token and get user
    # For now, accept all connections
    await websocket.accept()

    try:
        while True:
            # Get current simulation status
            # This is a simplified version - in production, use Redis pub/sub
            # to broadcast updates from the Celery worker

            try:
                # Try to get simulation (would need proper auth in production)
                simulation = await service.get_simulation(
                    db=db,
                    organization_id=None,  # Would get from token
                    simulation_id=simulation_id,
                )

                event = SimulationProgressEvent(
                    simulation_id=str(simulation_id),
                    status=simulation.status,
                    completed_agents=simulation.completed_agents,
                    total_agents=simulation.total_agents,
                )

                await websocket.send_json(event.model_dump())

                # If completed or failed, close connection
                if simulation.status in [
                    SimulationStatus.COMPLETED,
                    SimulationStatus.FAILED,
                ]:
                    await websocket.close()
                    break

            except Exception:
                pass

            # Wait before next update
            import asyncio

            await asyncio.sleep(2)

    except WebSocketDisconnect:
        pass
