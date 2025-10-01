"""
AI Incidents API endpoints.

Handles:
- CRUD operations for real-world AI failures
- Mapping incidents to scenarios/tests
- Statistics and breakdowns
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ...database import get_db
from ...database.repositories import AIIncidentRepository, BusinessTypeRepository
from ...models.ai_incident import (
    AIIncidentCreate,
    AIIncidentUpdate,
    AIIncidentResponse,
)

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.post("/", response_model=AIIncidentResponse, status_code=201)
def create_incident(
    request: AIIncidentCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new AI Incident.
    
    Track real-world AI failures (like AirCanada) to map to preventive tests.
    """
    # Verify business type exists if provided
    if request.business_type_id:
        business_type = BusinessTypeRepository.get_by_id(db, request.business_type_id)
        if not business_type:
            raise HTTPException(
                status_code=404,
                detail=f"Business type {request.business_type_id} not found"
            )
    
    # Check if incident_reference already exists
    if request.incident_reference:
        existing = AIIncidentRepository.get_by_reference(db, request.incident_reference)
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Incident with reference '{request.incident_reference}' already exists"
            )
    
    # Create incident
    incident = AIIncidentRepository.create(db, **request.model_dump())
    return incident


@router.get("/", response_model=List[AIIncidentResponse])
def list_incidents(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    severity: Optional[str] = Query(None, description="Filter by severity (P0-P4)"),
    harm_type: Optional[str] = Query(None, description="Filter by harm type"),
    company: Optional[str] = Query(None, description="Filter by company name (fuzzy)"),
    business_type_id: Optional[str] = Query(None, description="Filter by business type"),
):
    """
    List all AI incidents with optional filters.
    
    For safety story dashboard: Show buyers what can go wrong.
    """
    incidents = AIIncidentRepository.list_all(
        db,
        skip=skip,
        limit=limit,
        severity=severity,
        harm_type=harm_type,
        company=company,
        business_type_id=business_type_id,
    )
    return incidents


@router.get("/stats/severity")
def get_severity_stats(
    db: Session = Depends(get_db),
    business_type_id: Optional[str] = Query(None, description="Filter by business type"),
):
    """Get incident count breakdown by severity level."""
    stats = AIIncidentRepository.count_by_severity(db, business_type_id)
    return {
        "severity_breakdown": stats,
        "total_incidents": sum(stats.values())
    }


@router.get("/stats/harm-types")
def get_harm_type_stats(
    db: Session = Depends(get_db),
    business_type_id: Optional[str] = Query(None, description="Filter by business type"),
):
    """Get incident count breakdown by harm type."""
    stats = AIIncidentRepository.count_by_harm_type(db, business_type_id)
    return {
        "harm_type_breakdown": stats,
        "total_incidents": sum(stats.values())
    }


@router.get("/{incident_id}", response_model=AIIncidentResponse)
def get_incident(
    incident_id: str,
    db: Session = Depends(get_db),
):
    """Get a specific AI incident by ID."""
    incident = AIIncidentRepository.get_by_id(db, incident_id)
    if not incident:
        raise HTTPException(
            status_code=404,
            detail=f"Incident {incident_id} not found"
        )
    
    return incident


@router.patch("/{incident_id}", response_model=AIIncidentResponse)
def update_incident(
    incident_id: str,
    request: AIIncidentUpdate,
    db: Session = Depends(get_db),
):
    """Update an existing AI incident."""
    # Verify business type exists if being updated
    if request.business_type_id:
        business_type = BusinessTypeRepository.get_by_id(db, request.business_type_id)
        if not business_type:
            raise HTTPException(
                status_code=404,
                detail=f"Business type {request.business_type_id} not found"
            )
    
    # Update incident
    incident = AIIncidentRepository.update(
        db,
        incident_id,
        **request.model_dump(exclude_unset=True)
    )
    
    if not incident:
        raise HTTPException(
            status_code=404,
            detail=f"Incident {incident_id} not found"
        )
    
    return incident


@router.delete("/{incident_id}", status_code=204)
def delete_incident(
    incident_id: str,
    db: Session = Depends(get_db),
):
    """Delete an AI incident."""
    success = AIIncidentRepository.delete(db, incident_id)
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Incident {incident_id} not found"
        )
    
    return None

