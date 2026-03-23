"""SimulationRun and SimulationResult models."""

from datetime import datetime
from typing import Any

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, OrganizationMixin, TimestampMixin, UUIDMixin


class SimulationRun(Base, UUIDMixin, TimestampMixin, OrganizationMixin):
    """Simulation run model."""

    __tablename__ = "simulation_runs"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        String(20), default="pending", nullable=False, index=True
    )
    survey_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("surveys.id"), nullable=False
    )
    agent_ids: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    total_agents: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completed_agents: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed_agents: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    results_summary: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    celery_task_id: Mapped[str | None] = mapped_column(String(100))
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="simulation_runs", lazy="selectin"
    )
    survey: Mapped["Survey"] = relationship(
        "Survey", back_populates="simulation_runs", lazy="selectin"
    )
    results: Mapped[list["SimulationResult"]] = relationship(
        "SimulationResult",
        back_populates="simulation_run",
        lazy="selectin",
        cascade="all, delete-orphan",
    )


class SimulationResult(Base, UUIDMixin, TimestampMixin):
    """Individual agent response in a simulation."""

    __tablename__ = "simulation_results"

    simulation_run_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("simulation_runs.id"), nullable=False, index=True
    )
    agent_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    question_id: Mapped[str] = mapped_column(String(100), nullable=False)
    response_type: Mapped[str] = mapped_column(String(20), nullable=False)
    response_value: Mapped[float | None] = mapped_column()
    reasoning: Mapped[str | None] = mapped_column(Text)
    answer_text: Mapped[str | None] = mapped_column(Text)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    response_time_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    raw_llm_response: Mapped[dict[str, Any] | None] = mapped_column(JSONB)

    # Relationships
    simulation_run: Mapped["SimulationRun"] = relationship(
        "SimulationRun", back_populates="results", lazy="selectin"
    )
