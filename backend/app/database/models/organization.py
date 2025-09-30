"""
Organization database model for AI Safety Evaluation Dashboard.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from ..base import Base


class Organization(Base):
    """
    Organization model representing companies using the platform.
    
    Each org picks ONE business type (e.g., AirCanada → Airlines Customer Support)
    
    Examples:
    - "AirCanada Corp" → business_type: "Airlines Customer Support"
    - "Pinterest Inc" → business_type: "API Developer Support"
    - "Shopify" → business_type: "E-commerce Support"
    """
    __tablename__ = "organizations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    business_type_id = Column(String, ForeignKey("business_types.id"), nullable=False)
    
    name = Column(String(255), nullable=False, unique=True, index=True)
    slug = Column(String(100), nullable=False, unique=True, index=True)  # e.g., "aircanada"
    
    # Contact info
    contact_email = Column(String(255), nullable=True)
    contact_name = Column(String(255), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    business_type = relationship("BusinessType", back_populates="organizations")
    evaluation_rounds = relationship("EvaluationRound", back_populates="organization", cascade="all, delete-orphan")
    certifications = relationship("AiucCertification", back_populates="organization", cascade="all, delete-orphan")
    agent_iterations = relationship("AgentIteration", back_populates="organization", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Organization(id={self.id}, name={self.name}, slug={self.slug})>"
