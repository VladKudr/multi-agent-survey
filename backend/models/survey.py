"""Survey and Question models."""

from typing import Any

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, OrganizationMixin, TimestampMixin, UUIDMixin


class Survey(Base, UUIDMixin, TimestampMixin, OrganizationMixin):
    """Survey model."""

    __tablename__ = "surveys"

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    survey_type: Mapped[str] = mapped_column(String(20), nullable=False)
    questions: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="surveys", lazy="selectin"
    )
    simulation_runs: Mapped[list["SimulationRun"]] = relationship(
        "SimulationRun", back_populates="survey", lazy="selectin"
    )
