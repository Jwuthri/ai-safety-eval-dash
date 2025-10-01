"""
Safeguard/Mitigation model for AI Safety Dashboard.

Maps incidents to preventive measures and detection strategies.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, ARRAY, JSON
from sqlalchemy.orm import relationship

from ..base import Base


class Safeguard(Base):
    """
    Safeguard model representing preventive measures for AI incidents.
    
    Example:
    - Incident: AirCanada refund hallucination
    - Safeguard: Grounding in policy documents + confidence thresholds
    - Implementation: RAG with fact-checking layer
    """
    __tablename__ = "safeguards"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Safeguard identification
    name = Column(String(255), nullable=False)  # e.g., "Policy Document Grounding"
    category = Column(String(100), nullable=False)  # e.g., "hallucination_prevention", "prompt_injection_defense"
    
    # Description
    description = Column(Text, nullable=False)  # What this safeguard does
    why_it_works = Column(Text, nullable=True)  # Technical explanation
    
    # Implementation
    implementation_type = Column(String(100), nullable=False)  # e.g., "RAG", "prompt_engineering", "output_validation", "input_filtering"
    implementation_details = Column(JSON, nullable=True)  # Code snippets, config examples
    
    # AIUC-1 compliance mapping
    aiuc_requirement = Column(String(100), nullable=True)  # e.g., "AIUC-1.2.3"
    compliance_level = Column(String(50), nullable=True)  # e.g., "required", "recommended", "optional"
    
    # Effectiveness
    effectiveness_rating = Column(String(20), nullable=True)  # e.g., "high", "medium", "low"
    reduces_severity = Column(ARRAY(String), default=list)  # e.g., ["P0", "P1"] - which severities this prevents
    
    # Detection & Response
    detection_method = Column(Text, nullable=True)  # How to detect violations
    automated_response = Column(Text, nullable=True)  # What to do when detected
    
    # Related incidents (many-to-many will be defined separately)
    incident_types = Column(ARRAY(String), default=list)  # e.g., ["hallucination", "prompt_injection"]
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Safeguard(name={self.name}, category={self.category})>"


# Junction table for incident-safeguard mapping
class IncidentSafeguardMapping(Base):
    """Maps specific incidents to their recommended safeguards."""
    __tablename__ = "incident_safeguard_mappings"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    incident_id = Column(String, ForeignKey("ai_incidents.id"), nullable=False)
    safeguard_id = Column(String, ForeignKey("safeguards.id"), nullable=False)
    
    # How this safeguard addresses this incident
    effectiveness_note = Column(Text, nullable=True)
    priority = Column(String(20), nullable=True)  # e.g., "critical", "high", "medium", "low"
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<IncidentSafeguardMapping(incident={self.incident_id}, safeguard={self.safeguard_id})>"

