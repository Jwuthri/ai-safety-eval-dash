"""
Human Review models.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from .enums import ReviewStatusEnum, SeverityGrade


class HumanReviewCreate(BaseModel):
    """Human review creation model."""
    evaluation_result_id: str = Field(..., description="Result ID")
    reviewer_id: Optional[str] = Field(None, description="Reviewer ID")
    review_status: ReviewStatusEnum = Field(..., description="Review status")
    override_grade: Optional[SeverityGrade] = Field(None, description="Grade override")
    comments: Optional[str] = Field(None, description="Review comments")

    class Config:
        json_schema_extra = {
            "example": {
                "evaluation_result_id": "result_123",
                "reviewer_id": "user_456",
                "review_status": "needs_improvement",
                "override_grade": "P2",
                "comments": "Judge marked as PASS but response still shows compliance"
            }
        }


class HumanReviewResponse(BaseModel):
    """Human review response model."""
    id: str = Field(..., description="Review ID")
    evaluation_result_id: str = Field(..., description="Result ID")
    reviewer_id: Optional[str] = Field(None, description="Reviewer ID")
    review_status: ReviewStatusEnum = Field(..., description="Review status")
    override_grade: Optional[SeverityGrade] = Field(None, description="Grade override")
    comments: Optional[str] = Field(None, description="Comments")
    reviewed_at: datetime = Field(..., description="Review timestamp")

    class Config:
        from_attributes = True
