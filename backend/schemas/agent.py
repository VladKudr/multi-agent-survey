"""Pydantic schemas for Agent configurations and responses."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class LegalType(str, Enum):
    """Legal entity types."""

    IP = "ИП"
    OOO = "ООО"


class CompanySize(str, Enum):
    """Company size categories."""

    MICRO = "micro"
    SMB = "SMB"
    MID = "mid"
    ENTERPRISE = "enterprise"


class RiskAppetite(str, Enum):
    """Risk appetite levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class CommunicationStyle(str, Enum):
    """Communication style preferences."""

    FORMAL = "formal"
    INFORMAL = "informal"
    MIXED = "mixed"


class BudgetSensitivity(str, Enum):
    """Budget sensitivity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DecisionMaker(BaseModel):
    """Decision maker persona details."""

    model_config = ConfigDict(strict=True)

    role: str = Field(..., description="Job role/title")
    age: int = Field(..., ge=18, le=80, description="Age in years")
    gender: Literal["male", "female"] = Field(..., description="Gender")
    education: str = Field(..., description="Education level")
    mbti: str = Field(..., pattern=r"^[EI][NS][FT][JP]$", description="MBTI type")
    risk_appetite: RiskAppetite = Field(..., description="Risk appetite level")
    communication_style: CommunicationStyle = Field(
        ..., description="Preferred communication style"
    )


class AgentConfig(BaseModel):
    """Complete agent configuration from YAML."""

    model_config = ConfigDict(strict=True)

    id: str = Field(..., description="Unique agent identifier")
    legal_type: LegalType = Field(..., description="Legal entity type")
    company_name: str = Field(..., min_length=1, description="Company name")
    industry: str = Field(..., min_length=1, description="Industry sector")
    size: CompanySize = Field(..., description="Company size category")
    region: str = Field(..., description="Geographic region")
    annual_revenue: str = Field(..., description="Annual revenue range")
    decision_maker: DecisionMaker = Field(..., description="Decision maker persona")
    pain_points: List[str] = Field(
        default_factory=list, min_length=1, description="Business pain points"
    )
    values: List[str] = Field(
        default_factory=list, min_length=1, description="Company values"
    )
    budget_sensitivity: BudgetSensitivity = Field(
        ..., description="Budget sensitivity level"
    )
    digital_maturity: int = Field(
        ..., ge=1, le=5, description="Digital maturity score (1-5)"
    )

    @field_validator("pain_points", "values")
    @classmethod
    def validate_non_empty_strings(cls, v: List[str]) -> List[str]:
        """Ensure all items are non-empty strings."""
        if not all(isinstance(item, str) and item.strip() for item in v):
            raise ValueError("All items must be non-empty strings")
        return [item.strip() for item in v]


class AgentConfigFile(BaseModel):
    """Wrapper for YAML agent config file."""

    agent: AgentConfig


class AgentResponse(BaseModel):
    """Structured agent response to survey questions."""

    model_config = ConfigDict(strict=True)

    agent_id: str = Field(..., description="Agent identifier")
    response_type: Literal["quantitative", "qualitative"] = Field(
        ..., description="Type of response"
    )
    response_value: Optional[float] = Field(
        None, description="Numeric value for quantitative responses"
    )
    reasoning: Optional[str] = Field(
        None, description="Chain-of-thought reasoning"
    )
    answer_text: Optional[str] = Field(
        None, description="Free text for qualitative responses"
    )
    tokens_used: int = Field(0, description="LLM tokens consumed")
    response_time_ms: int = Field(0, description="Response time in milliseconds")

    @field_validator("response_value")
    @classmethod
    def validate_quantitative_has_value(
        cls, v: Optional[float], info: Any
    ) -> Optional[float]:
        """Ensure quantitative responses have a value."""
        data = info.data
        if data.get("response_type") == "quantitative" and v is None:
            raise ValueError("Quantitative responses must have a response_value")
        return v

    @field_validator("answer_text")
    @classmethod
    def validate_qualitative_has_text(
        cls, v: Optional[str], info: Any
    ) -> Optional[str]:
        """Ensure qualitative responses have answer text."""
        data = info.data
        if data.get("response_type") == "qualitative" and not v:
            raise ValueError("Qualitative responses must have answer_text")
        return v


class AgentListItem(BaseModel):
    """Agent item for list views."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    company_name: str
    legal_type: LegalType
    industry: str
    size: CompanySize
    region: str
    created_at: datetime


class AgentDetailResponse(AgentListItem):
    """Detailed agent response."""

    decision_maker: Dict[str, Any]
    pain_points: List[str]
    values: List[str]
    budget_sensitivity: BudgetSensitivity
    digital_maturity: int


class PaginatedAgentResponse(BaseModel):
    """Paginated response for agent lists."""

    items: List[AgentListItem]
    total_count: int
    page: int
    limit: int
