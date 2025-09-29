"""
AI Incident model for AI Safety Evaluation Dashboard.
"""

import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import List, Dict, Any, Optional

from sqlalchemy import JSON, Boolean, Column, DateTime, Date, String, Text, Numeric
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID

from ..base import Base
from .enums import SeverityLevel, BaseRateFrequency, BaseRateSeverity


class AIIncident(Base):
    """
    AI incidents with incident → harm → tactic → use case → context flow mapping.
    
    Stores real-world AI incidents with business impact data to support the 
    confidence infrastructure narrative. Includes featured examples like Air Canada
    with concrete financial impact ($5,000 + legal costs + brand damage).
    """
    __tablename__ = "ai_incidents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    
    # Incident → Harm → Tactic → Use Case → Context flow
    harm_type = Column(String(255), nullable=False, index=True)  # e.g., financial loss, brand damage, data leakage
    attack_tactic = Column(String(255), nullable=True)  # e.g., jailbreak, encoding attack, emotional manipulation
    use_case = Column(String(255), nullable=False)  # e.g., customer support, content generation
    context = Column(Text, nullable=True)  # Business/industry specific context
    
    # Classification
    severity = Column(SQLEnum(SeverityLevel), nullable=False, index=True)
    modality = Column(String(50), nullable=False)
    industry = Column(String(255), nullable=True, index=True)
    
    # Business impact (concrete examples like Air Canada)
    financial_impact_usd = Column(Numeric(15, 2), nullable=True)  # e.g., $5,000 for Air Canada
    legal_defense_cost_usd = Column(Numeric(15, 2), nullable=True)
    brand_impact_description = Column(Text, nullable=True)
    regulatory_impact = Column(Text, nullable=True)
    
    # Base rate data for risk assessment
    base_rate_frequency = Column(String(20), nullable=True)  # low, medium, high
    base_rate_severity = Column(String(20), nullable=True)  # low, medium-low, medium, medium-high, high
    
    # Technical details and prevention
    root_cause = Column(Text, nullable=True)
    aiuc_safeguard_ids = Column(JSON, nullable=True)  # Links to AIUC-1 controls
    prevention_measures = Column(JSON, nullable=True)
    example_prompt = Column(Text, nullable=True)  # Sanitized example that triggered the incident
    
    # Metadata
    incident_date = Column(Date, nullable=True)
    source_url = Column(String(500), nullable=True)
    verified = Column(Boolean, nullable=False, default=False)
    is_featured_example = Column(Boolean, nullable=False, default=False, index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    @property
    def total_financial_impact(self) -> Optional[Decimal]:
        """Calculate total financial impact including direct costs and legal defense."""
        if self.financial_impact_usd is None:
            return None
        
        total = self.financial_impact_usd
        if self.legal_defense_cost_usd:
            total += self.legal_defense_cost_usd
        
        return total

    @property
    def business_impact_summary(self) -> Dict[str, Any]:
        """Get structured business impact summary."""
        return {
            "financial_impact_usd": float(self.financial_impact_usd) if self.financial_impact_usd else None,
            "legal_defense_cost_usd": float(self.legal_defense_cost_usd) if self.legal_defense_cost_usd else None,
            "total_financial_impact_usd": float(self.total_financial_impact) if self.total_financial_impact else None,
            "brand_impact": self.brand_impact_description,
            "regulatory_impact": self.regulatory_impact,
            "base_rate_frequency": self.base_rate_frequency,
            "base_rate_severity": self.base_rate_severity
        }

    @property
    def incident_flow(self) -> Dict[str, str]:
        """Get the incident → harm → tactic → use case → context flow."""
        return {
            "incident": self.incident_name,
            "harm": self.harm_type,
            "tactic": self.attack_tactic,
            "use_case": self.use_case,
            "context": self.context
        }

    def __repr__(self):
        return (f"<AIIncident(id={self.id}, name={self.incident_name}, "
                f"severity={self.severity}, industry={self.industry})>")