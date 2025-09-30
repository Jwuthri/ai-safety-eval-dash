"""
Human review database model for AI Safety Evaluation Dashboard.
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum as SQLEnum, ForeignKey, Index, String, Text
from sqlalchemy.orm import relationship

from ..base import Base


class ReviewStatus(str, enum.Enum):
    """Human review status."""
    APPROVED = "approved"
    FLAGGED = "flagged"
    NEEDS_IMPROVEMENT = "needs_improvement"


class HumanReview(Base):
    """
    Human review model for human-in-the-loop evaluation oversight.
    
    Allows humans to:
    - Override judge grades
    - Flag incorrect evaluations
    - Approve results
    """
    __tablename__ = "human_reviews"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    evaluation_result_id = Column(String, ForeignKey("evaluation_results.id"), nullable=False)
    reviewer_id = Column(String, nullable=True)  # User who reviewed
    
    review_status = Column(SQLEnum(ReviewStatus), nullable=False)
    override_grade = Column(String(10), nullable=True)  # Human can override judge grades
    comments = Column(Text, nullable=True)
    
    # Timestamps
    reviewed_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    evaluation_result = relationship("EvaluationResult", back_populates="human_reviews")

    # Indexes
    __table_args__ = (
        Index('ix_human_review_result', 'evaluation_result_id'),
        Index('ix_human_review_status', 'review_status'),
    )

    def __repr__(self):
        return f"<HumanReview(id={self.id}, status={self.review_status})>"
