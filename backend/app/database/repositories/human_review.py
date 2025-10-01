"""
Human Review repository for AI Safety Evaluation Dashboard.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from ...utils.logging import get_logger
from ..models.human_review import HumanReview

logger = get_logger("human_review_repository")


class HumanReviewRepository:
    """Repository for HumanReview model operations."""

    @staticmethod
    def create(
        db: Session,
        evaluation_result_id: str,
        original_grade: str,
        original_confidence: int,
        reviewed_grade: str,
        reviewer_id: Optional[str] = None,
        reviewer_name: Optional[str] = None,
        review_notes: Optional[str] = None,
    ) -> HumanReview:
        """Create a new human review."""
        review = HumanReview(
            evaluation_result_id=evaluation_result_id,
            original_grade=original_grade,
            original_confidence=original_confidence,
            reviewed_grade=reviewed_grade,
            reviewer_id=reviewer_id,
            reviewer_name=reviewer_name,
            review_notes=review_notes,
        )
        db.add(review)
        db.commit()
        db.refresh(review)
        logger.info(f"Created human review: {review.id} - {original_grade}→{reviewed_grade}")
        return review

    @staticmethod
    def get_by_id(db: Session, review_id: str) -> Optional[HumanReview]:
        """Get human review by ID."""
        return db.query(HumanReview).filter(HumanReview.id == review_id).first()

    @staticmethod
    def get_by_evaluation_result(db: Session, result_id: str) -> List[HumanReview]:
        """Get human reviews for a specific evaluation result."""
        return db.query(HumanReview).filter(
            HumanReview.evaluation_result_id == result_id
        ).all()

    @staticmethod
    def get_by_reviewer(db: Session, reviewer_id: str) -> List[HumanReview]:
        """Get all reviews by a specific reviewer."""
        return db.query(HumanReview).filter(
            HumanReview.reviewer_id == reviewer_id
        ).all()

    @staticmethod
    def get_by_round(db: Session, round_id: str) -> List[HumanReview]:
        """Get all human reviews for an evaluation round."""
        from ..models.evaluation_result import EvaluationResult
        
        return db.query(HumanReview).join(
            EvaluationResult,
            HumanReview.evaluation_result_id == EvaluationResult.id
        ).filter(
            EvaluationResult.evaluation_round_id == round_id
        ).all()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[HumanReview]:
        """Get all human reviews with pagination."""
        return db.query(HumanReview).offset(skip).limit(limit).all()

    @staticmethod
    def delete(db: Session, review_id: str) -> bool:
        """Delete a human review."""
        review = HumanReviewRepository.get_by_id(db, review_id)
        if review:
            db.delete(review)
            db.commit()
            logger.info(f"Deleted human review: {review_id}")
            return True
        return False
