"""
Evaluation enums.
"""

from enum import Enum


class EvaluationRoundStatusEnum(str, Enum):
    """Evaluation round status."""
    RUNNING = "running"
    COMPLETED = "completed"
    UNDER_REVIEW = "under_review"
    FAILED = "failed"


class ReviewStatusEnum(str, Enum):
    """Human review status."""
    APPROVED = "approved"
    FLAGGED = "flagged"
    NEEDS_IMPROVEMENT = "needs_improvement"


class CertificationStatusEnum(str, Enum):
    """AIUC certification status."""
    PENDING = "pending"
    CERTIFIED = "certified"
    REVOKED = "revoked"


class SeverityGrade(str, Enum):
    """Severity grading scale."""
    PASS = "PASS"
    P4 = "P4"
    P3 = "P3"
    P2 = "P2"
    P1 = "P1"
    P0 = "P0"
    UNK = "UNK"  # Unknown/unparseable grade from precomputed data
