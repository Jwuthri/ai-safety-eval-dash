"""
Evaluation round database model for AI Safety Evaluation Dashboard.
"""

import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum as SQLEnum, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship

from ..base import Base


class EvaluationRoundStatus(str, enum.Enum):
    """Evaluation round status."""
    RUNNING = "running"
    COMPLETED = "completed"
    UNDER_REVIEW = "under_review"
    FAILED = "failed"


class EvaluationRound(Base):
    """
    Evaluation round model for tracking multi-round testing iterations.
    
    Tracks improvement over time for a specific organization:
    - Round 1: 77.9% pass rate
    - Round 2: 94.1% pass rate
    - Round 3: 97.4% pass rate → Certified!
    """
    __tablename__ = "evaluation_rounds"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    
    round_number = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(EvaluationRoundStatus), default=EvaluationRoundStatus.RUNNING)
    
    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="evaluation_rounds")
    evaluation_results = relationship("EvaluationResult", back_populates="evaluation_round", cascade="all, delete-orphan")
    certifications = relationship("AiucCertification", back_populates="evaluation_round", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('ix_eval_round_org_number', 'organization_id', 'round_number'),
        Index('ix_eval_round_status', 'status'),
    )

    def __repr__(self):
        return f"<EvaluationRound(id={self.id}, round={self.round_number}, status={self.status})>"
