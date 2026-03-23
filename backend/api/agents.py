"""Agent API routes."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth import get_current_active_user
from config.database import get_db
from models.user import User
from schemas.agent import (
    AgentDetailResponse,
    PaginatedAgentResponse,
)
from services.agent_service import AgentService

router = APIRouter(prefix="/agents", tags=["Agents"])


def get_agent_service() -> AgentService:
    """Get agent service instance."""
    return AgentService()


@router.get(
    "",
    response_model=PaginatedAgentResponse,
    description="List available agent personas",
)
async def list_agents(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
    service: AgentService = Depends(get_agent_service),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    industry: str | None = Query(None, description="Filter by industry"),
    size: str | None = Query(None, description="Filter by company size"),
    region: str | None = Query(None, description="Filter by region"),
) -> PaginatedAgentResponse:
    """List available agents with optional filtering."""
    items, total = await service.list_agents(
        db=db,
        organization_id=current_user.organization_id,
        page=page,
        limit=limit,
        industry=industry,
        size=size,
        region=region,
    )

    return PaginatedAgentResponse(
        items=items,
        total_count=total,
        page=page,
        limit=limit,
    )


@router.get(
    "/filters",
    description="Get available filter options",
)
async def get_filters(
    current_user: Annotated[User, Depends(get_current_active_user)],
    service: AgentService = Depends(get_agent_service),
) -> dict:
    """Get available filter values from all agents."""
    return await service.get_available_filters()


@router.get(
    "/{agent_id}",
    response_model=AgentDetailResponse,
    description="Get detailed agent configuration",
)
async def get_agent(
    agent_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
    service: AgentService = Depends(get_agent_service),
) -> AgentDetailResponse:
    """Get detailed agent information."""
    return await service.get_agent(
        db=db,
        organization_id=current_user.organization_id,
        agent_id=agent_id,
    )
