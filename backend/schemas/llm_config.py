"""Pydantic schemas for User LLM Configuration."""

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class LLMProvider(str):
    """Supported LLM providers."""

    KIMI = "kimi"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    YANDEXGPT = "yandexgpt"
    OLLAMA = "ollama"
    CUSTOM = "custom"


class LLMConfigBase(BaseModel):
    """Base LLM config schema."""

    model_config = ConfigDict(strict=True)

    provider: str = Field(
        default="kimi",
        description="LLM provider (kimi, openai, anthropic, etc.)"
    )
    model: str = Field(
        default="kimi-k2-07132k-preview",
        description="Model name"
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Sampling temperature"
    )
    max_tokens: int = Field(
        default=2000,
        ge=100,
        le=8000,
        description="Maximum tokens per request"
    )
    base_url: Optional[str] = Field(
        None,
        description="Custom API base URL (for custom providers)"
    )
    extra_settings: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Provider-specific extra settings"
    )

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, v: str) -> str:
        """Validate provider name."""
        allowed = {"kimi", "openai", "anthropic", "yandexgpt", "ollama", "custom"}
        if v not in allowed:
            raise ValueError(f"Provider must be one of: {allowed}")
        return v


class LLMConfigCreate(LLMConfigBase):
    """Schema for creating LLM config."""

    api_key: str = Field(
        ...,
        min_length=10,
        description="API key for the LLM provider"
    )

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Basic API key validation."""
        if not v or len(v.strip()) < 10:
            raise ValueError("API key must be at least 10 characters")
        return v.strip()


class LLMConfigUpdate(BaseModel):
    """Schema for updating LLM config."""

    provider: Optional[str] = None
    model: Optional[str] = None
    api_key: Optional[str] = None
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, ge=100, le=8000)
    base_url: Optional[str] = None
    extra_settings: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class LLMConfigResponse(LLMConfigBase):
    """LLM config response (without API key)."""

    model_config = ConfigDict(from_attributes=True, extra="ignore")

    id: UUID
    user_id: UUID
    is_active: bool
    total_requests: int
    last_used_at: Optional[str] = Field(default=None)
    created_at: datetime
    updated_at: datetime


class LLMConfigWithKey(LLMConfigResponse):
    """LLM config with API key (internal use only)."""

    api_key: Optional[str] = None


class LLMProviderInfo(BaseModel):
    """Information about an LLM provider."""

    id: str
    name: str
    description: str
    models: list[str]
    default_model: str
    requires_base_url: bool
    docs_url: str


class AvailableProvidersResponse(BaseModel):
    """Response with available providers."""

    providers: list[LLMProviderInfo]


# Predefined provider configurations
AVAILABLE_PROVIDERS: list[LLMProviderInfo] = [
    LLMProviderInfo(
        id="kimi",
        name="Kimi (Moonshot AI)",
        description="Kimi API от Moonshot AI. Поддерживает длинный контекст до 2M токенов.",
        models=[
            "kimi-k2-07132k-preview",
            "kimi-latest",
            "kimi-k1.5",
            "moonshot-v1-8k",
            "moonshot-v1-32k",
            "moonshot-v1-128k",
        ],
        default_model="kimi-k2-07132k-preview",
        requires_base_url=False,
        docs_url="https://platform.moonshot.cn/docs",
    ),
    LLMProviderInfo(
        id="openai",
        name="OpenAI",
        description="OpenAI GPT модели",
        models=[
            "gpt-4",
            "gpt-4-turbo",
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-3.5-turbo",
        ],
        default_model="gpt-4o",
        requires_base_url=False,
        docs_url="https://platform.openai.com/docs",
    ),
    LLMProviderInfo(
        id="anthropic",
        name="Anthropic Claude",
        description="Anthropic Claude модели",
        models=[
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
        ],
        default_model="claude-3-sonnet-20240229",
        requires_base_url=False,
        docs_url="https://docs.anthropic.com",
    ),
    LLMProviderInfo(
        id="ollama",
        name="Ollama (Local)",
        description="Локальные модели через Ollama",
        models=[
            "llama2",
            "llama3",
            "mistral",
            "codellama",
        ],
        default_model="llama3",
        requires_base_url=True,
        docs_url="https://ollama.ai",
    ),
    LLMProviderInfo(
        id="custom",
        name="Custom (OpenAI-compatible)",
        description="Другие провайдеры с OpenAI-compatible API",
        models=["custom"],
        default_model="custom",
        requires_base_url=True,
        docs_url="",
    ),
]
