"""
Business Type API endpoints.

Handles listing and retrieving business types.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...database import get_db
from ...database.repositories import BusinessTypeRepository
from ...models.evaluation import BusinessTypeResponse

router = APIRouter(prefix="/business-types", tags=["business-types"])


@router.get("/", response_model=List[BusinessTypeResponse])
def list_business_types(
    db: Session = Depends(get_db),
):
    """
    List all available business types.
    
    Business types are predefined templates for different industries:
    - Airlines Customer Support
    - API Developer Support
    - E-commerce Support
    - etc.
    """
    business_types = BusinessTypeRepository.get_all(db)
    return business_types


@router.get("/{business_type_id}", response_model=BusinessTypeResponse)
def get_business_type(
    business_type_id: str,
    db: Session = Depends(get_db),
):
    """Get a specific business type by ID."""
    business_type = BusinessTypeRepository.get_by_id(db, business_type_id)
    if not business_type:
        raise HTTPException(
            status_code=404, 
            detail=f"Business type {business_type_id} not found"
        )
    
    return business_type


@router.get("/name/{name}", response_model=BusinessTypeResponse)
def get_business_type_by_name(
    name: str,
    db: Session = Depends(get_db),
):
    """Get a specific business type by name."""
    business_type = BusinessTypeRepository.get_by_name(db, name)
    if not business_type:
        raise HTTPException(
            status_code=404, 
            detail=f"Business type '{name}' not found"
        )
    
    return business_type


@router.get("/industry/{industry}", response_model=List[BusinessTypeResponse])
def list_business_types_by_industry(
    industry: str,
    db: Session = Depends(get_db),
):
    """List all business types for a specific industry."""
    business_types = BusinessTypeRepository.get_by_industry(db, industry)
    return business_types
