"""
AIUC Certification model for AI Safety Evaluation Dashboard.
"""

import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import List, Dict, Any, Optional

from sqlalchemy import JSON, Boolean, Column, DateTime, Date, String, Numeric
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID

from ..base import Base
from .enums import CertificationStatus


class AIUCCertification(Base):
    """
    AIUC-1 certification and insurance status tracking.
    
    Manages certification status, insurance eligibility, and coverage amounts
    to support the confidence infrastructure's insurance value proposition.
    """
    __tablename__ = "aiuc_certifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vendor_name = Column(String(255), nullable=False, index=True)
    model_name = Column(String(255), nullable=False)
    
    # Certification status
    certification_status = Column(SQLEnum(CertificationStatus), nullable=False, index=True)
    certification_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True)
    framework_version = Column(String(50), nullable=False)
    
    # Insurance coverage
    insurance_eligible = Column(Boolean, nullable=False, default=False)
    insurance_coverage_usd = Column(Numeric(15, 2), nullable=True)
    insurance_provider = Column(String(255), nullable=True)
    policy_start_date = Column(Date, nullable=True)
    policy_end_date = Column(Date, nullable=True)
    
    # Evaluation linkage
    evaluation_ids = Column(JSON, nullable=True)  # Array of evaluation IDs that support this certification
    
    # Compliance details
    compliance_score = Column(Numeric(5, 2), nullable=True)  # 0-100 compliance score
    aiuc_controls_passed = Column(JSON, nullable=True)  # Which AIUC-1 controls were verified
    residual_risks = Column(JSON, nullable=True)  # Documented residual risks after certification
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    @property
    def is_active(self) -> bool:
        """Check if certification is currently active."""
        if self.certification_status != CertificationStatus.ACTIVE:
            return False
        
        if self.expiry_date and self.expiry_date < date.today():
            return False
        
        return True

    @property
    def insurance_status(self) -> Dict[str, Any]:
        """Get structured insurance status information."""
        return {
            "eligible": self.insurance_eligible,
            "coverage_amount_usd": float(self.insurance_coverage_usd) if self.insurance_coverage_usd else None,
            "provider": self.insurance_provider,
            "policy_active": self.is_policy_active,
            "policy_start_date": self.policy_start_date.isoformat() if self.policy_start_date else None,
            "policy_end_date": self.policy_end_date.isoformat() if self.policy_end_date else None
        }

    @property
    def is_policy_active(self) -> bool:
        """Check if insurance policy is currently active."""
        if not self.insurance_eligible or not self.policy_start_date or not self.policy_end_date:
            return False
        
        today = date.today()
        return self.policy_start_date <= today <= self.policy_end_date

    @property
    def certification_summary(self) -> Dict[str, Any]:
        """Get structured certification summary."""
        return {
            "vendor_name": self.vendor_name,
            "model_name": self.model_name,
            "status": self.certification_status.value,
            "is_active": self.is_active,
            "certification_date": self.certification_date.isoformat() if self.certification_date else None,
            "expiry_date": self.expiry_date.isoformat() if self.expiry_date else None,
            "framework_version": self.framework_version,
            "compliance_score": float(self.compliance_score) if self.compliance_score else None,
            "insurance_status": self.insurance_status
        }

    def __repr__(self):
        return (f"<AIUCCertification(id={self.id}, vendor={self.vendor_name}, "
                f"model={self.model_name}, status={self.certification_status})>")