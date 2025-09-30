"""
Evaluation round repository for AI Safety Evaluation Dashboard.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from ...utils.logging import get_logger
from ..models.evaluation_round import EvaluationRound, EvaluationRoundStatus

logger = get_logger("evaluation_round_repository")


class EvaluationRoundRepository:
    """Repository for EvaluationRound model operations."""

    @staticmethod
    def create(
        db: Session,
        organization_id: str,
        round_number: int,
        description: Optional[str] = None,
        status: EvaluationRoundStatus = EvaluationRoundStatus.RUNNING,
    ) -> EvaluationRound:
        """Create a new evaluation round."""
        evaluation_round = EvaluationRound(
            organization_id=organization_id,
            round_number=round_number,
            description=description,
            status=status,
        )
        db.add(evaluation_round)
        db.commit()
        db.refresh(evaluation_round)
        logger.info(f"Created evaluation round: {evaluation_round.id} - Round {round_number} for org {organization_id}")
        return evaluation_round

    @staticmethod
    def get_by_id(db: Session, round_id: str) -> Optional[EvaluationRound]:
        """Get evaluation round by ID."""
        return db.query(EvaluationRound).filter(EvaluationRound.id == round_id).first()

    @staticmethod
    def get_by_organization(db: Session, organization_id: str) -> List[EvaluationRound]:
        """Get all evaluation rounds for an organization."""
        return (
            db.query(EvaluationRound)
            .filter(EvaluationRound.organization_id == organization_id)
            .order_by(EvaluationRound.round_number.desc())
            .all()
        )

    @staticmethod
    def get_latest_by_organization(db: Session, organization_id: str) -> Optional[EvaluationRound]:
        """Get the latest evaluation round for an organization."""
        return (
            db.query(EvaluationRound)
            .filter(EvaluationRound.organization_id == organization_id)
            .order_by(EvaluationRound.round_number.desc())
            .first()
        )

    @staticmethod
    def get_by_org_and_round(
        db: Session, organization_id: str, round_number: int
    ) -> Optional[EvaluationRound]:
        """Get evaluation round by organization ID and round number."""
        return (
            db.query(EvaluationRound)
            .filter(
                EvaluationRound.organization_id == organization_id,
                EvaluationRound.round_number == round_number,
            )
            .first()
        )

    @staticmethod
    def get_by_status(db: Session, status: EvaluationRoundStatus) -> List[EvaluationRound]:
        """Get evaluation rounds by status."""
        return db.query(EvaluationRound).filter(EvaluationRound.status == status).all()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[EvaluationRound]:
        """Get all evaluation rounds with pagination."""
        return db.query(EvaluationRound).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, round_id: str, **kwargs) -> Optional[EvaluationRound]:
        """Update evaluation round."""
        evaluation_round = EvaluationRoundRepository.get_by_id(db, round_id)
        if not evaluation_round:
            return None

        for key, value in kwargs.items():
            if hasattr(evaluation_round, key):
                setattr(evaluation_round, key, value)

        db.commit()
        db.refresh(evaluation_round)
        logger.info(f"Updated evaluation round: {round_id}")
        return evaluation_round

    @staticmethod
    def complete(db: Session, round_id: str) -> Optional[EvaluationRound]:
        """Mark evaluation round as completed."""
        return EvaluationRoundRepository.update(
            db,
            round_id,
            status=EvaluationRoundStatus.COMPLETED,
            completed_at=datetime.utcnow(),
        )

    @staticmethod
    def fail(db: Session, round_id: str) -> Optional[EvaluationRound]:
        """Mark evaluation round as failed."""
        return EvaluationRoundRepository.update(
            db,
            round_id,
            status=EvaluationRoundStatus.FAILED,
            completed_at=datetime.utcnow(),
        )

    @staticmethod
    def delete(db: Session, round_id: str) -> bool:
        """Delete evaluation round by ID."""
        evaluation_round = EvaluationRoundRepository.get_by_id(db, round_id)
        if evaluation_round:
            db.delete(evaluation_round)
            db.commit()
            logger.info(f"Deleted evaluation round: {round_id}")
            return True
        return False
