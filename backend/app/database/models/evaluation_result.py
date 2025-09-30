"""
Evaluation result database model for AI Safety Evaluation Dashboard.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import relationship

from ..base import Base


class EvaluationResult(Base):
    """
    Evaluation result model storing judge responses and grading.
    
    Stores:
    - System under test response
    - 3 judge evaluations (Claude, GPT-4.1, Grok)
    - Final aggregated grade (PASS, P4, P3, P2, P1, P0)
    """
    __tablename__ = "evaluation_results"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    evaluation_round_id = Column(String, ForeignKey("evaluation_rounds.id"), nullable=False)
    scenario_id = Column(String, ForeignKey("scenarios.id"), nullable=False)
    
    # System under test response
    system_response = Column(Text, nullable=False)
    final_grade = Column(String(10), nullable=True)  # PASS, P4, P3, P2, P1, P0
    
    # Judge 1 (Claude Sonnet 4.5)
    judge_1_grade = Column(String(10), nullable=True)
    judge_1_reasoning = Column(Text, nullable=True)
    judge_1_recommendation = Column(Text, nullable=True)
    judge_1_model = Column(String(100), nullable=True)
    
    # Judge 2 (GPT-5)
    judge_2_grade = Column(String(10), nullable=True)
    judge_2_reasoning = Column(Text, nullable=True)
    judge_2_recommendation = Column(Text, nullable=True)
    judge_2_model = Column(String(100), nullable=True)
    
    # Judge 3 (Grok-4 fast)
    judge_3_grade = Column(String(10), nullable=True)
    judge_3_reasoning = Column(Text, nullable=True)
    judge_3_recommendation = Column(Text, nullable=True)
    judge_3_model = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    evaluation_round = relationship("EvaluationRound", back_populates="evaluation_results")
    scenario = relationship("Scenario", back_populates="evaluation_results")
    human_reviews = relationship("HumanReview", back_populates="evaluation_result", cascade="all, delete-orphan")

    # Indexes for querying failed tests
    __table_args__ = (
        Index('ix_eval_result_round_grade', 'evaluation_round_id', 'final_grade'),
        Index('ix_eval_result_scenario', 'scenario_id'),
    )

    def __repr__(self):
        return f"<EvaluationResult(id={self.id}, grade={self.final_grade})>"
