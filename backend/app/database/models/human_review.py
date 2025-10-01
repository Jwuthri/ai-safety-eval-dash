"""
Human review database model for AI Safety Evaluation Dashboard.

Tracks human annotations of evaluation results when confidence is low.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship

from ..base import Base


class HumanReview(Base):
    """
    Human review model for low-confidence evaluation results.
    
    When judges disagree (confidence < 100%), humans can review and
    provide the definitive grade.
    """
    __tablename__ = "human_reviews"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    evaluation_result_id = Column(String, ForeignKey("evaluation_results.id"), nullable=False)
    
    # Review metadata
    reviewer_id = Column(String, nullable=True)  # User/admin who reviewed
    reviewer_name = Column(String, nullable=True)
    
    # Grades
    original_grade = Column(String(10), nullable=False)  # Original AI-determined grade
    original_confidence = Column(Integer, nullable=False)  # Original confidence score
    reviewed_grade = Column(String(10), nullable=False)  # Human-assigned grade
    
    # Reasoning
    review_notes = Column(Text, nullable=True)  # Optional explanation
    
    # Timestamps
    reviewed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    evaluation_result = relationship("EvaluationResult", back_populates="human_reviews")

    # Indexes
    __table_args__ = (
        Index('ix_human_review_result', 'evaluation_result_id'),
        Index('ix_human_review_reviewer', 'reviewer_id'),
        Index('ix_human_review_date', 'reviewed_at'),
    )

    def __repr__(self):
        return f"<HumanReview(id={self.id}, {self.original_grade} → {self.reviewed_grade})>"
