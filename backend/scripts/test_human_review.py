#!/usr/bin/env python3
"""Quick test to verify human review data."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.database.models import EvaluationResult
from sqlalchemy import func

db = SessionLocal()

# Count results by confidence score
print("Confidence Score Distribution:")
results = db.query(
    EvaluationResult.confidence_score,
    func.count(EvaluationResult.id).label('count')
).group_by(EvaluationResult.confidence_score).all()

for score, count in results:
    print(f"  {score}%: {count} results")

# Get a few samples
print("\nSample low-confidence results:")
samples = db.query(EvaluationResult).filter(
    EvaluationResult.confidence_score != None,
    EvaluationResult.confidence_score < 100
).limit(3).all()

for r in samples:
    print(f"  ID: {r.id[:8]}... | Grade: {r.final_grade} | Confidence: {r.confidence_score}% | Judges: {r.judge_1_grade}/{r.judge_2_grade}/{r.judge_3_grade}")

db.close()

