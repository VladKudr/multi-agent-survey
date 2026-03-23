"""Survey API routes."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth import get_current_active_user
from config.database import get_db
from models.user import User
from schemas.survey import (
    PaginatedSurveyResponse,
    SurveyCreate,
    SurveyResponse,
    SurveyUpdate,
)
from services.survey_service import SurveyService

router = APIRouter(prefix="/surveys", tags=["Surveys"])


def get_survey_service() -> SurveyService:
    """Get survey service instance."""
    return SurveyService()


@router.post(
    "",
    response_model=SurveyResponse,
    status_code=status.HTTP_201_CREATED,
    description="Create a new survey",
)
async def create_survey(
    data: SurveyCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
    service: SurveyService = Depends(get_survey_service),
) -> SurveyResponse:
    """Create a new survey."""
    return await service.create_survey(
        db=db,
        organization_id=current_user.organization_id,
        data=data,
    )


@router.get(
    "",
    response_model=PaginatedSurveyResponse,
    description="List surveys",
)
async def list_surveys(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
    service: SurveyService = Depends(get_survey_service),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    is_active: bool | None = Query(None, description="Filter by active status"),
) -> PaginatedSurveyResponse:
    """List surveys with pagination."""
    return await service.list_surveys(
        db=db,
        organization_id=current_user.organization_id,
        page=page,
        limit=limit,
        is_active=is_active,
    )


@router.get(
    "/{survey_id}",
    response_model=SurveyResponse,
    description="Get survey by ID",
)
async def get_survey(
    survey_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
    service: SurveyService = Depends(get_survey_service),
) -> SurveyResponse:
    """Get survey details."""
    return await service.get_survey(
        db=db,
        organization_id=current_user.organization_id,
        survey_id=survey_id,
    )


@router.patch(
    "/{survey_id}",
    response_model=SurveyResponse,
    description="Update survey",
)
async def update_survey(
    survey_id: UUID,
    data: SurveyUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
    service: SurveyService = Depends(get_survey_service),
) -> SurveyResponse:
    """Update survey."""
    return await service.update_survey(
        db=db,
        organization_id=current_user.organization_id,
        survey_id=survey_id,
        data=data,
    )


@router.delete(
    "/{survey_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete survey",
)
async def delete_survey(
    survey_id: UUID,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
    service: SurveyService = Depends(get_survey_service),
) -> None:
    """Delete survey."""
    await service.delete_survey(
        db=db,
        organization_id=current_user.organization_id,
        survey_id=survey_id,
    )
