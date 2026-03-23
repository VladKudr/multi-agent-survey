"""Pydantic schemas for Simulation Runs."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SimulationStatus(str, Enum):
    """Simulation run status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SimulationCreate(BaseModel):
    """Schema for creating a simulation run."""

    model_config = ConfigDict(strict=True)

    survey_id: UUID = Field(..., description="Survey to run")
    agent_ids: List[str] = Field(
        ..., min_length=1, description="Agents to simulate"
    )
    name: str = Field(..., min_length=3, max_length=200, description="Run name")
    description: Optional[str] = Field(None, max_length=1000)
    max_parallel_agents: int = Field(
        4, ge=1, le=10, description="Max parallel agent executions"
    )
    temperature_override: Optional[float] = Field(
        None, ge=0.0, le=2.0, description="Override LLM temperature"
    )


class SimulationResponse(BaseModel):
    """Simulation run response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: Optional[str]
    status: SimulationStatus
    survey_id: UUID
    agent_ids: List[str]
    total_agents: int
    completed_agents: int
    failed_agents: int
    results_summary: Optional[Dict[str, Any]]
    organization_id: UUID
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]


class SimulationListItem(BaseModel):
    """Simulation item for list views."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    status: SimulationStatus
    total_agents: int
    completed_agents: int
    created_at: datetime


class PaginatedSimulationResponse(BaseModel):
    """Paginated response for simulation lists."""

    items: List[SimulationListItem]
    total_count: int
    page: int
    limit: int


class SimulationResultDetail(BaseModel):
    """Detailed simulation result for a single agent/question."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    simulation_run_id: UUID
    agent_id: str
    question_id: str
    response_type: str
    response_value: Optional[float]
    reasoning: Optional[str]
    answer_text: Optional[str]
    tokens_used: int
    response_time_ms: int
    created_at: datetime


class SimulationProgressEvent(BaseModel):
    """WebSocket progress event."""

    type: str = "progress"
    simulation_id: str
    status: SimulationStatus
    completed_agents: int
    total_agents: int
    current_agent: Optional[str] = None
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SimulationResultSummary(BaseModel):
    """Summary of simulation results."""

    simulation_id: UUID
    total_responses: int
    quantitative_summary: Dict[str, Dict[str, float]]  # question_id -> stats
    qualitative_themes: Optional[List[Dict[str, Any]]]  # BERTopic themes
    agent_breakdown: Dict[str, Dict[str, Any]]
    total_tokens_used: int
    total_cost_estimate: Optional[float]
