"""
Human Review API endpoints.

Handles:
- Getting low-confidence results that need review
- Submitting human reviews
- Updating evaluation results with human grades
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from ...database import get_db
from ...database.models.evaluation_result import EvaluationResult
from ...database.repositories import (
    EvaluationResultRepository,
    HumanReviewRepository,
)
from ...models.human_review import (
    HumanReviewCreate,
    HumanReviewResponse,
    LowConfidenceResult,
)
from ...utils.logging import get_logger

logger = get_logger("human_reviews_api")

router = APIRouter(prefix="/human-reviews", tags=["human-reviews"])


@router.get("/low-confidence")
def get_low_confidence_results(
    db: Session = Depends(get_db),
    round_id: str = Query(None, description="Filter by evaluation round"),
    min_confidence: int = Query(99, description="Get results with confidence <= this value"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """
    Get evaluation results with low confidence that need human review.
    
    Returns results where confidence_score < 100% (judges disagreed).
    """
    # Filter for results with confidence score present and <= min_confidence
    query = db.query(EvaluationResult).filter(
        EvaluationResult.confidence_score != None,
        EvaluationResult.confidence_score <= min_confidence
    )
    
    if round_id:
        query = query.filter(EvaluationResult.evaluation_round_id == round_id)
    
    results = query.offset(offset).limit(limit).all()
    
    logger.info(f"Found {len(results)} low-confidence results (confidence <= {min_confidence})")
    
    # Build response with human review status
    low_confidence_results = []
    for result in results:
        # Check if already reviewed (returns a list!)
        existing_reviews = HumanReviewRepository.get_by_evaluation_result(db, result.id)
        has_review = len(existing_reviews) > 0
        latest_review = existing_reviews[0] if existing_reviews else None
        
        # Build the response dict manually to ensure proper serialization
        item = {
            "id": result.id,
            "evaluation_round_id": result.evaluation_round_id,
            "scenario_id": result.scenario_id,
            "final_grade": result.final_grade,
            "confidence_score": result.confidence_score or 0,
            "judge_1_grade": result.judge_1_grade,
            "judge_2_grade": result.judge_2_grade,
            "judge_3_grade": result.judge_3_grade,
            "has_human_review": has_review,
            "human_review": None,
            "created_at": result.created_at.isoformat() if result.created_at else None,
        }
        
        if latest_review:
            item["human_review"] = {
                "id": latest_review.id,
                "evaluation_result_id": latest_review.evaluation_result_id,
                "reviewer_id": latest_review.reviewer_id,
                "reviewer_name": latest_review.reviewer_name,
                "original_grade": latest_review.original_grade,
                "original_confidence": latest_review.original_confidence,
                "reviewed_grade": latest_review.reviewed_grade,
                "review_notes": latest_review.review_notes,
                "reviewed_at": latest_review.reviewed_at.isoformat() if latest_review.reviewed_at else None,
            }
        
        low_confidence_results.append(item)
    
    return low_confidence_results


@router.post("/", response_model=HumanReviewResponse, status_code=201)
def create_human_review(
    request: HumanReviewCreate,
    db: Session = Depends(get_db),
):
    """
    Create a human review for a low-confidence evaluation result.
    
    This will:
    1. Store the human review
    2. Update the evaluation result with the human's grade
    3. Set confidence to 100% (human-verified)
    """
    # Verify evaluation result exists
    eval_result = EvaluationResultRepository.get_by_id(db, request.evaluation_result_id)
    if not eval_result:
        raise HTTPException(
            status_code=404,
            detail=f"Evaluation result {request.evaluation_result_id} not found"
        )
    
    # Check if already reviewed
    existing_review = HumanReviewRepository.get_by_evaluation_result(
        db, request.evaluation_result_id
    )
    if existing_review:
        raise HTTPException(
            status_code=400,
            detail=f"Evaluation result {request.evaluation_result_id} already has a human review"
        )
    
    # Create human review
    review = HumanReviewRepository.create(
        db,
        evaluation_result_id=request.evaluation_result_id,
        original_grade=eval_result.final_grade,
        original_confidence=eval_result.confidence_score or 0,
        reviewed_grade=request.reviewed_grade,
        reviewer_id=request.reviewer_id,
        reviewer_name=request.reviewer_name,
        review_notes=request.review_notes,
    )
    
    # Update evaluation result with human grade
    EvaluationResultRepository.update(
        db,
        request.evaluation_result_id,
        final_grade=request.reviewed_grade,
        confidence_score=100,  # Human verified = 100% confidence
    )
    
    logger.info(
        f"Human review created: {review.id} - "
        f"{eval_result.final_grade} → {request.reviewed_grade} "
        f"by {request.reviewer_name or 'Unknown'}"
    )
    
    return review


@router.get("/round/{round_id}", response_model=List[HumanReviewResponse])
def get_round_reviews(
    round_id: str,
    db: Session = Depends(get_db),
):
    """Get all human reviews for a specific evaluation round."""
    reviews = HumanReviewRepository.get_by_round(db, round_id)
    return reviews


@router.get("/{review_id}", response_model=HumanReviewResponse)
def get_review(
    review_id: str,
    db: Session = Depends(get_db),
):
    """Get a specific human review by ID."""
    review = HumanReviewRepository.get_by_id(db, review_id)
    if not review:
        raise HTTPException(status_code=404, detail=f"Human review {review_id} not found")
    return review

