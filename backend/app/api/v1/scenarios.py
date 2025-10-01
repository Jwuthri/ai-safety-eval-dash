"""
Scenario API endpoints.

Handles listing test scenarios.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ...database import get_db
from ...database.repositories import ScenarioRepository, BusinessTypeRepository
from ...models.scenario import ScenarioResponse

router = APIRouter(prefix="/scenarios", tags=["scenarios"])


@router.get("/", response_model=List[ScenarioResponse])
def list_scenarios(
    db: Session = Depends(get_db),
    business_type_id: Optional[str] = Query(None, description="Filter by business type"),
    category: Optional[str] = Query(None, description="Filter by category"),
    use_case: Optional[str] = Query(None, description="Filter by use case"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """
    List test scenarios.
    
    Scenarios can be filtered by:
    - business_type_id: Get scenarios for a specific business type
    - category: Filter by attack category (e.g., "SelfHarm", "Fraud")
    - use_case: Filter by use case (e.g., "customer_support", "api_support")
    """
    if business_type_id:
        scenarios = ScenarioRepository.get_by_business_type(db, business_type_id)
    elif category:
        scenarios = ScenarioRepository.get_by_category(db, category)
    elif use_case:
        scenarios = ScenarioRepository.get_by_use_case(db, use_case)
    else:
        scenarios = ScenarioRepository.get_all(db, limit=limit, offset=offset)
    
    return scenarios


@router.get("/{scenario_id}", response_model=ScenarioResponse)
def get_scenario(
    scenario_id: str,
    db: Session = Depends(get_db),
):
    """Get a specific scenario by ID."""
    scenario = ScenarioRepository.get_by_id(db, scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail=f"Scenario {scenario_id} not found")
    
    return scenario


@router.get("/business-types/{business_type_id}/stats")
def get_scenario_stats(
    business_type_id: str,
    db: Session = Depends(get_db),
):
    """
    Get scenario statistics for a business type.
    
    Returns:
    - Total scenarios
    - Breakdown by category
    - Breakdown by use case
    """
    # Verify business type exists
    business_type = BusinessTypeRepository.get_by_id(db, business_type_id)
    if not business_type:
        raise HTTPException(
            status_code=404, 
            detail=f"Business type {business_type_id} not found"
        )
    
    # Get all scenarios
    scenarios = ScenarioRepository.get_by_business_type(db, business_type_id)
    
    # Calculate stats
    categories = {}
    use_cases = {}
    
    for scenario in scenarios:
        # Count by category
        cat = scenario.category or "Uncategorized"
        categories[cat] = categories.get(cat, 0) + 1
        
        # Count by use case
        uc = scenario.use_case or "General"
        use_cases[uc] = use_cases.get(uc, 0) + 1
    
    return {
        "business_type_id": business_type_id,
        "total_scenarios": len(scenarios),
        "by_category": categories,
        "by_use_case": use_cases,
    }
