"""
Evaluation result repository for AI Safety Evaluation Dashboard.
"""

from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from ...utils.logging import get_logger
from ..models.evaluation_result import EvaluationResult

logger = get_logger("evaluation_result_repository")


class EvaluationResultRepository:
    """Repository for EvaluationResult model operations."""

    @staticmethod
    def create(
        db: Session,
        evaluation_round_id: str,
        scenario_id: str,
        system_response: str,
        final_grade: Optional[str] = None,
        confidence_score: Optional[int] = None,
        judge_1_grade: Optional[str] = None,
        judge_1_reasoning: Optional[str] = None,
        judge_1_recommendation: Optional[str] = None,
        judge_1_model: Optional[str] = None,
        judge_2_grade: Optional[str] = None,
        judge_2_reasoning: Optional[str] = None,
        judge_2_recommendation: Optional[str] = None,
        judge_2_model: Optional[str] = None,
        judge_3_grade: Optional[str] = None,
        judge_3_reasoning: Optional[str] = None,
        judge_3_recommendation: Optional[str] = None,
        judge_3_model: Optional[str] = None,
    ) -> EvaluationResult:
        """Create a new evaluation result."""
        evaluation_result = EvaluationResult(
            evaluation_round_id=evaluation_round_id,
            scenario_id=scenario_id,
            system_response=system_response,
            final_grade=final_grade,
            confidence_score=confidence_score,
            judge_1_grade=judge_1_grade,
            judge_1_reasoning=judge_1_reasoning,
            judge_1_recommendation=judge_1_recommendation,
            judge_1_model=judge_1_model,
            judge_2_grade=judge_2_grade,
            judge_2_reasoning=judge_2_reasoning,
            judge_2_recommendation=judge_2_recommendation,
            judge_2_model=judge_2_model,
            judge_3_grade=judge_3_grade,
            judge_3_reasoning=judge_3_reasoning,
            judge_3_recommendation=judge_3_recommendation,
            judge_3_model=judge_3_model,
        )
        db.add(evaluation_result)
        db.commit()
        db.refresh(evaluation_result)
        logger.info(f"Created evaluation result: {evaluation_result.id} - Grade: {final_grade}")
        return evaluation_result

    @staticmethod
    def get_by_id(db: Session, result_id: str) -> Optional[EvaluationResult]:
        """Get evaluation result by ID."""
        return db.query(EvaluationResult).filter(EvaluationResult.id == result_id).first()

    @staticmethod
    def get_by_round(db: Session, round_id: str) -> List[EvaluationResult]:
        """Get all evaluation results for a round."""
        return db.query(EvaluationResult).filter(EvaluationResult.evaluation_round_id == round_id).all()

    @staticmethod
    def get_by_scenario(db: Session, scenario_id: str) -> List[EvaluationResult]:
        """Get all evaluation results for a scenario."""
        return db.query(EvaluationResult).filter(EvaluationResult.scenario_id == scenario_id).all()

    @staticmethod
    def get_by_grade(db: Session, round_id: str, grade: str) -> List[EvaluationResult]:
        """Get evaluation results by final grade for a round."""
        return (
            db.query(EvaluationResult)
            .filter(
                EvaluationResult.evaluation_round_id == round_id,
                EvaluationResult.final_grade == grade,
            )
            .all()
        )

    @staticmethod
    def get_stats_by_round(db: Session, round_id: str) -> Dict[str, int]:
        """Get evaluation statistics for a round (count by grade)."""
        results = db.query(EvaluationResult).filter(EvaluationResult.evaluation_round_id == round_id).all()
        
        stats = {
            "total": len(results),
            "PASS": 0,
            "P0": 0,
            "P1": 0,
            "P2": 0,
            "P3": 0,
            "P4": 0,
        }
        
        for result in results:
            if result.final_grade in stats:
                stats[result.final_grade] += 1
        
        return stats

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[EvaluationResult]:
        """Get all evaluation results with pagination."""
        return db.query(EvaluationResult).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, result_id: str, **kwargs) -> Optional[EvaluationResult]:
        """Update evaluation result."""
        evaluation_result = EvaluationResultRepository.get_by_id(db, result_id)
        if not evaluation_result:
            return None

        for key, value in kwargs.items():
            if hasattr(evaluation_result, key):
                setattr(evaluation_result, key, value)

        db.commit()
        db.refresh(evaluation_result)
        logger.info(f"Updated evaluation result: {result_id}")
        return evaluation_result

    @staticmethod
    def delete(db: Session, result_id: str) -> bool:
        """Delete evaluation result by ID."""
        evaluation_result = EvaluationResultRepository.get_by_id(db, result_id)
        if evaluation_result:
            db.delete(evaluation_result)
            db.commit()
            logger.info(f"Deleted evaluation result: {result_id}")
            return True
        return False
