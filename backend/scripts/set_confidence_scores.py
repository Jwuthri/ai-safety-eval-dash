#!/usr/bin/env python3
"""
Script to set confidence scores for evaluation results.

Usage:
    python scripts/set_confidence_scores.py --score 66
    python scripts/set_confidence_scores.py --score 100  # Set all to 100
    python scripts/set_confidence_scores.py --score 66 --round-id <round_id>  # Set for specific round
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.database.models import EvaluationResult
from sqlalchemy import update, func


def set_confidence_scores(score: int, round_id: str = None):
    """Set confidence scores for evaluation results."""
    db = SessionLocal()
    
    try:
        # Build query
        if round_id:
            # Update specific round
            stmt = (
                update(EvaluationResult)
                .where(EvaluationResult.evaluation_round_id == round_id)
                .values(confidence_score=score)
            )
            result = db.execute(stmt)
            db.commit()
            print(f"✅ Updated {result.rowcount} results in round {round_id} to {score}% confidence")
        else:
            # Update all
            stmt = update(EvaluationResult).values(confidence_score=score)
            result = db.execute(stmt)
            db.commit()
            print(f"✅ Updated {result.rowcount} evaluation results to {score}% confidence")
        
        # Show breakdown
        print("\nCurrent confidence score distribution:")
        scores = db.query(
            EvaluationResult.confidence_score,
            func.count(EvaluationResult.id).label('count')
        ).group_by(EvaluationResult.confidence_score).all()
        
        for conf_score, count in scores:
            print(f"  {conf_score}%: {count} results")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Set confidence scores for evaluation results")
    parser.add_argument(
        "--score",
        type=int,
        required=True,
        choices=[33, 66, 100],
        help="Confidence score to set (33, 66, or 100)"
    )
    parser.add_argument(
        "--round-id",
        type=str,
        help="Only update results for this evaluation round"
    )
    
    args = parser.parse_args()
    
    print(f"Setting confidence scores to {args.score}%...")
    if args.round_id:
        print(f"Filtering by round: {args.round_id}")
    
    set_confidence_scores(args.score, args.round_id)


if __name__ == "__main__":
    main()

