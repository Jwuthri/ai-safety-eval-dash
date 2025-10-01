"""
Safeguards API endpoints.

Provides CRUD operations for safeguards and incident-safeguard mappings.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.database.models.safeguard import Safeguard, IncidentSafeguardMapping
from app.database.models.ai_incident import AIIncident

router = APIRouter(prefix="/safeguards", tags=["safeguards"])


@router.get("/", response_model=List[dict])
async def list_safeguards(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get list of all safeguards.
    Filter by category if provided.
    """
    query = db.query(Safeguard)
    
    if category:
        query = query.filter(Safeguard.category == category)
    
    safeguards = query.offset(skip).limit(limit).all()
    
    return [
        {
            "id": s.id,
            "name": s.name,
            "category": s.category,
            "description": s.description,
            "why_it_works": s.why_it_works,
            "implementation_type": s.implementation_type,
            "implementation_details": s.implementation_details,
            "aiuc_requirement": s.aiuc_requirement,
            "compliance_level": s.compliance_level,
            "effectiveness_rating": s.effectiveness_rating,
            "reduces_severity": s.reduces_severity,
            "detection_method": s.detection_method,
            "automated_response": s.automated_response,
            "incident_types": s.incident_types,
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "updated_at": s.updated_at.isoformat() if s.updated_at else None,
        }
        for s in safeguards
    ]


@router.get("/{safeguard_id}", response_model=dict)
async def get_safeguard(
    safeguard_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific safeguard by ID."""
    safeguard = db.query(Safeguard).filter(Safeguard.id == safeguard_id).first()
    
    if not safeguard:
        raise HTTPException(status_code=404, detail="Safeguard not found")
    
    return {
        "id": safeguard.id,
        "name": safeguard.name,
        "category": safeguard.category,
        "description": safeguard.description,
        "why_it_works": safeguard.why_it_works,
        "implementation_type": safeguard.implementation_type,
        "implementation_details": safeguard.implementation_details,
        "aiuc_requirement": safeguard.aiuc_requirement,
        "compliance_level": safeguard.compliance_level,
        "effectiveness_rating": safeguard.effectiveness_rating,
        "reduces_severity": safeguard.reduces_severity,
        "detection_method": safeguard.detection_method,
        "automated_response": safeguard.automated_response,
        "incident_types": safeguard.incident_types,
        "created_at": safeguard.created_at.isoformat() if safeguard.created_at else None,
        "updated_at": safeguard.updated_at.isoformat() if safeguard.updated_at else None,
    }


@router.get("/for-incident/{incident_id}", response_model=List[dict])
async def get_safeguards_for_incident(
    incident_id: str,
    db: Session = Depends(get_db)
):
    """
    Get recommended safeguards for a specific incident.
    Includes priority and effectiveness notes.
    """
    # Get mappings for this incident
    mappings = db.query(
        IncidentSafeguardMapping, Safeguard
    ).join(
        Safeguard,
        IncidentSafeguardMapping.safeguard_id == Safeguard.id
    ).filter(
        IncidentSafeguardMapping.incident_id == incident_id
    ).all()
    
    return [
        {
            "id": safeguard.id,
            "name": safeguard.name,
            "category": safeguard.category,
            "description": safeguard.description,
            "why_it_works": safeguard.why_it_works,
            "implementation_type": safeguard.implementation_type,
            "implementation_details": safeguard.implementation_details,
            "aiuc_requirement": safeguard.aiuc_requirement,
            "compliance_level": safeguard.compliance_level,
            "effectiveness_rating": safeguard.effectiveness_rating,
            "reduces_severity": safeguard.reduces_severity,
            "detection_method": safeguard.detection_method,
            "automated_response": safeguard.automated_response,
            "incident_types": safeguard.incident_types,
            # Mapping-specific fields
            "priority": mapping.priority,
            "effectiveness_note": mapping.effectiveness_note,
        }
        for mapping, safeguard in mappings
    ]


@router.get("/categories/list", response_model=List[dict])
async def list_categories(db: Session = Depends(get_db)):
    """Get list of safeguard categories with counts."""
    from sqlalchemy import func
    
    results = db.query(
        Safeguard.category,
        func.count(Safeguard.id).label('count')
    ).group_by(Safeguard.category).all()
    
    return [
        {
            "category": category,
            "count": count,
            "display_name": category.replace('_', ' ').title()
        }
        for category, count in results
    ]

