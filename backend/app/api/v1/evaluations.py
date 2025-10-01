"""
Evaluation API endpoints.

Handles:
- Starting evaluation rounds
- Getting evaluation results
- Getting round statistics
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from ...database import get_db
from ...utils.logging import get_logger

logger = get_logger("evaluations_api")
from ...database.models import EvaluationRound, EvaluationResult
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
    from sqlalchemy.orm import joinedload
    
    # Verify round exists
    evaluation_round = EvaluationRoundRepository.get_by_id(db, round_id)
    if not evaluation_round:
        raise HTTPException(status_code=404, detail=f"Evaluation round {round_id} not found")
    
    # Get results with scenario data eager-loaded
    results = db.query(EvaluationResult).options(
        joinedload(EvaluationResult.scenario)
    ).filter_by(
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
    rounds = db.query(EvaluationRound).filter_by(
        organization_id=organization_id
    ).order_by(EvaluationRound.started_at.desc()).limit(limit).all()
    
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


@router.post("/run")
async def run_evaluation(
    organization_id: str,
    round_number: int,
    description: Optional[str] = None,
    use_fake_judges: bool = True,
    session_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Run a new evaluation round for an organization.
    
    Args:
        organization_id: The organization to evaluate
        round_number: The round number for this evaluation
        description: Optional description of this round
        use_fake_judges: If True, use fake judge responses (free, for demos). If False, use real LLM APIs.
        session_id: Optional session ID for WebSocket progress tracking
    
    Returns:
        round_id: The ID of the created evaluation round
        message: Success message
        session_id: Session ID for WebSocket connection (if provided)
    """
    # Verify organization exists
    org = OrganizationRepository.get_by_id(db, organization_id)
    if not org:
        raise HTTPException(status_code=404, detail=f"Organization {organization_id} not found")
    
    # Note: WebSocket connection will be established separately
    # The orchestrator will send updates if a WebSocket is connected with the session_id
    orchestrator = EvaluationOrchestrator(
        db, 
        show_progress=False,  # Don't show progress in API mode
        use_fake_judges=use_fake_judges
    )
    round_id = await orchestrator.run_evaluation_round(
        organization_id=organization_id,
        round_number=round_number,
        description=description,
    )
    
    response = {
        "round_id": round_id,
        "message": f"Evaluation round {round_number} completed successfully",
        "use_fake_judges": use_fake_judges
    }
    
    if session_id:
        response["session_id"] = session_id
    
    return response


@router.websocket("/ws/run")
async def run_evaluation_websocket(websocket: WebSocket):
    """
    WebSocket endpoint to run evaluation with real-time progress updates.
    
    Client sends:
    {
        "organization_id": "uuid",
        "round_number": 1,
        "description": "optional",
        "use_fake_judges": true
    }
    
    Server sends progress updates:
    {
        "type": "progress",
        "current": 3,
        "total": 15,
        "percentage": 20.0,
        "current_scenario": "Data Leakage",
        "current_grade": "PASS",
        "status": "evaluating|completed"
    }
    
    Final message:
    {
        "type": "complete",
        "round_id": "uuid",
        "total": 15,
        "message": "Evaluation round completed successfully"
    }
    """
    await websocket.accept()
    logger.info("WebSocket connection established for evaluation")
    
    try:
        # Receive evaluation request from client
        data = await websocket.receive_json()
        
        organization_id = data.get("organization_id")
        round_number = data.get("round_number")
        description = data.get("description")
        use_fake_judges = data.get("use_fake_judges", True)
        
        if not organization_id or not round_number:
            await websocket.send_json({
                "type": "error",
                "message": "Missing required fields: organization_id and round_number"
            })
            await websocket.close()
            return
        
        # Create new DB session for this WebSocket connection
        from ...database import SessionLocal
        db = SessionLocal()
        
        try:
            # Verify organization exists
            org = OrganizationRepository.get_by_id(db, organization_id)
            if not org:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Organization {organization_id} not found"
                })
                await websocket.close()
                return
            
            # Send start confirmation
            await websocket.send_json({
                "type": "started",
                "organization_id": organization_id,
                "round_number": round_number,
                "use_fake_judges": use_fake_judges
            })
            
            # Run evaluation with WebSocket progress
            orchestrator = EvaluationOrchestrator(
                db, 
                show_progress=False,
                use_fake_judges=use_fake_judges,
                websocket=websocket
            )
            
            round_id = await orchestrator.run_evaluation_round(
                organization_id=organization_id,
                round_number=round_number,
                description=description,
            )
            
            logger.info(f"Evaluation round {round_id} completed via WebSocket")
            
        finally:
            db.close()
                
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected during evaluation")
    except Exception as e:
        logger.error(f"WebSocket evaluation error: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"Evaluation failed: {str(e)}"
            })
        except:
            pass
        await websocket.close()
