"""
Organization models.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


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

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={datetime: lambda v: v.isoformat() if v else None},
        json_schema_extra={
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
    )
