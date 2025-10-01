"""
Organization repository for AI Safety Evaluation Dashboard.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from ...utils.logging import get_logger
from ..models.organization import Organization

logger = get_logger("organization_repository")


class OrganizationRepository:
    """Repository for Organization model operations."""

    @staticmethod
    def create(
        db: Session,
        business_type_id: str,
        name: str,
        slug: str,
        contact_email: Optional[str] = None,
        contact_name: Optional[str] = None,
        is_active: bool = True,
    ) -> Organization:
        """Create a new organization."""
        organization = Organization(
            business_type_id=business_type_id,
            name=name,
            slug=slug,
            contact_email=contact_email,
            contact_name=contact_name,
            is_active=is_active,
        )
        db.add(organization)
        db.commit()
        db.refresh(organization)
        logger.info(f"Created organization: {organization.id} - {organization.name}")
        return organization

    @staticmethod
    def get_by_id(db: Session, organization_id: str) -> Optional[Organization]:
        """Get organization by ID."""
        return db.query(Organization).filter(Organization.id == organization_id).first()

    @staticmethod
    def get_by_slug(db: Session, slug: str) -> Optional[Organization]:
        """Get organization by slug."""
        return db.query(Organization).filter(Organization.slug == slug).first()

    @staticmethod
    def get_by_business_type(db: Session, business_type_id: str) -> List[Organization]:
        """Get organizations by business type."""
        return db.query(Organization).filter(Organization.business_type_id == business_type_id).all()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100, active_only: bool = False) -> List[Organization]:
        """Get all organizations with pagination."""
        query = db.query(Organization)
        if active_only:
            query = query.filter(Organization.is_active == True)
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, organization_id: str, **kwargs) -> Optional[Organization]:
        """Update organization."""
        organization = OrganizationRepository.get_by_id(db, organization_id)
        if not organization:
            return None

        for key, value in kwargs.items():
            if hasattr(organization, key):
                setattr(organization, key, value)

        organization.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(organization)
        logger.info(f"Updated organization: {organization_id}")
        return organization

    @staticmethod
    def delete(db: Session, organization_id: str) -> bool:
        """Delete organization by ID."""
        organization = OrganizationRepository.get_by_id(db, organization_id)
        if organization:
            db.delete(organization)
            db.commit()
            logger.info(f"Deleted organization: {organization_id}")
            return True
        return False

    @staticmethod
    def deactivate(db: Session, organization_id: str) -> Optional[Organization]:
        """Deactivate organization (soft delete)."""
        return OrganizationRepository.update(db, organization_id, is_active=False)
