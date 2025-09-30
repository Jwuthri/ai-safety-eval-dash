"""
AIUC certification repository for AI Safety Evaluation Dashboard.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy.orm import Session

from ...utils.logging import get_logger
from ..models.aiuc_certification import AiucCertification, CertificationStatus

logger = get_logger("aiuc_certification_repository")


class AiucCertificationRepository:
    """Repository for AiucCertification model operations."""

    @staticmethod
    def create(
        db: Session,
        organization_id: str,
        evaluation_round_id: str,
        certification_status: CertificationStatus = CertificationStatus.PENDING,
        final_pass_rate: Optional[Decimal] = None,
        p2_count: Optional[int] = None,
        p3_count: Optional[int] = None,
        p4_count: Optional[int] = None,
    ) -> AiucCertification:
        """Create a new AIUC certification."""
        certification = AiucCertification(
            organization_id=organization_id,
            evaluation_round_id=evaluation_round_id,
            certification_status=certification_status,
            final_pass_rate=final_pass_rate,
            p2_count=p2_count,
            p3_count=p3_count,
            p4_count=p4_count,
        )
        db.add(certification)
        db.commit()
        db.refresh(certification)
        logger.info(f"Created AIUC certification: {certification.id} - Status: {certification_status}")
        return certification

    @staticmethod
    def get_by_id(db: Session, certification_id: str) -> Optional[AiucCertification]:
        """Get AIUC certification by ID."""
        return db.query(AiucCertification).filter(AiucCertification.id == certification_id).first()

    @staticmethod
    def get_by_organization(db: Session, organization_id: str) -> List[AiucCertification]:
        """Get all certifications for an organization."""
        return (
            db.query(AiucCertification)
            .filter(AiucCertification.organization_id == organization_id)
            .order_by(AiucCertification.issued_at.desc())
            .all()
        )

    @staticmethod
    def get_active_by_organization(db: Session, organization_id: str) -> Optional[AiucCertification]:
        """Get active/certified certification for an organization."""
        return (
            db.query(AiucCertification)
            .filter(
                AiucCertification.organization_id == organization_id,
                AiucCertification.certification_status == CertificationStatus.CERTIFIED,
            )
            .order_by(AiucCertification.issued_at.desc())
            .first()
        )

    @staticmethod
    def get_by_round(db: Session, round_id: str) -> Optional[AiucCertification]:
        """Get certification for an evaluation round."""
        return db.query(AiucCertification).filter(AiucCertification.evaluation_round_id == round_id).first()

    @staticmethod
    def get_by_status(db: Session, status: CertificationStatus) -> List[AiucCertification]:
        """Get certifications by status."""
        return db.query(AiucCertification).filter(AiucCertification.certification_status == status).all()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[AiucCertification]:
        """Get all certifications with pagination."""
        return db.query(AiucCertification).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, certification_id: str, **kwargs) -> Optional[AiucCertification]:
        """Update AIUC certification."""
        certification = AiucCertificationRepository.get_by_id(db, certification_id)
        if not certification:
            return None

        for key, value in kwargs.items():
            if hasattr(certification, key):
                setattr(certification, key, value)

        db.commit()
        db.refresh(certification)
        logger.info(f"Updated AIUC certification: {certification_id}")
        return certification

    @staticmethod
    def certify(db: Session, certification_id: str, expires_at: Optional[datetime] = None) -> Optional[AiucCertification]:
        """Mark certification as certified."""
        return AiucCertificationRepository.update(
            db,
            certification_id,
            certification_status=CertificationStatus.CERTIFIED,
            issued_at=datetime.utcnow(),
            expires_at=expires_at,
        )

    @staticmethod
    def revoke(db: Session, certification_id: str) -> Optional[AiucCertification]:
        """Revoke a certification."""
        return AiucCertificationRepository.update(
            db,
            certification_id,
            certification_status=CertificationStatus.REVOKED,
        )

    @staticmethod
    def delete(db: Session, certification_id: str) -> bool:
        """Delete AIUC certification by ID."""
        certification = AiucCertificationRepository.get_by_id(db, certification_id)
        if certification:
            db.delete(certification)
            db.commit()
            logger.info(f"Deleted AIUC certification: {certification_id}")
            return True
        return False
