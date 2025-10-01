"""
Pydantic models for AI Incident API.
"""

from datetime import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field


class AIIncidentBase(BaseModel):
    """Base AI Incident model."""
    incident_name: str = Field(..., description="Name of the incident", max_length=255)
    company: str = Field(..., description="Company where incident occurred", max_length=255)
    date_occurred: Optional[datetime] = Field(None, description="When the incident happened")
    harm_type: str = Field(..., description="Type of harm (financial_loss, reputation_damage, etc.)", max_length=100)
    severity: str = Field(..., description="Severity level (P0-P4)", max_length=10)
    description: str = Field(..., description="What happened")
    root_cause: Optional[str] = Field(None, description="Why it happened")
    impact_description: Optional[str] = Field(None, description="What damage was done")
    estimated_cost: Optional[Decimal] = Field(None, description="Dollar amount of damage")
    affected_users: Optional[int] = Field(None, description="Number of users impacted")
    source_url: Optional[str] = Field(None, description="Link to news article/report", max_length=500)
    incident_reference: Optional[str] = Field(None, description="Unique identifier", max_length=255)


class AIIncidentCreate(AIIncidentBase):
    """Model for creating an AI Incident."""
    pass


class AIIncidentUpdate(BaseModel):
    """Model for updating an AI Incident."""
    incident_name: Optional[str] = Field(None, max_length=255)
    company: Optional[str] = Field(None, max_length=255)
    date_occurred: Optional[datetime] = None
    harm_type: Optional[str] = Field(None, max_length=100)
    severity: Optional[str] = Field(None, max_length=10)
    description: Optional[str] = None
    root_cause: Optional[str] = None
    impact_description: Optional[str] = None
    estimated_cost: Optional[Decimal] = None
    affected_users: Optional[int] = None
    source_url: Optional[str] = Field(None, max_length=500)
    incident_reference: Optional[str] = Field(None, max_length=255)


class AIIncidentResponse(AIIncidentBase):
    """Model for AI Incident response."""
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "incident_name": "AirCanada Refund Hallucination",
                "company": "Air Canada",
                "date_occurred": "2024-02-15T00:00:00Z",
                "harm_type": "financial_loss",
                "severity": "P1",
                "description": "Chatbot hallucinated refund policy, promising customer full refund. Customer won in court. Company had to honor false promise.",
                "root_cause": "LLM hallucination without proper guardrails",
                "impact_description": "Legal precedent set, reputation damage, financial loss",
                "estimated_cost": 15000.00,
                "affected_users": 1,
                "source_url": "https://www.cbc.ca/news/canada/air-canada-chatbot-refund-1.7110426",
                "incident_reference": "aircanada-2024-refund",
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": None
            }
        }

