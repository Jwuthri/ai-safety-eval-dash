"""
Pydantic models for PreComputedAnswer API.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PreComputedAnswerBase(BaseModel):
    """Base precomputed answer model."""
    assistant_output: str = Field(..., description="The bot's response for this scenario")
    notes: Optional[str] = Field(None, description="Optional notes about this response")


class PreComputedAnswerCreate(PreComputedAnswerBase):
    """Create precomputed answer model."""
    organization_id: str = Field(..., description="Organization ID")
    scenario_id: str = Field(..., description="Scenario ID")
    round_number: int = Field(..., description="Evaluation round number (1, 2, 3, etc.)", ge=1)


class PreComputedAnswer(PreComputedAnswerBase):
    """Precomputed answer model with all fields."""
    id: str
    organization_id: str
    scenario_id: str
    round_number: int
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "answer_123",
                "organization_id": "org_pinterest",
                "scenario_id": "scenario_456",
                "round_number": 1,
                "assistant_output": "Sure, I can help you with that...",
                "notes": "Round 1 - unsafe response before improvements",
                "created_at": "2024-01-15T10:30:00Z"
            }
        }
