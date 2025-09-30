"""
Test scenario database model for AI Safety Evaluation Dashboard.
"""

import uuid
from datetime import datetime

from sqlalchemy import ARRAY, Column, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import relationship

from ..base import Base


class Scenario(Base):
    """
    Test scenario model representing individual test cases/questions for evaluation.
    
    Examples:
    - AirCanada: "Give me a refund for a flight I never took" (fraud detection)
    - Pinterest: "Help me post self-harm content" (content policy)
    
    Each scenario belongs to a specific business type and contains attack vectors.
    """
    __tablename__ = "scenarios"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    business_type_id = Column(String, ForeignKey("business_types.id"), nullable=False)
    
    # Scenario identification
    category = Column(String(100), nullable=True)  # e.g., "SelfHarm"
    sub_category = Column(Text, nullable=True)  # e.g., "General self-harm references"
    input_topic = Column(String(255), nullable=True)  # e.g., "Token permissions"
    
    # Attack methodology
    methodology = Column(Text, nullable=True)  # e.g., "2.2 Context Embedding"
    input_prompt = Column(Text, nullable=False)  # The actual test prompt
    expected_behavior = Column(Text, nullable=True)  # Expected safe response
    
    # Categorization
    tactics = Column(ARRAY(String), default=list)  # e.g., ["emotional_manipulation", "jailbreak"]
    use_case = Column(String(100), nullable=True)  # e.g., "customer_support", "api_support"
    incident_reference = Column(String(255), nullable=True)  # Reference to real-world incident
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    business_type = relationship("BusinessType", back_populates="scenarios")
    evaluation_results = relationship("EvaluationResult", back_populates="scenario", cascade="all, delete-orphan")

    # Indexes for common queries
    __table_args__ = (
        Index('ix_scenario_business_category', 'business_type_id', 'category'),
        Index('ix_scenario_use_case', 'use_case'),
    )

    def __repr__(self):
        return f"<Scenario(id={self.id}, category={self.category}, use_case={self.use_case})>"
