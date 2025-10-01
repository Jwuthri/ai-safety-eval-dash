"""
Human Review API models.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .enums import SeverityGrade


class HumanReviewCreate(BaseModel):
    """Create a human review for an evaluation result."""
    evaluation_result_id: str = Field(..., description="Evaluation result ID")
    reviewed_grade: SeverityGrade = Field(..., description="Human-assigned grade")
    review_notes: Optional[str] = Field(None, description="Optional review notes/reasoning")
    reviewer_id: Optional[str] = Field(None, description="Reviewer user ID")
    reviewer_name: Optional[str] = Field(None, description="Reviewer name")

    class Config:
        json_schema_extra = {
            "example": {
                "evaluation_result_id": "result_123",
                "reviewed_grade": "P2",
                "review_notes": "Confirmed P2 severity - system provided harmful advice",
                "reviewer_id": "user_123",
                "reviewer_name": "Admin User"
            }
        }


class HumanReviewResponse(BaseModel):
    """Human review response model."""
    id: str = Field(..., description="Review ID")
    evaluation_result_id: str = Field(..., description="Evaluation result ID")
    
    reviewer_id: Optional[str] = Field(None, description="Reviewer ID")
    reviewer_name: Optional[str] = Field(None, description="Reviewer name")
    
    original_grade: SeverityGrade = Field(..., description="Original AI grade")
    original_confidence: int = Field(..., description="Original confidence score")
    reviewed_grade: SeverityGrade = Field(..., description="Human-assigned grade")
    
    review_notes: Optional[str] = Field(None, description="Review notes")
    reviewed_at: datetime = Field(..., description="Review timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={datetime: lambda v: v.isoformat() if v else None}
    )


class LowConfidenceResult(BaseModel):
    """Evaluation result that needs human review (confidence < 100%)."""
    id: str = Field(..., description="Result ID")
    evaluation_round_id: str = Field(..., description="Round ID")
    scenario_id: str = Field(..., description="Scenario ID")
    
    final_grade: SeverityGrade = Field(..., description="Current AI grade")
    confidence_score: int = Field(..., description="Confidence score (33% or 66%)")
    
    # Judge grades for context
    judge_1_grade: SeverityGrade = Field(..., description="Judge 1 grade")
    judge_2_grade: SeverityGrade = Field(..., description="Judge 2 grade")
    judge_3_grade: SeverityGrade = Field(..., description="Judge 3 grade")
    
    # Has this been reviewed?
    has_human_review: bool = Field(False, description="Already reviewed by human")
    human_review: Optional[HumanReviewResponse] = Field(None, description="Human review if exists")
    
    created_at: datetime = Field(..., description="Creation timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={datetime: lambda v: v.isoformat() if v else None}
    )
