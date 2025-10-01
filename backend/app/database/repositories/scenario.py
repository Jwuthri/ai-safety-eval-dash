"""
Scenario repository for AI Safety Evaluation Dashboard.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from ...utils.logging import get_logger
from ..models.scenario import Scenario

logger = get_logger("scenario_repository")


class ScenarioRepository:
    """Repository for Scenario model operations."""

    @staticmethod
    def create(
        db: Session,
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
    ) -> Scenario:
        """Create a new scenario."""
        scenario = Scenario(
            business_type_id=business_type_id,
            input_prompt=input_prompt,
            category=category,
            sub_category=sub_category,
            input_topic=input_topic,
            methodology=methodology,
            expected_behavior=expected_behavior,
            tactics=tactics or [],
            use_case=use_case,
            incident_reference=incident_reference,
        )
        db.add(scenario)
        db.commit()
        db.refresh(scenario)
        logger.info(f"Created scenario: {scenario.id} - {scenario.category}")
        return scenario

    @staticmethod
    def get_by_id(db: Session, scenario_id: str) -> Optional[Scenario]:
        """Get scenario by ID."""
        return db.query(Scenario).filter(Scenario.id == scenario_id).first()

    @staticmethod
    def get_by_business_type(db: Session, business_type_id: str) -> List[Scenario]:
        """Get scenarios by business type."""
        return db.query(Scenario).filter(Scenario.business_type_id == business_type_id).all()

    @staticmethod
    def get_by_category(db: Session, category: str) -> List[Scenario]:
        """Get scenarios by category."""
        return db.query(Scenario).filter(Scenario.category == category).all()

    @staticmethod
    def get_by_use_case(db: Session, use_case: str) -> List[Scenario]:
        """Get scenarios by use case."""
        return db.query(Scenario).filter(Scenario.use_case == use_case).all()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Scenario]:
        """Get all scenarios with pagination."""
        return db.query(Scenario).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, scenario_id: str, **kwargs) -> Optional[Scenario]:
        """Update scenario."""
        scenario = ScenarioRepository.get_by_id(db, scenario_id)
        if not scenario:
            return None

        for key, value in kwargs.items():
            if hasattr(scenario, key):
                setattr(scenario, key, value)

        db.commit()
        db.refresh(scenario)
        logger.info(f"Updated scenario: {scenario_id}")
        return scenario

    @staticmethod
    def delete(db: Session, scenario_id: str) -> bool:
        """Delete scenario by ID."""
        scenario = ScenarioRepository.get_by_id(db, scenario_id)
        if scenario:
            db.delete(scenario)
            db.commit()
            logger.info(f"Deleted scenario: {scenario_id}")
            return True
        return False
