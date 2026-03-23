"""Survey service for managing surveys."""

from typing import List
from uuid import UUID

import structlog
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.survey import Survey
from schemas.survey import (
    PaginatedSurveyResponse,
    SurveyCreate,
    SurveyListItem,
    SurveyResponse,
    SurveyUpdate,
)

logger = structlog.get_logger()


class SurveyService:
    """Service for survey CRUD operations."""

    async def create_survey(
        self,
        db: AsyncSession,
        organization_id: UUID,
        data: SurveyCreate,
    ) -> SurveyResponse:
        """Create a new survey.

        Args:
            db: Database session
            organization_id: Organization ID for multi-tenancy
            data: Survey creation data

        Returns:
            Created survey response
        """
        survey = Survey(
            organization_id=organization_id,
            title=data.title,
            description=data.description,
            survey_type=data.survey_type.value,
            questions=data.questions,
            is_active=True,
        )

        db.add(survey)
        await db.flush()

        logger.info(
            "survey_created",
            survey_id=str(survey.id),
            organization_id=str(organization_id),
            title=data.title,
        )

        return SurveyResponse.model_validate(survey)

    async def list_surveys(
        self,
        db: AsyncSession,
        organization_id: UUID,
        page: int = 1,
        limit: int = 20,
        is_active: bool | None = None,
    ) -> PaginatedSurveyResponse:
        """List surveys with pagination.

        Args:
            db: Database session
            organization_id: Organization ID
            page: Page number
            limit: Items per page
            is_active: Filter by active status

        Returns:
            Paginated survey response
        """
        query = select(Survey).where(Survey.organization_id == organization_id)

        if is_active is not None:
            query = query.where(Survey.is_active == is_active)

        # Count total
        count_query = select(Survey).where(Survey.organization_id == organization_id)
        if is_active is not None:
            count_query = count_query.where(Survey.is_active == is_active)
        total_result = await db.execute(
            select(Survey.id).where(Survey.organization_id == organization_id)
        )
        total = len(total_result.scalars().all())

        # Paginate
        query = query.offset((page - 1) * limit).limit(limit)
        result = await db.execute(query)
        surveys = result.scalars().all()

        items = [SurveyListItem.model_validate(s) for s in surveys]

        return PaginatedSurveyResponse(
            items=items,
            total_count=total,
            page=page,
            limit=limit,
        )

    async def get_survey(
        self,
        db: AsyncSession,
        organization_id: UUID,
        survey_id: UUID,
    ) -> SurveyResponse:
        """Get survey by ID.

        Args:
            db: Database session
            organization_id: Organization ID
            survey_id: Survey UUID

        Returns:
            Survey response

        Raises:
            HTTPException: If not found or unauthorized
        """
        result = await db.execute(
            select(Survey).where(
                Survey.id == survey_id,
                Survey.organization_id == organization_id,
            )
        )
        survey = result.scalar_one_or_none()

        if not survey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Survey not found",
            )

        return SurveyResponse.model_validate(survey)

    async def update_survey(
        self,
        db: AsyncSession,
        organization_id: UUID,
        survey_id: UUID,
        data: SurveyUpdate,
    ) -> SurveyResponse:
        """Update survey.

        Args:
            db: Database session
            organization_id: Organization ID
            survey_id: Survey UUID
            data: Update data

        Returns:
            Updated survey response
        """
        result = await db.execute(
            select(Survey).where(
                Survey.id == survey_id,
                Survey.organization_id == organization_id,
            )
        )
        survey = result.scalar_one_or_none()

        if not survey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Survey not found",
            )

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(survey, field, value)

        await db.flush()

        logger.info(
            "survey_updated",
            survey_id=str(survey_id),
            organization_id=str(organization_id),
        )

        return SurveyResponse.model_validate(survey)

    async def delete_survey(
        self,
        db: AsyncSession,
        organization_id: UUID,
        survey_id: UUID,
    ) -> None:
        """Delete survey.

        Args:
            db: Database session
            organization_id: Organization ID
            survey_id: Survey UUID
        """
        result = await db.execute(
            select(Survey).where(
                Survey.id == survey_id,
                Survey.organization_id == organization_id,
            )
        )
        survey = result.scalar_one_or_none()

        if not survey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Survey not found",
            )

        await db.delete(survey)

        logger.info(
            "survey_deleted",
            survey_id=str(survey_id),
            organization_id=str(organization_id),
        )
