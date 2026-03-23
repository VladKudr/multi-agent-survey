"""Pydantic schemas for Users and Authentication."""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

if TYPE_CHECKING:
    from .llm_config import LLMConfigResponse


class UserRole(str, Enum):
    """User roles for RBAC."""

    ADMIN = "admin"
    RESEARCHER = "researcher"
    VIEWER = "viewer"


class UserBase(BaseModel):
    """Base user schema."""

    model_config = ConfigDict(strict=True)

    email: EmailStr = Field(..., description="User email")
    full_name: str = Field(..., min_length=2, max_length=100, description="Full name")
    role: UserRole = Field(default=UserRole.VIEWER, description="User role")
    is_active: bool = Field(True, description="Account active status")


class UserCreate(UserBase):
    """Schema for creating a user."""

    password: str = Field(
        ..., min_length=8, max_length=100, description="User password"
    )
    organization_id: UUID = Field(..., description="Organization ID")

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Ensure password has required complexity."""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """User response schema."""

    model_config = ConfigDict(from_attributes=True, extra="ignore")

    id: UUID
    organization_id: UUID
    llm_config: Optional["LLMConfigResponse"] = None
    created_at: datetime
    updated_at: datetime


class UserLogin(BaseModel):
    """User login schema."""

    model_config = ConfigDict(strict=True)

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Access token TTL in seconds")


class TokenRefresh(BaseModel):
    """Token refresh schema."""

    refresh_token: str


class TokenPayload(BaseModel):
    """JWT token payload."""

    sub: UUID = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    role: UserRole = Field(..., description="User role")
    org_id: UUID = Field(..., description="Organization ID")
    exp: datetime = Field(..., description="Expiration time")
    type: str = Field(default="access", description="Token type")


class OrganizationBase(BaseModel):
    """Base organization schema."""

    model_config = ConfigDict(strict=True)

    name: str = Field(..., min_length=2, max_length=200, description="Org name")
    slug: str = Field(..., min_length=2, max_length=50, description="URL slug")

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        """Ensure slug is URL-safe."""
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError("Slug must be alphanumeric with hyphens/underscores only")
        return v.lower()


class OrganizationCreate(OrganizationBase):
    """Schema for creating an organization."""

    pass


class OrganizationResponse(OrganizationBase):
    """Organization response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime


class PaginatedUserResponse(BaseModel):
    """Paginated response for user lists."""

    items: list
    total_count: int
    page: int
    limit: int


class PasswordChange(BaseModel):
    """Password change schema."""

    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Ensure password has required complexity."""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


# Rebuild models with forward references
UserResponse.model_rebuild()
