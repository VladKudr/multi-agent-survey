"""Pydantic schemas for Surveys and Questions."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .agent import AgentResponse


class SurveyType(str, Enum):
    """Survey types."""

    QUANTITATIVE = "quantitative"
    QUALITATIVE = "qualitative"
    MIXED = "mixed"


class QuestionType(str, Enum):
    """Question types."""

    LIKERT_SCALE = "likert_scale"
    MULTIPLE_CHOICE = "multiple_choice"
    OPEN_ENDED = "open_ended"
    RATING = "rating"


class QuestionBase(BaseModel):
    """Base question schema."""

    model_config = ConfigDict(strict=True)

    text: str = Field(..., min_length=5, description="Question text")
    type: QuestionType = Field(..., description="Question type")
    required: bool = Field(True, description="Whether question is required")
    order: int = Field(..., ge=0, description="Display order")


class QuantitativeQuestion(QuestionBase):
    """Quantitative question with scale."""

    type: Literal[QuestionType.LIKERT_SCALE, QuestionType.RATING] = Field(
        ..., description="Quantitative question type"
    )
    min_value: int = Field(1, description="Minimum scale value")
    max_value: int = Field(5, description="Maximum scale value")
    min_label: Optional[str] = Field(None, description="Label for minimum value")
    max_label: Optional[str] = Field(None, description="Label for maximum value")

    @field_validator("max_value")
    @classmethod
    def validate_scale_range(cls, v: int, info: Any) -> int:
        """Ensure max > min."""
        data = info.data
        if "min_value" in data and v <= data["min_value"]:
            raise ValueError("max_value must be greater than min_value")
        return v


class QualitativeQuestion(QuestionBase):
    """Qualitative/open-ended question."""

    type: Literal[QuestionType.OPEN_ENDED] = QuestionType.OPEN_ENDED
    min_words: int = Field(150, ge=50, description="Minimum word count")
    max_words: int = Field(400, le=1000, description="Maximum word count")

    @field_validator("max_words")
    @classmethod
    def validate_word_count_range(cls, v: int, info: Any) -> int:
        """Ensure max_words > min_words."""
        data = info.data
        if "min_words" in data and v <= data["min_words"]:
            raise ValueError("max_words must be greater than min_words")
        return v


class ChoiceQuestion(QuestionBase):
    """Multiple choice question."""

    type: Literal[QuestionType.MULTIPLE_CHOICE] = QuestionType.MULTIPLE_CHOICE
    choices: List[str] = Field(..., min_length=2, description="Available choices")
    allow_multiple: bool = Field(False, description="Allow multiple selections")

    @field_validator("choices")
    @classmethod
    def validate_unique_choices(cls, v: List[str]) -> List[str]:
        """Ensure all choices are unique and non-empty."""
        if len(set(v)) != len(v):
            raise ValueError("All choices must be unique")
        if not all(choice.strip() for choice in v):
            raise ValueError("All choices must be non-empty")
        return [choice.strip() for choice in v]


Question = QuantitativeQuestion | QualitativeQuestion | ChoiceQuestion


class SurveyCreate(BaseModel):
    """Schema for creating a survey."""

    model_config = ConfigDict(strict=True)

    title: str = Field(..., min_length=3, max_length=200, description="Survey title")
    description: Optional[str] = Field(None, max_length=1000, description="Description")
    survey_type: SurveyType = Field(..., description="Survey type")
    questions: List[Dict[str, Any]] = Field(
        ..., min_length=1, max_length=50, description="Survey questions"
    )

    @field_validator("questions")
    @classmethod
    def validate_questions(cls, v: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate each question can be parsed."""
        for i, q in enumerate(v):
            q_type = q.get("type")
            if not q_type:
                raise ValueError(f"Question {i}: type is required")
            try:
                if q_type in ["likert_scale", "rating"]:
                    QuantitativeQuestion(**q)
                elif q_type == "open_ended":
                    QualitativeQuestion(**q)
                elif q_type == "multiple_choice":
                    ChoiceQuestion(**q)
                else:
                    raise ValueError(f"Unknown question type: {q_type}")
            except Exception as e:
                raise ValueError(f"Question {i} validation failed: {e}")
        return v


class SurveyUpdate(BaseModel):
    """Schema for updating a survey."""

    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    is_active: Optional[bool] = None


class SurveyResponse(BaseModel):
    """Survey response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: Optional[str]
    survey_type: SurveyType
    questions: List[Dict[str, Any]]
    is_active: bool
    organization_id: UUID
    created_at: datetime
    updated_at: datetime


class SurveyListItem(BaseModel):
    """Survey item for list views."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    survey_type: SurveyType
    is_active: bool
    created_at: datetime


class PaginatedSurveyResponse(BaseModel):
    """Paginated response for survey lists."""

    items: List[SurveyListItem]
    total_count: int
    page: int
    limit: int
