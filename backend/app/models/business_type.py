"""
Business Type models.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


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

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={datetime: lambda v: v.isoformat() if v else None},
        json_schema_extra={
            "example": {
                "id": "biz_123",
                "name": "Airlines Customer Support",
                "industry": "Airlines",
                "use_cases": ["customer_support", "refunds", "booking"],
                "context": "retail_airlines",
                "created_at": "2025-01-01T00:00:00Z"
            }
        }
    )
