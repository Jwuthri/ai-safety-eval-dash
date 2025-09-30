"""
Pydantic models for AI Safety Evaluation API.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


# Enums
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


# Business Type Models (Predefined Templates)
class BusinessTypeBase(BaseModel):
    """Base business type model."""
    name: str = Field(..., description="Business type name", max_length=255)
    industry: Optional[str] = Field(None, description="Industry sector")
    use_cases: List[str] = Field(default_factory=list, description="Use cases")
    context: Optional[str] = Field(None, description="Business context")


class BusinessTypeCreate(BusinessTypeBase):
    """Business type creation model."""
    pass


class BusinessTypeResponse(BusinessTypeBase):
    """Business type response model."""
    id: str = Field(..., description="Business type ID")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "biz_123",
                "name": "Airlines Customer Support",
                "industry": "Airlines",
                "use_cases": ["customer_support", "refunds", "booking"],
                "context": "retail_airlines",
                "created_at": "2025-01-01T00:00:00Z"
            }
        }


# Organization Models
class OrganizationBase(BaseModel):
    """Base organization model."""
    name: str = Field(..., description="Organization name", max_length=255)
    slug: str = Field(..., description="URL-friendly slug", max_length=100)
    contact_email: Optional[str] = Field(None, description="Contact email")
    contact_name: Optional[str] = Field(None, description="Contact person name")
    is_active: bool = Field(True, description="Organization status")


class OrganizationCreate(OrganizationBase):
    """Organization creation model."""
    business_type_id: str = Field(..., description="Business type ID they belong to")


class OrganizationUpdate(BaseModel):
    """Organization update model."""
    name: Optional[str] = Field(None, description="Organization name", max_length=255)
    contact_email: Optional[str] = Field(None, description="Contact email")
    contact_name: Optional[str] = Field(None, description="Contact person name")
    is_active: Optional[bool] = Field(None, description="Organization status")


class OrganizationResponse(OrganizationBase):
    """Organization response model."""
    id: str = Field(..., description="Organization ID")
    business_type_id: str = Field(..., description="Business type ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "org_123",
                "business_type_id": "biz_123",
                "name": "AirCanada Corp",
                "slug": "aircanada",
                "contact_email": "safety@aircanada.com",
                "contact_name": "John Doe",
                "is_active": True,
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T00:00:00Z"
            }
        }


# Scenario Models
class ScenarioBase(BaseModel):
    """Base scenario model."""
    category: Optional[str] = Field(None, description="Attack category")
    sub_category: Optional[str] = Field(None, description="Attack sub-category")
    input_topic: Optional[str] = Field(None, description="Input topic")
    methodology: Optional[str] = Field(None, description="Attack methodology")
    input_prompt: str = Field(..., description="Test prompt")
    expected_behavior: Optional[str] = Field(None, description="Expected safe response")
    tactics: List[str] = Field(default_factory=list, description="Attack tactics")
    use_case: Optional[str] = Field(None, description="Use case")
    incident_reference: Optional[str] = Field(None, description="Real-world incident reference")


class ScenarioCreate(ScenarioBase):
    """Scenario creation model."""
    business_type_id: str = Field(..., description="Business type ID")


class ScenarioResponse(ScenarioBase):
    """Scenario response model."""
    id: str = Field(..., description="Scenario ID")
    business_type_id: str = Field(..., description="Business type ID")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True


# Evaluation Round Models
class EvaluationRoundCreate(BaseModel):
    """Evaluation round creation model."""
    organization_id: str = Field(..., description="Organization ID being evaluated")
    round_number: int = Field(..., description="Round number", ge=1)
    description: Optional[str] = Field(None, description="Round description")

    class Config:
        json_schema_extra = {
            "example": {
                "organization_id": "org_123",
                "round_number": 1,
                "description": "Initial safety evaluation"
            }
        }


class EvaluationRoundResponse(BaseModel):
    """Evaluation round response model."""
    id: str = Field(..., description="Round ID")
    organization_id: str = Field(..., description="Organization ID")
    round_number: int = Field(..., description="Round number")
    description: Optional[str] = Field(None, description="Round description")
    status: EvaluationRoundStatusEnum = Field(..., description="Round status")
    started_at: datetime = Field(..., description="Start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "round_123",
                "organization_id": "org_123",
                "round_number": 1,
                "description": "Initial safety evaluation",
                "status": "running",
                "started_at": "2025-01-01T00:00:00Z",
                "completed_at": None
            }
        }


# Judge Response Model
class JudgeResponse(BaseModel):
    """Individual judge evaluation response."""
    grade: SeverityGrade = Field(..., description="Severity grade")
    reasoning: str = Field(..., description="Judge reasoning")
    recommendation: Optional[str] = Field(None, description="Improvement recommendation")
    model: str = Field(..., description="LLM model used")


# Evaluation Result Models
class EvaluationResultCreate(BaseModel):
    """Evaluation result creation model."""
    evaluation_round_id: str = Field(..., description="Evaluation round ID")
    scenario_id: str = Field(..., description="Scenario ID")
    system_response: str = Field(..., description="System under test response")
    final_grade: SeverityGrade = Field(..., description="Final aggregated grade")
    judge_1: JudgeResponse = Field(..., description="Judge 1 (Claude) response")
    judge_2: JudgeResponse = Field(..., description="Judge 2 (GPT-4.1) response")
    judge_3: JudgeResponse = Field(..., description="Judge 3 (Grok) response")


class EvaluationResultResponse(BaseModel):
    """Evaluation result response model."""
    id: str = Field(..., description="Result ID")
    evaluation_round_id: str = Field(..., description="Evaluation round ID")
    scenario_id: str = Field(..., description="Scenario ID")
    system_response: str = Field(..., description="System response")
    final_grade: SeverityGrade = Field(..., description="Final grade")
    
    # Judge responses
    judge_1_grade: SeverityGrade = Field(..., description="Judge 1 grade")
    judge_1_reasoning: str = Field(..., description="Judge 1 reasoning")
    judge_1_model: str = Field(..., description="Judge 1 model")
    
    judge_2_grade: SeverityGrade = Field(..., description="Judge 2 grade")
    judge_2_reasoning: str = Field(..., description="Judge 2 reasoning")
    judge_2_model: str = Field(..., description="Judge 2 model")
    
    judge_3_grade: SeverityGrade = Field(..., description="Judge 3 grade")
    judge_3_reasoning: str = Field(..., description="Judge 3 reasoning")
    judge_3_model: str = Field(..., description="Judge 3 model")
    
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True


# Round Summary Model
class RoundSummary(BaseModel):
    """Evaluation round summary statistics."""
    round_id: str = Field(..., description="Round ID")
    total_tests: int = Field(..., description="Total test count")
    pass_count: int = Field(..., description="Passed tests")
    pass_rate: float = Field(..., description="Pass rate percentage")
    severity_breakdown: dict = Field(..., description="Count by severity")

    class Config:
        json_schema_extra = {
            "example": {
                "round_id": "round_123",
                "total_tests": 303,
                "pass_count": 236,
                "pass_rate": 77.9,
                "severity_breakdown": {
                    "PASS": 236,
                    "P4": 29,
                    "P3": 33,
                    "P2": 5,
                    "P1": 0,
                    "P0": 0
                }
            }
        }


# Human Review Models
class HumanReviewCreate(BaseModel):
    """Human review creation model."""
    evaluation_result_id: str = Field(..., description="Result ID")
    reviewer_id: Optional[str] = Field(None, description="Reviewer ID")
    review_status: ReviewStatusEnum = Field(..., description="Review status")
    override_grade: Optional[SeverityGrade] = Field(None, description="Grade override")
    comments: Optional[str] = Field(None, description="Review comments")

    class Config:
        json_schema_extra = {
            "example": {
                "evaluation_result_id": "result_123",
                "reviewer_id": "user_456",
                "review_status": "needs_improvement",
                "override_grade": "P2",
                "comments": "Judge marked as PASS but response still shows compliance"
            }
        }


class HumanReviewResponse(BaseModel):
    """Human review response model."""
    id: str = Field(..., description="Review ID")
    evaluation_result_id: str = Field(..., description="Result ID")
    reviewer_id: Optional[str] = Field(None, description="Reviewer ID")
    review_status: ReviewStatusEnum = Field(..., description="Review status")
    override_grade: Optional[SeverityGrade] = Field(None, description="Grade override")
    comments: Optional[str] = Field(None, description="Comments")
    reviewed_at: datetime = Field(..., description="Review timestamp")

    class Config:
        from_attributes = True


# Certification Models
class CertificationCheck(BaseModel):
    """Certification eligibility check result."""
    eligible: bool = Field(..., description="Eligible for certification")
    level: str = Field(..., description="Certification level")
    message: str = Field(..., description="Status message")
    blockers: List[str] = Field(default_factory=list, description="Blocking issues")

    class Config:
        json_schema_extra = {
            "example": {
                "eligible": False,
                "level": "Near Certification",
                "message": "Only minor issues remaining. 5 P3 and 2 P4 to resolve.",
                "blockers": []
            }
        }


class CertificationCreate(BaseModel):
    """Certification issuance request."""
    organization_id: str = Field(..., description="Organization ID")
    evaluation_round_id: str = Field(..., description="Evaluation round ID")


# Alias for backwards compatibility
CertificationIssue = CertificationCreate


class CertificationResponse(BaseModel):
    """AIUC certification response."""
    id: str = Field(..., description="Certificate ID")
    organization_id: str = Field(..., description="Organization ID")
    evaluation_round_id: str = Field(..., description="Evaluation round ID")
    certification_status: CertificationStatusEnum = Field(..., description="Status")
    issued_at: Optional[datetime] = Field(None, description="Issue timestamp")
    expires_at: Optional[datetime] = Field(None, description="Expiry timestamp")
    final_pass_rate: Optional[Decimal] = Field(None, description="Final pass rate")
    p2_count: int = Field(..., description="P2 count")
    p3_count: int = Field(..., description="P3 count")
    p4_count: int = Field(..., description="P4 count")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "AIUC-1-2025-001",
                "organization_id": "org_123",
                "evaluation_round_id": "round_456",
                "certification_status": "certified",
                "issued_at": "2025-01-01T12:00:00Z",
                "expires_at": "2026-01-01T12:00:00Z",
                "final_pass_rate": 97.4,
                "p2_count": 0,
                "p3_count": 0,
                "p4_count": 0
            }
        }
