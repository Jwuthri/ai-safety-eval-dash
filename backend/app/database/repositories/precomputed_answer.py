"""
Repository for PreComputedAnswer model.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from ..models.precomputed_answer import PreComputedAnswer


class PreComputedAnswerRepository:
    """Repository for managing precomputed answer records."""

    @staticmethod
    def create(
        db: Session,
        organization_id: str,
        scenario_id: str,
        round_number: int,
        assistant_output: str,
        notes: Optional[str] = None,
    ) -> PreComputedAnswer:
        """
        Create a new precomputed answer record.
        
        Args:
            db: Database session
            organization_id: Organization ID
            scenario_id: Scenario ID
            round_number: Round number (1, 2, 3, etc.)
            assistant_output: The bot's response
            notes: Optional notes
            
        Returns:
            Created PreComputedAnswer
        """
        answer = PreComputedAnswer(
            organization_id=organization_id,
            scenario_id=scenario_id,
            round_number=round_number,
            assistant_output=assistant_output,
            notes=notes,
        )
        db.add(answer)
        db.commit()
        db.refresh(answer)
        return answer

    @staticmethod
    def get_by_id(db: Session, answer_id: str) -> Optional[PreComputedAnswer]:
        """Get answer by ID."""
        return db.query(PreComputedAnswer).filter_by(id=answer_id).first()

    @staticmethod
    def get_by_scenario_and_round(
        db: Session, scenario_id: str, round_number: int, organization_id: str
    ) -> Optional[PreComputedAnswer]:
        """Get answer for a specific scenario, round, and organization."""
        return (
            db.query(PreComputedAnswer)
            .filter_by(
                scenario_id=scenario_id,
                round_number=round_number,
                organization_id=organization_id
            )
            .first()
        )

    @staticmethod
    def get_by_round(
        db: Session, organization_id: str, round_number: int
    ) -> List[PreComputedAnswer]:
        """Get all answers for an organization in a specific round."""
        return (
            db.query(PreComputedAnswer)
            .filter_by(organization_id=organization_id, round_number=round_number)
            .all()
        )

    @staticmethod
    def get_by_organization(
        db: Session, organization_id: str
    ) -> List[PreComputedAnswer]:
        """Get all answers for an organization."""
        return (
            db.query(PreComputedAnswer)
            .filter_by(organization_id=organization_id)
            .all()
        )

    @staticmethod
    def delete(db: Session, answer_id: str) -> bool:
        """Delete a precomputed answer."""
        answer = db.query(PreComputedAnswer).filter_by(id=answer_id).first()
        if answer:
            db.delete(answer)
            db.commit()
            return True
        return False
