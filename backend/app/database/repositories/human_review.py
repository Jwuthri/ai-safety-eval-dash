"""
Human review repository for AI Safety Evaluation Dashboard.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from ...utils.logging import get_logger
from ..models.human_review import HumanReview, ReviewStatus

logger = get_logger("human_review_repository")


class HumanReviewRepository:
    """Repository for HumanReview model operations."""

    @staticmethod
    def create(
        db: Session,
        evaluation_result_id: str,
        reviewer_id: Optional[str] = None,
        review_status: ReviewStatus = ReviewStatus.NEEDS_IMPROVEMENT,
        override_grade: Optional[str] = None,
        comments: Optional[str] = None,
    ) -> HumanReview:
        """Create a new human review."""
        human_review = HumanReview(
            evaluation_result_id=evaluation_result_id,
            reviewer_id=reviewer_id,
            review_status=review_status,
            override_grade=override_grade,
            comments=comments,
        )
        db.add(human_review)
        db.commit()
        db.refresh(human_review)
        logger.info(f"Created human review: {human_review.id} - Status: {review_status}")
        return human_review

    @staticmethod
    def get_by_id(db: Session, review_id: str) -> Optional[HumanReview]:
        """Get human review by ID."""
        return db.query(HumanReview).filter(HumanReview.id == review_id).first()

    @staticmethod
    def get_by_result(db: Session, result_id: str) -> List[HumanReview]:
        """Get all human reviews for an evaluation result."""
        return db.query(HumanReview).filter(HumanReview.evaluation_result_id == result_id).all()

    @staticmethod
    def get_by_reviewer(db: Session, reviewer_id: str) -> List[HumanReview]:
        """Get all reviews by a specific reviewer."""
        return db.query(HumanReview).filter(HumanReview.reviewer_id == reviewer_id).all()

    @staticmethod
    def get_by_status(db: Session, status: ReviewStatus) -> List[HumanReview]:
        """Get reviews by status."""
        return db.query(HumanReview).filter(HumanReview.review_status == status).all()

    @staticmethod
    def get_pending_reviews(db: Session) -> List[HumanReview]:
        """Get all reviews that need improvement."""
        return db.query(HumanReview).filter(HumanReview.review_status == ReviewStatus.NEEDS_IMPROVEMENT).all()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[HumanReview]:
        """Get all human reviews with pagination."""
        return db.query(HumanReview).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, review_id: str, **kwargs) -> Optional[HumanReview]:
        """Update human review."""
        human_review = HumanReviewRepository.get_by_id(db, review_id)
        if not human_review:
            return None

        for key, value in kwargs.items():
            if hasattr(human_review, key):
                setattr(human_review, key, value)

        db.commit()
        db.refresh(human_review)
        logger.info(f"Updated human review: {review_id}")
        return human_review

    @staticmethod
    def delete(db: Session, review_id: str) -> bool:
        """Delete human review by ID."""
        human_review = HumanReviewRepository.get_by_id(db, review_id)
        if human_review:
            db.delete(human_review)
            db.commit()
            logger.info(f"Deleted human review: {review_id}")
            return True
        return False
