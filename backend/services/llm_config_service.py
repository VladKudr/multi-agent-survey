"""Service for managing user LLM configurations."""

from typing import Optional
from uuid import UUID

import structlog
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User, UserLLMConfig
from schemas.llm_config import (
    AVAILABLE_PROVIDERS,
    LLMConfigCreate,
    LLMConfigResponse,
    LLMConfigUpdate,
    LLMConfigWithKey,
    LLMProviderInfo,
)

logger = structlog.get_logger()


class LLMConfigService:
    """Service for user LLM configuration operations."""

    async def create_config(
        self,
        db: AsyncSession,
        user_id: UUID,
        data: LLMConfigCreate,
    ) -> LLMConfigResponse:
        """Create LLM config for user.
        
        Args:
            db: Database session
            user_id: User ID
            data: LLM configuration data
            
        Returns:
            Created LLM config
        """
        # Check if user already has config
        result = await db.execute(
            select(UserLLMConfig).where(UserLLMConfig.user_id == user_id)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already has LLM configuration. Use update instead.",
            )
        
        # Determine base_url if not provided
        base_url = data.base_url
        if not base_url and data.provider == "kimi":
            base_url = "https://api.moonshot.cn/v1"
        elif not base_url and data.provider == "ollama":
            base_url = "http://localhost:11434"
        
        config = UserLLMConfig(
            user_id=user_id,
            provider=data.provider,
            model=data.model,
            api_key=data.api_key,  # Note: In production, encrypt this
            base_url=base_url,
            temperature=data.temperature,
            max_tokens=data.max_tokens,
            extra_settings=data.extra_settings or {},
            is_active=True,
            total_requests=0,
        )
        
        db.add(config)
        await db.flush()
        
        logger.info(
            "llm_config_created",
            user_id=str(user_id),
            provider=data.provider,
            model=data.model,
        )
        
        return LLMConfigResponse.model_validate(config)

    async def get_config(
        self,
        db: AsyncSession,
        user_id: UUID,
        include_api_key: bool = False,
    ) -> Optional[LLMConfigWithKey | LLMConfigResponse]:
        """Get user's LLM config.
        
        Args:
            db: Database session
            user_id: User ID
            include_api_key: Whether to include API key in response
            
        Returns:
            LLM config or None
        """
        result = await db.execute(
            select(UserLLMConfig).where(UserLLMConfig.user_id == user_id)
        )
        config = result.scalar_one_or_none()
        
        if not config:
            return None
        
        if include_api_key:
            return LLMConfigWithKey.model_validate(config)
        return LLMConfigResponse.model_validate(config)

    async def update_config(
        self,
        db: AsyncSession,
        user_id: UUID,
        data: LLMConfigUpdate,
    ) -> LLMConfigResponse:
        """Update user's LLM config.
        
        Args:
            db: Database session
            user_id: User ID
            data: Update data
            
        Returns:
            Updated config
        """
        result = await db.execute(
            select(UserLLMConfig).where(UserLLMConfig.user_id == user_id)
        )
        config = result.scalar_one_or_none()
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="LLM configuration not found",
            )
        
        update_data = data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            if value is not None:
                setattr(config, field, value)
        
        await db.flush()
        
        logger.info(
            "llm_config_updated",
            user_id=str(user_id),
            provider=config.provider,
        )
        
        return LLMConfigResponse.model_validate(config)

    async def delete_config(
        self,
        db: AsyncSession,
        user_id: UUID,
    ) -> None:
        """Delete user's LLM config.
        
        Args:
            db: Database session
            user_id: User ID
        """
        result = await db.execute(
            select(UserLLMConfig).where(UserLLMConfig.user_id == user_id)
        )
        config = result.scalar_one_or_none()
        
        if config:
            await db.delete(config)
            logger.info("llm_config_deleted", user_id=str(user_id))

    async def get_or_create_default(
        self,
        db: AsyncSession,
        user_id: UUID,
    ) -> LLMConfigWithKey:
        """Get existing config or create default one.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            LLM config with API key
        """
        result = await db.execute(
            select(UserLLMConfig).where(UserLLMConfig.user_id == user_id)
        )
        config = result.scalar_one_or_none()
        
        if config:
            return LLMConfigWithKey.model_validate(config)
        
        # Create default config (Kimi)
        config = UserLLMConfig(
            user_id=user_id,
            provider="kimi",
            model="kimi-k2-07132k-preview",
            api_key="",  # Empty initially
            base_url="https://api.moonshot.cn/v1",
            temperature=0.7,
            max_tokens=2000,
            is_active=True,
            total_requests=0,
        )
        
        db.add(config)
        await db.flush()
        
        logger.info("default_llm_config_created", user_id=str(user_id))
        
        return LLMConfigWithKey.model_validate(config)

    async def increment_request_count(
        self,
        db: AsyncSession,
        user_id: UUID,
    ) -> None:
        """Increment request count for user's config.
        
        Args:
            db: Database session
            user_id: User ID
        """
        from datetime import datetime
        
        result = await db.execute(
            select(UserLLMConfig).where(UserLLMConfig.user_id == user_id)
        )
        config = result.scalar_one_or_none()
        
        if config:
            config.total_requests += 1
            config.last_used_at = datetime.utcnow().isoformat()
            await db.flush()

    def get_available_providers(self) -> list[LLMProviderInfo]:
        """Get list of available LLM providers.
        
        Returns:
            List of provider information
        """
        return AVAILABLE_PROVIDERS

    def validate_api_key(self, provider: str, api_key: str) -> bool:
        """Validate API key format for provider.
        
        Args:
            provider: Provider ID
            api_key: API key to validate
            
        Returns:
            True if valid format
        """
        if not api_key or len(api_key.strip()) < 10:
            return False
        
        # Provider-specific validations
        if provider == "kimi":
            # Kimi keys typically start with specific prefix
            return api_key.startswith("sk-") or len(api_key) > 20
        elif provider == "openai":
            return api_key.startswith("sk-")
        elif provider == "anthropic":
            return api_key.startswith("sk-ant-")
        
        return True
