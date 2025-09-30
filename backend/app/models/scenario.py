"""
Scenario models.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


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
