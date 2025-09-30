"""
Business type repository for AI Safety Evaluation Dashboard.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from ...utils.logging import get_logger
from ..models.business_type import BusinessType

logger = get_logger("business_type_repository")


class BusinessTypeRepository:
    """Repository for BusinessType model operations."""

    @staticmethod
    def create(
        db: Session,
        name: str,
        industry: Optional[str] = None,
        use_cases: Optional[List[str]] = None,
        context: Optional[str] = None,
    ) -> BusinessType:
        """Create a new business type."""
        business_type = BusinessType(
            name=name,
            industry=industry,
            use_cases=use_cases or [],
            context=context,
        )
        db.add(business_type)
        db.commit()
        db.refresh(business_type)
        logger.info(f"Created business type: {business_type.id} - {business_type.name}")
        return business_type

    @staticmethod
    def get_by_id(db: Session, business_type_id: str) -> Optional[BusinessType]:
        """Get business type by ID."""
        return db.query(BusinessType).filter(BusinessType.id == business_type_id).first()

    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[BusinessType]:
        """Get business type by name."""
        return db.query(BusinessType).filter(BusinessType.name == name).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[BusinessType]:
        """Get all business types with pagination."""
        return db.query(BusinessType).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_industry(db: Session, industry: str) -> List[BusinessType]:
        """Get business types by industry."""
        return db.query(BusinessType).filter(BusinessType.industry == industry).all()

    @staticmethod
    def update(db: Session, business_type_id: str, **kwargs) -> Optional[BusinessType]:
        """Update business type."""
        business_type = BusinessTypeRepository.get_by_id(db, business_type_id)
        if not business_type:
            return None

        for key, value in kwargs.items():
            if hasattr(business_type, key):
                setattr(business_type, key, value)

        db.commit()
        db.refresh(business_type)
        logger.info(f"Updated business type: {business_type_id}")
        return business_type

    @staticmethod
    def delete(db: Session, business_type_id: str) -> bool:
        """Delete business type by ID."""
        business_type = BusinessTypeRepository.get_by_id(db, business_type_id)
        if business_type:
            db.delete(business_type)
            db.commit()
            logger.info(f"Deleted business type: {business_type_id}")
            return True
        return False
