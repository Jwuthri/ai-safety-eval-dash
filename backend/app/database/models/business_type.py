"""
Business type database model for AI Safety Evaluation Dashboard.
"""

import uuid
from datetime import datetime

from sqlalchemy import ARRAY, Column, DateTime, String, Text
from sqlalchemy.orm import relationship

from ..base import Base


class BusinessType(Base):
    """
    Business type model - predefined universal categories for different industries.
    
    Examples:
    - "Airlines Customer Support" (AirCanada, Delta, etc. use this)
    - "API Developer Support" (Pinterest, Stripe, etc. use this)
    - "E-commerce Support" (Shopify, Amazon, etc. use this)
    
    These are templates - orgs pick which one they belong to.
    """
    __tablename__ = "business_types"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, unique=True, index=True)
    industry = Column(String(100), nullable=True)
    use_cases = Column(ARRAY(String), default=list)  # e.g., ["customer_support", "refunds", "booking"]
    context = Column(String(100), nullable=True)  # e.g., "retail_airlines", "tech_platform"
    description = Column(Text, nullable=True)  # Detailed description for buyers
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    organizations = relationship("Organization", back_populates="business_type")
    scenarios = relationship("Scenario", back_populates="business_type", cascade="all, delete-orphan")
    incidents = relationship("AIIncident", back_populates="business_type", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<BusinessType(id={self.id}, name={self.name}, industry={self.industry})>"