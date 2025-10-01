"""
AI Incident database model for tracking real-world AI failures.

Examples:
- AirCanada chatbot: Refund policy hallucination
- Google Gemini: Image generation bias incidents
- Microsoft Tay: Offensive content generation
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, Numeric
from sqlalchemy.orm import relationship

from ..base import Base


class AIIncident(Base):
    """
    Real-world AI incident model for mapping to preventive scenarios.
    
    Purpose: Show buyers "This is what happened" → "Here's how we test for it"
    """
    __tablename__ = "ai_incidents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Incident identification
    incident_name = Column(String(255), nullable=False)  # e.g., "AirCanada Refund Hallucination"
    company = Column(String(255), nullable=False)  # e.g., "Air Canada"
    date_occurred = Column(DateTime, nullable=True)  # When it happened
    
    # Classification
    harm_type = Column(String(100), nullable=False)  # e.g., "financial_loss", "reputation_damage", "privacy_breach"
    severity = Column(String(10), nullable=False)  # P0-P4 severity level
    
    # Details
    description = Column(Text, nullable=False)  # What happened
    root_cause = Column(Text, nullable=True)  # Why it happened
    impact_description = Column(Text, nullable=True)  # What damage was done
    
    # Financial impact
    estimated_cost = Column(Numeric(precision=15, scale=2), nullable=True)  # Dollar amount
    affected_users = Column(Integer, nullable=True)  # Number of users impacted
    
    # References
    source_url = Column(String(500), nullable=True)  # Link to news article/report
    incident_reference = Column(String(255), nullable=True, unique=True)  # Unique identifier
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<AIIncident(name={self.incident_name}, company={self.company}, severity={self.severity})>"

