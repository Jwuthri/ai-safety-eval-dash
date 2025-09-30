"""
AIUC certification database model for AI Safety Evaluation Dashboard.
"""

import enum
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Column, DateTime, Enum as SQLEnum, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.orm import relationship

from ..base import Base


class CertificationStatus(str, enum.Enum):
    """AIUC certification status."""
    PENDING = "pending"
    CERTIFIED = "certified"
    REVOKED = "revoked"


class AiucCertification(Base):
    """
    AIUC-1 certification model for tracking AI safety certification.
    
    Issued to an organization when they achieve:
    - P0 count = 0
    - P1 count = 0
    - P2 count = 0
    - P3 count = 0
    - P4 count = 0
    """
    __tablename__ = "aiuc_certifications"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    evaluation_round_id = Column(String, ForeignKey("evaluation_rounds.id"), nullable=False)
    
    certification_status = Column(SQLEnum(CertificationStatus), default=CertificationStatus.PENDING)
    
    # Certificate details
    issued_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    
    # Metrics snapshot
    final_pass_rate = Column(Numeric(5, 2), nullable=True)  # e.g., 97.40
    p2_count = Column(Integer, default=0)
    p3_count = Column(Integer, default=0)
    p4_count = Column(Integer, default=0)
    
    # Relationships
    organization = relationship("Organization", back_populates="certifications")
    evaluation_round = relationship("EvaluationRound", back_populates="certifications")

    # Indexes
    __table_args__ = (
        Index('ix_cert_org_status', 'organization_id', 'certification_status'),
        Index('ix_cert_issued', 'issued_at'),
    )

    def __repr__(self):
        return f"<AiucCertification(id={self.id}, status={self.certification_status})>"
