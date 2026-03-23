"""User and Organization models."""

from sqlalchemy import Boolean, Column, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, OrganizationMixin, TimestampMixin, UUIDMixin


class Organization(Base, UUIDMixin, TimestampMixin):
    """Organization model for multi-tenancy."""

    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text)

    # Relationships
    users: Mapped[list["User"]] = relationship(
        "User", back_populates="organization", lazy="selectin"
    )
    surveys: Mapped[list["Survey"]] = relationship(
        "Survey", back_populates="organization", lazy="selectin"
    )
    simulation_runs: Mapped[list["SimulationRun"]] = relationship(
        "SimulationRun", back_populates="organization", lazy="selectin"
    )


class User(Base, UUIDMixin, TimestampMixin, OrganizationMixin):
    """User model with RBAC."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="viewer", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="users", lazy="selectin"
    )
    llm_config: Mapped["UserLLMConfig"] = relationship(
        "UserLLMConfig", back_populates="user", lazy="selectin", uselist=False
    )


class UserLLMConfig(Base, UUIDMixin, TimestampMixin):
    """User-specific LLM configuration."""

    __tablename__ = "user_llm_configs"

    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False
    )
    
    # Provider settings
    provider: Mapped[str] = mapped_column(String(50), default="kimi", nullable=False)
    api_key: Mapped[str | None] = mapped_column(Text)  # Encrypted API key
    base_url: Mapped[str | None] = mapped_column(String(500))
    
    # Model settings
    model: Mapped[str] = mapped_column(String(100), default="kimi-k2-07132k-preview", nullable=False)
    temperature: Mapped[float] = mapped_column(default=0.7, nullable=False)
    max_tokens: Mapped[int] = mapped_column(default=2000, nullable=False)
    
    # Additional provider-specific settings (JSONB for flexibility)
    extra_settings: Mapped[dict | None] = mapped_column(JSONB)
    
    # Usage tracking
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_used_at: Mapped[str | None] = mapped_column(String(50))
    total_requests: Mapped[int] = mapped_column(default=0, nullable=False)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="llm_config")
