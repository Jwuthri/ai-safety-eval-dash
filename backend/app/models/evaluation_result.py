"""
Evaluation Result models.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from .enums import SeverityGrade
from .scenario import ScenarioResponse


class JudgeResponse(BaseModel):
    """Individual judge evaluation response."""
    grade: SeverityGrade = Field(..., description="Severity grade")
    reasoning: str = Field(..., description="Judge reasoning")
    recommendation: Optional[str] = Field(None, description="Improvement recommendation")
    model: str = Field(..., description="LLM model used")


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
    judge_1_recommendation: Optional[str] = Field(None, description="Judge 1 recommendation")
    judge_1_model: str = Field(..., description="Judge 1 model")
    
    judge_2_grade: SeverityGrade = Field(..., description="Judge 2 grade")
    judge_2_reasoning: str = Field(..., description="Judge 2 reasoning")
    judge_2_recommendation: Optional[str] = Field(None, description="Judge 2 recommendation")
    judge_2_model: str = Field(..., description="Judge 2 model")
    
    judge_3_grade: SeverityGrade = Field(..., description="Judge 3 grade")
    judge_3_reasoning: str = Field(..., description="Judge 3 reasoning")
    judge_3_recommendation: Optional[str] = Field(None, description="Judge 3 recommendation")
    judge_3_model: str = Field(..., description="Judge 3 model")
    
    # Nested scenario data
    scenario: Optional[ScenarioResponse] = Field(None, description="Associated scenario details")
    
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True
