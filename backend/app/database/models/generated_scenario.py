"""
Generated Scenario database model for AI Safety Evaluation Dashboard.
Auto-generated test scenarios specific to an organization.
"""

import uuid
from datetime import datetime

from sqlalchemy import ARRAY, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from ..base import Base


class GeneratedScenario(Base):
    """
    Generated test scenario model for AI-generated test cases.
    
    These scenarios are auto-generated when creating a new organization
    based on their business type and description. They are NOT shared
    across organizations like the main scenarios table.
    
    Examples:
    - "Try to get a refund without proof of purchase" (fraud)
    - "Request access to another user's API keys" (unauthorized access)
    """
    __tablename__ = "generated_scenarios"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    business_type_id = Column(String, ForeignKey("business_types.id"), nullable=False)
    
    # Scenario identification
    category = Column(String(100), nullable=True)  # e.g., "Fraud", "Unauthorized Access"
    sub_category = Column(Text, nullable=True)
    input_topic = Column(String(255), nullable=True)
    
    # Attack methodology
    methodology = Column(Text, nullable=True)
    input_prompt = Column(Text, nullable=False)  # The actual test prompt
    expected_behavior = Column(Text, nullable=True)  # Expected safe response
    
    # Categorization
    tactics = Column(ARRAY(String), default=list)
    use_case = Column(String(100), nullable=True)
    incident_reference = Column(String(255), nullable=True)
    
    # Generation metadata
    generation_prompt = Column(Text, nullable=True)  # The prompt used to generate this
    model_used = Column(String(100), nullable=True)  # Which LLM model generated this
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    organization = relationship("Organization", backref="generated_scenarios")
    business_type = relationship("BusinessType", backref="generated_scenarios")

    def __repr__(self):
        return f"<GeneratedScenario(id={self.id}, org_id={self.organization_id}, category={self.category})>"

