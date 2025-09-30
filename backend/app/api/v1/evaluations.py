"""
Evaluation API endpoints.

Handles:
- Starting evaluation rounds
- Getting evaluation results
- Getting round statistics
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ...database import get_db
from ...database.repositories import (
    EvaluationRoundRepository,
    EvaluationResultRepository,
    OrganizationRepository,
)
from ...models.evaluation import (
    EvaluationRoundResponse,
    EvaluationResultResponse,
    EvaluationRoundCreate,
)
from ...services.evaluation_orchestrator import EvaluationOrchestrator

router = APIRouter(prefix="/evaluations", tags=["evaluations"])


@router.post("/rounds", response_model=EvaluationRoundResponse)
async def start_evaluation_round(
    request: EvaluationRoundCreate,
    db: Session = Depends(get_db),
):
    """
    Start a new evaluation round for an organization.
    
    This will:
    1. Create a new evaluation round
    2. Fetch all scenarios for the organization's business type
    3. Run 3 parallel judge evaluations for each scenario
    4. Store all results in the database
    """
    # Verify organization exists
    org = OrganizationRepository.get_by_id(db, request.organization_id)
    if not org:
        raise HTTPException(status_code=404, detail=f"Organization {request.organization_id} not found")
    
    # Start evaluation round
    orchestrator = EvaluationOrchestrator(db)
    round_id = await orchestrator.run_evaluation_round(
        organization_id=request.organization_id,
        round_number=request.round_number,
        description=request.description,
    )
    
    # Get the created round
    evaluation_round = EvaluationRoundRepository.get_by_id(db, round_id)
    return evaluation_round


@router.get("/rounds/{round_id}", response_model=EvaluationRoundResponse)
def get_evaluation_round(
    round_id: str,
    db: Session = Depends(get_db),
):
    """Get details of a specific evaluation round."""
    evaluation_round = EvaluationRoundRepository.get_by_id(db, round_id)
    if not evaluation_round:
        raise HTTPException(status_code=404, detail=f"Evaluation round {round_id} not found")
    
    return evaluation_round


@router.get("/rounds/{round_id}/results", response_model=List[EvaluationResultResponse])
def get_round_results(
    round_id: str,
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """Get all evaluation results for a specific round."""
    # Verify round exists
    evaluation_round = EvaluationRoundRepository.get_by_id(db, round_id)
    if not evaluation_round:
        raise HTTPException(status_code=404, detail=f"Evaluation round {round_id} not found")
    
    # Get results
    results = db.query(EvaluationResultRepository.model).filter_by(
        evaluation_round_id=round_id
    ).offset(offset).limit(limit).all()
    
    return results


@router.get("/rounds/{round_id}/stats")
def get_round_statistics(
    round_id: str,
    db: Session = Depends(get_db),
):
    """
    Get statistics for an evaluation round.
    
    Returns:
    - Total tests
    - Pass count & rate
    - Severity breakdown (PASS, P0-P4)
    """
    # Verify round exists
    evaluation_round = EvaluationRoundRepository.get_by_id(db, round_id)
    if not evaluation_round:
        raise HTTPException(status_code=404, detail=f"Evaluation round {round_id} not found")
    
    # Get stats
    orchestrator = EvaluationOrchestrator(db)
    stats = orchestrator.get_round_statistics(round_id)
    
    return stats


@router.get("/organizations/{organization_id}/rounds", response_model=List[EvaluationRoundResponse])
def list_organization_rounds(
    organization_id: str,
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
):
    """List all evaluation rounds for an organization."""
    # Verify org exists
    org = OrganizationRepository.get_by_id(db, organization_id)
    if not org:
        raise HTTPException(status_code=404, detail=f"Organization {organization_id} not found")
    
    # Get rounds
    rounds = db.query(EvaluationRoundRepository.model).filter_by(
        organization_id=organization_id
    ).order_by(EvaluationRoundRepository.model.started_at.desc()).limit(limit).all()
    
    return rounds


@router.get("/organizations/{organization_id}/latest-round", response_model=Optional[EvaluationRoundResponse])
def get_latest_round(
    organization_id: str,
    db: Session = Depends(get_db),
):
    """Get the latest evaluation round for an organization."""
    round = EvaluationRoundRepository.get_latest_by_organization(db, organization_id)
    if not round:
        return None
    return round
