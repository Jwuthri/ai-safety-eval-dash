"""
Database models package for ai-safety-eval-dash.
"""

from .api_key import ApiKey
from .chat_message import ChatMessage, MessageRoleEnum
from .chat_session import ChatSession
from .completion import Completion
from .task_result import TaskResult
from .user import User, UserStatusEnum

# AI Safety Evaluation Dashboard models
from .evaluation_result import EvaluationResult
from .ai_incident import AIIncident
from .test_taxonomy import TestTaxonomy
from .aiuc_certification import AIUCCertification
from .enums import (
    SeverityLevel,
    TestType,
    CertificationStatus,
    BaseRateFrequency,
    BaseRateSeverity,
    DifficultyLevel
)

__all__ = [
    # Original Models
    "User",
    "ChatSession",
    "ChatMessage",
    "Completion",
    "ApiKey",
    "TaskResult",

    # AI Safety Evaluation Dashboard Models
    "EvaluationResult",
    "AIIncident",
    "TestTaxonomy",
    "AIUCCertification",

    # Original Enums
    "UserStatusEnum",
    "MessageRoleEnum",

    # AI Safety Evaluation Dashboard Enums
    "SeverityLevel",
    "TestType",
    "CertificationStatus",
    "BaseRateFrequency",
    "BaseRateSeverity",
    "DifficultyLevel",
]
