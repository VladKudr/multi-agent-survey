"""LLM Gateway abstraction with user-specific configurations."""

import os
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, AsyncGenerator, Optional

import litellm
import structlog
from litellm import acompletion

from config.settings import Settings, get_settings
from schemas.llm_config import LLMConfigWithKey

logger = structlog.get_logger()


class LLMProvider(str, Enum):
    """Supported LLM providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    YANDEXGPT = "yandexgpt"
    OLLAMA = "ollama"
    KIMI = "kimi"
    CUSTOM = "custom"


@dataclass
class LLMResponse:
    """Standardized LLM response."""

    content: str
    model: str
    provider: str
    tokens_input: int
    tokens_output: int
    tokens_total: int
    cost_usd: float | None
    response_time_ms: int
    raw_response: Any | None = None


class LLMGateway:
    """Gateway for LLM API calls with user-specific configurations."""

    # Provider-specific base URLs
    PROVIDER_URLS = {
        "kimi": "https://api.moonshot.cn/v1",
        "openai": "https://api.openai.com/v1",
        "anthropic": None,  # Uses litellm default
        "ollama": "http://localhost:11434",
        "custom": None,  # Must be provided by user
    }

    def __init__(self, user_config: Optional[LLMConfigWithKey] = None):
        """Initialize gateway with optional user config.
        
        Args:
            user_config: User-specific LLM configuration. If None, uses system defaults.
        """
        self.user_config = user_config
        self._rate_limit_counter: dict[str, list[float]] = {}

    def _get_api_key(self) -> Optional[str]:
        """Get API key from user config or environment."""
        if self.user_config and self.user_config.api_key:
            return self.user_config.api_key
        
        # Fallback to environment variables
        settings = get_settings()
        return (
            settings.OPENAI_API_KEY 
            or settings.ANTHROPIC_API_KEY 
            or settings.YANDEXGPT_API_KEY
        )

    def _get_base_url(self) -> Optional[str]:
        """Get base URL for the provider."""
        if self.user_config:
            # Use custom base_url if provided
            if self.user_config.base_url:
                return self.user_config.base_url
            
            # Use provider-specific default
            provider = self.user_config.provider
            return self.PROVIDER_URLS.get(provider)
        
        return None

    def _get_model_name(self) -> str:
        """Get model name for the request."""
        if self.user_config:
            # For kimi, use the model as-is
            if self.user_config.provider == "kimi":
                return self.user_config.model
            return self.user_config.model
        
        return "gpt-4"

    def _get_temperature(self) -> float:
        """Get temperature setting."""
        if self.user_config:
            return self.user_config.temperature
        return 0.7

    def _get_max_tokens(self) -> int:
        """Get max tokens setting."""
        if self.user_config:
            return self.user_config.max_tokens
        return 2000

    def _setup_litellm(self):
        """Configure litellm with user settings."""
        api_key = self._get_api_key()
        base_url = self._get_base_url()
        
        if api_key:
            litellm.api_key = api_key
        
        if base_url:
            litellm.api_base = base_url
            
        # Enable cost tracking
        litellm.set_verbose = False

    def _check_rate_limit(self, organization_id: str) -> bool:
        """Check if request is within rate limit."""
        import time

        now = time.time()
        window_start = now - 60  # 1 minute window

        # Clean old entries and count recent ones
        recent_requests = [
            ts
            for ts in self._rate_limit_counter.get(organization_id, [])
            if ts > window_start
        ]
        self._rate_limit_counter[organization_id] = recent_requests

        # Use user's rate limit or default
        limit = 60  # Default rate limit per minute
        if self.user_config and self.user_config.extra_settings:
            limit = self.user_config.extra_settings.get("rate_limit_per_minute", 60)
        
        return len(recent_requests) < limit

    def _record_request(self, organization_id: str) -> None:
        """Record a request for rate limiting."""
        import time

        if organization_id not in self._rate_limit_counter:
            self._rate_limit_counter[organization_id] = []
        self._rate_limit_counter[organization_id].append(time.time())

    async def generate(
        self,
        messages: list[dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        organization_id: str | None = None,
        response_format: dict[str, Any] | None = None,
    ) -> LLMResponse:
        """Generate completion with user configuration.

        Args:
            messages: List of message dicts with role and content
            model: Override model name (optional)
            temperature: Override temperature (optional)
            max_tokens: Override max tokens (optional)
            organization_id: For rate limiting
            response_format: JSON schema for response

        Returns:
            Standardized LLM response
        """
        import time

        org_id = organization_id or "default"

        # Check rate limit
        if not self._check_rate_limit(org_id):
            raise RateLimitError(f"Rate limit exceeded for organization {org_id}")

        start_time = time.time()
        self._record_request(org_id)

        # Setup litellm with user config
        self._setup_litellm()

        # Get effective settings
        effective_model = model or self._get_model_name()
        effective_temp = temperature or self._get_temperature()
        effective_max_tokens = max_tokens or self._get_max_tokens()

        # Handle kimi provider
        if self.user_config and self.user_config.provider == "kimi":
            # Kimi uses openai-compatible API
            effective_model = f"openai/{effective_model}"

        try:
            kwargs = {
                "model": effective_model,
                "messages": messages,
                "temperature": effective_temp,
                "max_tokens": effective_max_tokens,
            }
            if response_format:
                kwargs["response_format"] = response_format

            response = await acompletion(**kwargs)

            elapsed_ms = int((time.time() - start_time) * 1000)

            # Extract usage info
            usage = response.get("usage", {})
            tokens_input = usage.get("prompt_tokens", 0)
            tokens_output = usage.get("completion_tokens", 0)
            tokens_total = usage.get("total_tokens", tokens_input + tokens_output)

            # Calculate cost
            try:
                cost = litellm.completion_cost(response)
            except Exception:
                cost = None

            result = LLMResponse(
                content=response.choices[0].message.content,
                model=response.model,
                provider=self.user_config.provider if self.user_config else "unknown",
                tokens_input=tokens_input,
                tokens_output=tokens_output,
                tokens_total=tokens_total,
                cost_usd=cost,
                response_time_ms=elapsed_ms,
                raw_response=response,
            )

            # Log for billing (never log prompt content)
            logger.info(
                "llm_api_call",
                organization_id=org_id,
                provider=self.user_config.provider if self.user_config else "default",
                model=effective_model,
                tokens_input=tokens_input,
                tokens_output=tokens_output,
                cost_usd=cost,
                response_time_ms=elapsed_ms,
            )

            return result

        except Exception as e:
            logger.error(
                "llm_api_error",
                organization_id=org_id,
                model=effective_model,
                error=str(e),
                error_type=type(e).__name__,
            )
            raise LLMError(f"LLM API error: {e}") from e

    async def generate_stream(
        self,
        messages: list[dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> AsyncGenerator[str, None]:
        """Generate streaming completion."""
        try:
            self._setup_litellm()
            
            effective_model = model or self._get_model_name()
            if self.user_config and self.user_config.provider == "kimi":
                effective_model = f"openai/{effective_model}"

            response = await acompletion(
                model=effective_model,
                messages=messages,
                temperature=temperature or self._get_temperature(),
                max_tokens=max_tokens or self._get_max_tokens(),
                stream=True,
            )

            async for chunk in response:
                content = chunk.choices[0].delta.content
                if content:
                    yield content

        except Exception as e:
            raise LLMError(f"LLM streaming error: {e}") from e


class LLMError(Exception):
    """Base LLM error."""

    pass


class RateLimitError(LLMError):
    """Rate limit exceeded error."""

    pass


def get_llm_gateway(user_config: Optional[LLMConfigWithKey] = None) -> LLMGateway:
    """Get LLM gateway instance with optional user config.
    
    Args:
        user_config: User-specific LLM configuration
        
    Returns:
        Configured LLMGateway instance
    """
    return LLMGateway(user_config=user_config)
