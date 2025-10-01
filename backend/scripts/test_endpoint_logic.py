#!/usr/bin/env python3
"""Test the endpoint logic directly."""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.database.models import EvaluationResult
from app.database.repositories import HumanReviewRepository

db = SessionLocal()

# Run the same query as the endpoint
query = db.query(EvaluationResult).filter(
    EvaluationResult.confidence_score != None,
    EvaluationResult.confidence_score <= 99
)

results = query.limit(1).all()

print(f"Found {len(results)} results")

if results:
    result = results[0]
    print(f"\nResult details:")
    print(f"  ID: {result.id}")
    print(f"  Confidence: {result.confidence_score}")
    print(f"  Grade: {result.final_grade}")
    print(f"  Created At: {result.created_at}")
    print(f"  Created At Type: {type(result.created_at)}")
    
    # Try to build the response dict
    existing_reviews = HumanReviewRepository.get_by_evaluation_result(db, result.id)
    has_review = len(existing_reviews) > 0
    latest_review = existing_reviews[0] if existing_reviews else None
    
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
    
    print(f"\nBuilt dict successfully:")
    print(json.dumps(item, indent=2))

db.close()

