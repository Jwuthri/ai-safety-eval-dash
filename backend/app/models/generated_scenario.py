"""
Generated scenario models for API.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class GeneratedScenarioBase(BaseModel):
    """Base generated scenario model."""
    category: Optional[str] = Field(None, description="Attack category")
    sub_category: Optional[str] = Field(None, description="Attack sub-category")
    input_topic: Optional[str] = Field(None, description="Input topic")
    methodology: Optional[str] = Field(None, description="Attack methodology")
    input_prompt: str = Field(..., description="Test prompt")
    expected_behavior: Optional[str] = Field(None, description="Expected safe response")
    tactics: List[str] = Field(default_factory=list, description="Attack tactics")
    use_case: Optional[str] = Field(None, description="Use case")
    incident_reference: Optional[str] = Field(None, description="Real-world incident reference")


class GeneratedScenarioCreate(GeneratedScenarioBase):
    """Generated scenario creation model (used by agent)."""
    organization_id: str = Field(..., description="Organization ID")
    business_type_id: str = Field(..., description="Business type ID")
    generation_prompt: Optional[str] = Field(None, description="Prompt used to generate")
    model_used: Optional[str] = Field(None, description="Model that generated this")


class GeneratedScenarioResponse(GeneratedScenarioBase):
    """Generated scenario response model."""
    id: str = Field(..., description="Scenario ID")
    organization_id: str = Field(..., description="Organization ID")
    business_type_id: str = Field(..., description="Business type ID")
    generation_prompt: Optional[str] = Field(None, description="Prompt used to generate")
    model_used: Optional[str] = Field(None, description="Model that generated this")
    created_at: datetime = Field(..., description="Creation timestamp")

    model_config = ConfigDict(from_attributes=True)


class GenerateScenarioRequest(BaseModel):
    """Request to generate scenarios for an organization."""
    organization_id: str = Field(..., description="Organization ID to generate scenarios for")
    count: int = Field(20, description="Number of scenarios to generate", ge=1, le=50)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "organization_id": "123e4567-e89b-12d3-a456-426614174000",
                "count": 20
            }
        }
    )


class GenerateScenarioResponse(BaseModel):
    """Response after generating scenarios."""
    organization_id: str = Field(..., description="Organization ID")
    scenarios_generated: int = Field(..., description="Number of scenarios generated")
    scenarios: List[GeneratedScenarioResponse] = Field(..., description="Generated scenarios")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "organization_id": "123e4567-e89b-12d3-a456-426614174000",
                "scenarios_generated": 20,
                "scenarios": []
            }
        }
    )

