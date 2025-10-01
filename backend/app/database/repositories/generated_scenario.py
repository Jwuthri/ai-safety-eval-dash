"""
Generated scenario repository for database operations.
"""

from typing import List, Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from ..models import GeneratedScenario
from app.utils.logging import get_logger

logger = get_logger("generated_scenario_repository")


class GeneratedScenarioRepository:
    """Repository for generated scenario database operations."""

    @staticmethod
    def create(
        db: Session,
        organization_id: str,
        business_type_id: str,
        input_prompt: str,
        category: Optional[str] = None,
        sub_category: Optional[str] = None,
        input_topic: Optional[str] = None,
        methodology: Optional[str] = None,
        expected_behavior: Optional[str] = None,
        tactics: Optional[List[str]] = None,
        use_case: Optional[str] = None,
        incident_reference: Optional[str] = None,
        generation_prompt: Optional[str] = None,
        model_used: Optional[str] = None,
    ) -> GeneratedScenario:
        """Create a new generated scenario."""
        scenario = GeneratedScenario(
            organization_id=organization_id,
            business_type_id=business_type_id,
            category=category,
            sub_category=sub_category,
            input_topic=input_topic,
            methodology=methodology,
            input_prompt=input_prompt,
            expected_behavior=expected_behavior,
            tactics=tactics or [],
            use_case=use_case,
            incident_reference=incident_reference,
            generation_prompt=generation_prompt,
            model_used=model_used,
        )
        db.add(scenario)
        db.commit()
        db.refresh(scenario)
        return scenario

    @staticmethod
    def get_by_id(db: Session, scenario_id: str) -> Optional[GeneratedScenario]:
        """Get a generated scenario by ID."""
        return db.query(GeneratedScenario).filter(GeneratedScenario.id == scenario_id).first()

    @staticmethod
    def get_by_organization(
        db: Session,
        organization_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[GeneratedScenario]:
        """Get all generated scenarios for an organization."""
        return (
            db.query(GeneratedScenario)
            .filter(GeneratedScenario.organization_id == organization_id)
            .order_by(desc(GeneratedScenario.created_at))
            .limit(limit)
            .offset(offset)
            .all()
        )

    @staticmethod
    def get_by_business_type(
        db: Session,
        business_type_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[GeneratedScenario]:
        """Get all generated scenarios for a business type."""
        return (
            db.query(GeneratedScenario)
            .filter(GeneratedScenario.business_type_id == business_type_id)
            .order_by(desc(GeneratedScenario.created_at))
            .limit(limit)
            .offset(offset)
            .all()
        )

    @staticmethod
    def count_by_organization(db: Session, organization_id: str) -> int:
        """Count scenarios for an organization."""
        return (
            db.query(GeneratedScenario)
            .filter(GeneratedScenario.organization_id == organization_id)
            .count()
        )

    @staticmethod
    def delete_by_organization(db: Session, organization_id: str) -> int:
        """Delete all generated scenarios for an organization."""
        count = (
            db.query(GeneratedScenario)
            .filter(GeneratedScenario.organization_id == organization_id)
            .delete()
        )
        db.commit()
        return count

    @staticmethod
    def delete_by_id(db: Session, scenario_id: str) -> bool:
        """Delete a generated scenario by ID."""
        scenario = GeneratedScenarioRepository.get_by_id(db, scenario_id)
        if scenario:
            db.delete(scenario)
            db.commit()
            return True
        return False

