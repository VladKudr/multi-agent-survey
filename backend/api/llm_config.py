"""LLM Configuration API routes."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth import get_current_active_user
from config.database import get_db
from models.user import User
from schemas.llm_config import (
    AvailableProvidersResponse,
    LLMConfigCreate,
    LLMConfigResponse,
    LLMConfigUpdate,
    LLMProviderInfo,
)
from services.llm_config_service import LLMConfigService

router = APIRouter(prefix="/llm-config", tags=["LLM Configuration"])


def get_llm_config_service() -> LLMConfigService:
    """Get LLM config service instance."""
    return LLMConfigService()


@router.get(
    "/providers",
    response_model=AvailableProvidersResponse,
    description="Get available LLM providers",
)
async def get_providers(
    service: LLMConfigService = Depends(get_llm_config_service),
) -> AvailableProvidersResponse:
    """Get list of available LLM providers with their models."""
    providers = service.get_available_providers()
    return AvailableProvidersResponse(providers=providers)


@router.get(
    "/me",
    response_model=LLMConfigResponse,
    description="Get current user's LLM configuration",
)
async def get_my_config(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
    service: LLMConfigService = Depends(get_llm_config_service),
) -> LLMConfigResponse:
    """Get current user's LLM configuration (without API key)."""
    config = await service.get_config(
        db=db,
        user_id=current_user.id,
        include_api_key=False,
    )
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LLM configuration not found. Please create one first.",
        )
    
    return config


@router.post(
    "/me",
    response_model=LLMConfigResponse,
    status_code=status.HTTP_201_CREATED,
    description="Create LLM configuration for current user",
)
async def create_my_config(
    data: LLMConfigCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
    service: LLMConfigService = Depends(get_llm_config_service),
) -> LLMConfigResponse:
    """Create new LLM configuration for current user."""
    # Validate API key format
    if not service.validate_api_key(data.provider, data.api_key):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid API key format for provider: {data.provider}",
        )
    
    return await service.create_config(
        db=db,
        user_id=current_user.id,
        data=data,
    )


@router.patch(
    "/me",
    response_model=LLMConfigResponse,
    description="Update current user's LLM configuration",
)
async def update_my_config(
    data: LLMConfigUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
    service: LLMConfigService = Depends(get_llm_config_service),
) -> LLMConfigResponse:
    """Update current user's LLM configuration."""
    # Validate API key if provided
    if data.api_key and data.provider:
        if not service.validate_api_key(data.provider, data.api_key):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid API key format for provider: {data.provider}",
            )
    
    return await service.update_config(
        db=db,
        user_id=current_user.id,
        data=data,
    )


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete current user's LLM configuration",
)
async def delete_my_config(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
    service: LLMConfigService = Depends(get_llm_config_service),
) -> None:
    """Delete current user's LLM configuration."""
    await service.delete_config(
        db=db,
        user_id=current_user.id,
    )


@router.post(
    "/me/test",
    description="Test LLM configuration with a simple request",
)
async def test_my_config(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: AsyncSession = Depends(get_db),
    service: LLMConfigService = Depends(get_llm_config_service),
) -> dict:
    """Test current user's LLM configuration."""
    from llm.gateway import get_llm_gateway
    
    # Get config with API key
    config = await service.get_config(
        db=db,
        user_id=current_user.id,
        include_api_key=True,
    )
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LLM configuration not found",
        )
    
    if not config.api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API key not configured",
        )
    
    try:
        # Create gateway with user config
        gateway = get_llm_gateway(user_config=config)
        
        # Test with simple request
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'Hello from LLM test' and nothing else."},
        ]
        
        response = await gateway.generate(
            messages=messages,
            max_tokens=50,
            organization_id=str(current_user.organization_id),
        )
        
        # Update request count
        await service.increment_request_count(db, current_user.id)
        
        return {
            "success": True,
            "message": "LLM configuration is working",
            "response_preview": response.content[:100],
            "model": response.model,
            "tokens_used": response.tokens_total,
            "response_time_ms": response.response_time_ms,
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"LLM test failed: {str(e)}",
        )
