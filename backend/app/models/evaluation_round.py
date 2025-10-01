"""
Evaluation Round models.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .enums import EvaluationRoundStatusEnum


class EvaluationRoundCreate(BaseModel):
    """Evaluation round creation model."""
    organization_id: str = Field(..., description="Organization ID being evaluated")
    round_number: int = Field(..., description="Round number", ge=1)
    description: Optional[str] = Field(None, description="Round description")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "organization_id": "org_123",
                "round_number": 1,
                "description": "Initial safety evaluation"
            }
        }
    )


class EvaluationRoundResponse(BaseModel):
    """Evaluation round response model."""
    id: str = Field(..., description="Round ID")
    organization_id: str = Field(..., description="Organization ID")
    round_number: int = Field(..., description="Round number")
    description: Optional[str] = Field(None, description="Round description")
    status: EvaluationRoundStatusEnum = Field(..., description="Round status")
    started_at: datetime = Field(..., description="Start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={datetime: lambda v: v.isoformat() if v else None},
        json_schema_extra={
            "example": {
                "id": "round_123",
                "organization_id": "org_123",
                "round_number": 1,
                "description": "Initial safety evaluation",
                "status": "running",
                "started_at": "2025-01-01T00:00:00Z",
                "completed_at": None
            }
        }
    )


class RoundSummary(BaseModel):
    """Evaluation round summary statistics."""
    round_id: str = Field(..., description="Round ID")
    total_tests: int = Field(..., description="Total test count")
    pass_count: int = Field(..., description="Passed tests")
    pass_rate: float = Field(..., description="Pass rate percentage")
    severity_breakdown: dict = Field(..., description="Count by severity")

    class Config:
        json_schema_extra = {
            "example": {
                "round_id": "round_123",
                "total_tests": 303,
                "pass_count": 236,
                "pass_rate": 77.9,
                "severity_breakdown": {
                    "PASS": 236,
                    "P4": 29,
                    "P3": 33,
                    "P2": 5,
                    "P1": 0,
                    "P0": 0
                }
            }
        }
