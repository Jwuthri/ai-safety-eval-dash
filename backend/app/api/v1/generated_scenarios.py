"""
Generated scenarios API endpoints.

Handles AI-generated test scenario creation and retrieval.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ...database import get_db
from ...database.repositories import OrganizationRepository
from ...models.generated_scenario import (
    GeneratedScenarioResponse,
    GenerateScenarioRequest,
    GenerateScenarioResponse,
)
from ...services.scenario_generation_service import ScenarioGenerationService
from ...config import Settings, get_settings

router = APIRouter(prefix="/generated-scenarios", tags=["generated-scenarios"])


def get_scenario_service(settings: Settings = Depends(get_settings)) -> ScenarioGenerationService:
    """Dependency to get scenario generation service."""
    service = ScenarioGenerationService(settings)
    return service


@router.post("/generate", response_model=GenerateScenarioResponse, status_code=201)
async def generate_scenarios(
    request: GenerateScenarioRequest,
    db: Session = Depends(get_db),
    service: ScenarioGenerationService = Depends(get_scenario_service),
):
    """
    Generate AI-powered test scenarios for an organization.
    
    This endpoint uses an AI agent to automatically create ~20 diverse test scenarios
    based on the organization's business type and context.
    """
    # Verify organization exists
    org = OrganizationRepository.get_by_id(db, request.organization_id)
    if not org:
        raise HTTPException(
            status_code=404,
            detail=f"Organization {request.organization_id} not found"
        )

    # Initialize service
    await service.initialize()

    # Generate scenarios
    scenarios = await service.generate_scenarios_for_org(
        db=db,
        organization_id=request.organization_id,
        count=request.count
    )

    return GenerateScenarioResponse(
        organization_id=request.organization_id,
        scenarios_generated=len(scenarios),
        scenarios=scenarios
    )


@router.get("/organization/{organization_id}", response_model=List[GeneratedScenarioResponse])
def get_organization_scenarios(
    organization_id: str,
    db: Session = Depends(get_db),
    service: ScenarioGenerationService = Depends(get_scenario_service),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """
    Get all generated scenarios for an organization.
    
    Returns scenarios in reverse chronological order (newest first).
    """
    # Verify organization exists
    org = OrganizationRepository.get_by_id(db, organization_id)
    if not org:
        raise HTTPException(
            status_code=404,
            detail=f"Organization {organization_id} not found"
        )

    scenarios = service.get_scenarios_for_org(
        db=db,
        organization_id=organization_id,
        limit=limit,
        offset=offset
    )

    return scenarios


@router.get("/organization/{organization_id}/count")
def count_organization_scenarios(
    organization_id: str,
    db: Session = Depends(get_db),
    service: ScenarioGenerationService = Depends(get_scenario_service),
):
    """Get count of generated scenarios for an organization."""
    # Verify organization exists
    org = OrganizationRepository.get_by_id(db, organization_id)
    if not org:
        raise HTTPException(
            status_code=404,
            detail=f"Organization {organization_id} not found"
        )

    count = service.count_scenarios_for_org(db, organization_id)
    return {"organization_id": organization_id, "count": count}


@router.delete("/organization/{organization_id}")
def delete_organization_scenarios(
    organization_id: str,
    db: Session = Depends(get_db),
    service: ScenarioGenerationService = Depends(get_scenario_service),
):
    """Delete all generated scenarios for an organization."""
    # Verify organization exists
    org = OrganizationRepository.get_by_id(db, organization_id)
    if not org:
        raise HTTPException(
            status_code=404,
            detail=f"Organization {organization_id} not found"
        )

    count = service.delete_scenarios_for_org(db, organization_id)
    return {
        "organization_id": organization_id,
        "deleted_count": count,
        "message": f"Deleted {count} generated scenarios"
    }

