"""Agent service for managing agent configurations."""

from typing import List
from uuid import UUID

import structlog
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config.yaml_loader import AgentConfigLoader, get_config_loader
from schemas.agent import AgentConfig, AgentDetailResponse, AgentListItem

logger = structlog.get_logger()


class AgentService:
    """Service for agent configuration operations."""

    def __init__(self, config_loader: AgentConfigLoader | None = None):
        """Initialize with config loader."""
        self.config_loader = config_loader or get_config_loader()

    async def list_agents(
        self,
        db: AsyncSession,
        organization_id: UUID,
        page: int = 1,
        limit: int = 20,
        industry: str | None = None,
        size: str | None = None,
        region: str | None = None,
    ) -> tuple[List[AgentListItem], int]:
        """List available agents with optional filtering.

        Args:
            db: Database session
            organization_id: Organization ID for multi-tenancy
            page: Page number (1-based)
            limit: Items per page
            industry: Filter by industry
            size: Filter by company size
            region: Filter by region

        Returns:
            Tuple of (agents list, total count)
        """
        configs = self.config_loader.load_all_configs()

        # Apply filters
        if industry:
            configs = [c for c in configs if c.industry.lower() == industry.lower()]
        if size:
            configs = [c for c in configs if c.size.value == size]
        if region:
            configs = [c for c in configs if c.region.lower() == region.lower()]

        total = len(configs)

        # Pagination
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_configs = configs[start_idx:end_idx]

        items = [
            AgentListItem(
                id=c.id,
                company_name=c.company_name,
                legal_type=c.legal_type,
                industry=c.industry,
                size=c.size,
                region=c.region,
                created_at=None,  # Not stored, from YAML
            )
            for c in paginated_configs
        ]

        logger.info(
            "agents_listed",
            organization_id=str(organization_id),
            total=total,
            page=page,
            limit=limit,
        )

        return items, total

    async def get_agent(
        self,
        db: AsyncSession,
        organization_id: UUID,
        agent_id: str,
    ) -> AgentDetailResponse:
        """Get detailed agent configuration.

        Args:
            db: Database session
            organization_id: Organization ID for multi-tenancy
            agent_id: Agent identifier

        Returns:
            Agent detail response

        Raises:
            HTTPException: If agent not found
        """
        try:
            config = self.config_loader.load_config(agent_id)
        except Exception as e:
            logger.warning(
                "agent_not_found",
                agent_id=agent_id,
                organization_id=str(organization_id),
                error=str(e),
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent '{agent_id}' not found",
            )

        return AgentDetailResponse(
            id=config.id,
            company_name=config.company_name,
            legal_type=config.legal_type,
            industry=config.industry,
            size=config.size,
            region=config.region,
            decision_maker=config.decision_maker.model_dump(),
            pain_points=config.pain_points,
            values=config.values,
            budget_sensitivity=config.budget_sensitivity,
            digital_maturity=config.digital_maturity,
            created_at=None,
        )

    async def get_agent_config(
        self,
        agent_id: str,
    ) -> AgentConfig:
        """Get raw agent config for simulation use.

        Args:
            agent_id: Agent identifier

        Returns:
            AgentConfig object

        Raises:
            HTTPException: If agent not found
        """
        try:
            return self.config_loader.load_config(agent_id)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent '{agent_id}' not found: {e}",
            )

    async def validate_agent_ids(
        self,
        agent_ids: List[str],
    ) -> List[str]:
        """Validate list of agent IDs and return invalid ones.

        Args:
            agent_ids: List of agent IDs to validate

        Returns:
            List of invalid agent IDs (empty if all valid)
        """
        available = set(self.config_loader.list_available_agents())
        invalid = [aid for aid in agent_ids if aid not in available]
        return invalid

    async def get_available_filters(
        self,
    ) -> dict:
        """Get available filter options from all agents.

        Returns:
            Dictionary of unique industries, sizes, and regions
        """
        configs = self.config_loader.load_all_configs()

        return {
            "industries": sorted(list(set(c.industry for c in configs))),
            "sizes": sorted(list(set(c.size.value for c in configs))),
            "regions": sorted(list(set(c.region for c in configs))),
        }
