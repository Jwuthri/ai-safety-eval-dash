"""
Certification models.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field

from .enums import CertificationStatusEnum


class CertificationCheck(BaseModel):
    """Certification eligibility check result."""
    eligible: bool = Field(..., description="Eligible for certification")
    level: str = Field(..., description="Certification level")
    message: str = Field(..., description="Status message")
    blockers: List[str] = Field(default_factory=list, description="Blocking issues")

    class Config:
        json_schema_extra = {
            "example": {
                "eligible": False,
                "level": "Near Certification",
                "message": "Only minor issues remaining. 5 P3 and 2 P4 to resolve.",
                "blockers": []
            }
        }


class CertificationCreate(BaseModel):
    """Certification issuance request."""
    organization_id: str = Field(..., description="Organization ID")
    evaluation_round_id: str = Field(..., description="Evaluation round ID")


# Alias for backwards compatibility
CertificationIssue = CertificationCreate


class CertificationResponse(BaseModel):
    """AIUC certification response."""
    id: str = Field(..., description="Certificate ID")
    organization_id: str = Field(..., description="Organization ID")
    evaluation_round_id: str = Field(..., description="Evaluation round ID")
    certification_status: CertificationStatusEnum = Field(..., description="Status")
    issued_at: Optional[datetime] = Field(None, description="Issue timestamp")
    expires_at: Optional[datetime] = Field(None, description="Expiry timestamp")
    final_pass_rate: Optional[Decimal] = Field(None, description="Final pass rate")
    p2_count: int = Field(..., description="P2 count")
    p3_count: int = Field(..., description="P3 count")
    p4_count: int = Field(..., description="P4 count")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "AIUC-1-2025-001",
                "organization_id": "org_123",
                "evaluation_round_id": "round_456",
                "certification_status": "certified",
                "issued_at": "2025-01-01T12:00:00Z",
                "expires_at": "2026-01-01T12:00:00Z",
                "final_pass_rate": 97.4,
                "p2_count": 0,
                "p3_count": 0,
                "p4_count": 0
            }
        }
