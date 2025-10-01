"""
Organization API endpoints.

Handles CRUD operations for organizations.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ...database import get_db
from ...database.repositories import OrganizationRepository, BusinessTypeRepository
from ...models.organization import (
    OrganizationResponse,
    OrganizationCreate,
    OrganizationUpdate,
)

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.post("/", response_model=OrganizationResponse, status_code=201)
def create_organization(
    request: OrganizationCreate,
    db: Session = Depends(get_db),
):
    """Create a new organization."""
    # Verify business type exists
    business_type = BusinessTypeRepository.get_by_id(db, request.business_type_id)
    if not business_type:
        raise HTTPException(
            status_code=404, 
            detail=f"Business type {request.business_type_id} not found"
        )
    
    # Check if org with same name or slug exists
    existing = OrganizationRepository.get_by_slug(db, request.slug)
    if existing:
        raise HTTPException(
            status_code=400, 
            detail=f"Organization with slug '{request.slug}' already exists"
        )
    
    # Create organization
    org = OrganizationRepository.create(
        db,
        business_type_id=request.business_type_id,
        name=request.name,
        slug=request.slug,
        contact_email=request.contact_email,
        contact_name=request.contact_name,
    )
    
    return org


@router.get("/", response_model=List[OrganizationResponse])
def list_organizations(
    db: Session = Depends(get_db),
    business_type_id: str = Query(None, description="Filter by business type"),
    is_active: bool = Query(None, description="Filter by active status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """List all organizations."""
    if business_type_id:
        orgs = OrganizationRepository.get_by_business_type(db, business_type_id)
    else:
        orgs = OrganizationRepository.get_all(db, limit=limit, offset=offset)
    
    # Filter by active status if provided
    if is_active is not None:
        orgs = [org for org in orgs if org.is_active == is_active]
    
    return orgs


@router.get("/{organization_id}", response_model=OrganizationResponse)
def get_organization(
    organization_id: str,
    db: Session = Depends(get_db),
):
    """Get a specific organization by ID."""
    org = OrganizationRepository.get_by_id(db, organization_id)
    if not org:
        raise HTTPException(status_code=404, detail=f"Organization {organization_id} not found")
    
    return org


@router.get("/slug/{slug}", response_model=OrganizationResponse)
def get_organization_by_slug(
    slug: str,
    db: Session = Depends(get_db),
):
    """Get a specific organization by slug."""
    org = OrganizationRepository.get_by_slug(db, slug)
    if not org:
        raise HTTPException(status_code=404, detail=f"Organization with slug '{slug}' not found")
    
    return org


@router.patch("/{organization_id}", response_model=OrganizationResponse)
def update_organization(
    organization_id: str,
    request: OrganizationUpdate,
    db: Session = Depends(get_db),
):
    """Update an organization."""
    org = OrganizationRepository.get_by_id(db, organization_id)
    if not org:
        raise HTTPException(status_code=404, detail=f"Organization {organization_id} not found")
    
    # Update fields
    update_data = request.dict(exclude_unset=True)
    updated_org = OrganizationRepository.update(db, organization_id, **update_data)
    
    return updated_org


@router.delete("/{organization_id}", status_code=204)
def deactivate_organization(
    organization_id: str,
    db: Session = Depends(get_db),
):
    """Deactivate an organization (soft delete)."""
    org = OrganizationRepository.get_by_id(db, organization_id)
    if not org:
        raise HTTPException(status_code=404, detail=f"Organization {organization_id} not found")
    
    OrganizationRepository.deactivate(db, organization_id)
    return None
