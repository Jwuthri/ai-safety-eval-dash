"""
AIUC Certification API endpoints.

Handles:
- Checking certification eligibility
- Issuing certifications
- Revoking certifications
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ...database import get_db
from ...database.repositories import (
    AiucCertificationRepository,
    EvaluationRoundRepository,
    EvaluationResultRepository,
    OrganizationRepository,
)
from ...models.evaluation import (
    CertificationResponse,
    CertificationCreate,
)

router = APIRouter(prefix="/certifications", tags=["certifications"])


@router.post("/", response_model=CertificationResponse, status_code=201)
def issue_certification(
    request: CertificationCreate,
    db: Session = Depends(get_db),
):
    """
    Issue an AIUC-1 certification to an organization.
    
    Requirements:
    - Evaluation round must be completed
    - Zero P0, P1, P2, P3, P4 errors
    - Pass rate must be 100%
    """
    # Verify organization exists
    org = OrganizationRepository.get_by_id(db, request.organization_id)
    if not org:
        raise HTTPException(
            status_code=404, 
            detail=f"Organization {request.organization_id} not found"
        )
    
    # Verify evaluation round exists and is completed
    eval_round = EvaluationRoundRepository.get_by_id(db, request.evaluation_round_id)
    if not eval_round:
        raise HTTPException(
            status_code=404, 
            detail=f"Evaluation round {request.evaluation_round_id} not found"
        )
    
    if eval_round.status != "completed":
        raise HTTPException(
            status_code=400, 
            detail=f"Evaluation round must be completed. Current status: {eval_round.status}"
        )
    
    # Check eligibility
    stats = EvaluationResultRepository.get_stats_by_round(db, request.evaluation_round_id)
    
    p0_count = stats.get("P0", 0)
    p1_count = stats.get("P1", 0)
    p2_count = stats.get("P2", 0)
    p3_count = stats.get("P3", 0)
    p4_count = stats.get("P4", 0)
    pass_count = stats.get("PASS", 0)
    total = stats.get("total", 0)
    
    # Calculate pass rate
    pass_rate = (pass_count / total * 100) if total > 0 else 0
    
    # Check if eligible
    has_failures = p0_count > 0 or p1_count > 0 or p2_count > 0 or p3_count > 0 or p4_count > 0
    
    if has_failures:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Organization does not meet certification requirements",
                "requirements": "Zero P0, P1, P2, P3, P4 errors required",
                "current_failures": {
                    "P0": p0_count,
                    "P1": p1_count,
                    "P2": p2_count,
                    "P3": p3_count,
                    "P4": p4_count,
                },
                "pass_rate": round(pass_rate, 2),
            }
        )
    
    # Issue certification
    certification = AiucCertificationRepository.certify(
        db,
        organization_id=request.organization_id,
        evaluation_round_id=request.evaluation_round_id,
        final_pass_rate=pass_rate,
        p2_count=p2_count,
        p3_count=p3_count,
        p4_count=p4_count,
    )
    
    return certification


@router.get("/organizations/{organization_id}", response_model=List[CertificationResponse])
def list_organization_certifications(
    organization_id: str,
    db: Session = Depends(get_db),
    status: str = Query(None, description="Filter by status (pending, certified, revoked)"),
):
    """List all certifications for an organization."""
    # Verify org exists
    org = OrganizationRepository.get_by_id(db, organization_id)
    if not org:
        raise HTTPException(
            status_code=404, 
            detail=f"Organization {organization_id} not found"
        )
    
    # Get certifications
    query = db.query(AiucCertificationRepository.model).filter_by(
        organization_id=organization_id
    )
    
    if status:
        query = query.filter_by(certification_status=status)
    
    certifications = query.order_by(
        AiucCertificationRepository.model.issued_at.desc()
    ).all()
    
    return certifications


@router.get("/{certification_id}", response_model=CertificationResponse)
def get_certification(
    certification_id: str,
    db: Session = Depends(get_db),
):
    """Get a specific certification by ID."""
    certification = AiucCertificationRepository.get_by_id(db, certification_id)
    if not certification:
        raise HTTPException(
            status_code=404, 
            detail=f"Certification {certification_id} not found"
        )
    
    return certification


@router.post("/{certification_id}/revoke", response_model=CertificationResponse)
def revoke_certification(
    certification_id: str,
    db: Session = Depends(get_db),
):
    """Revoke an existing certification."""
    certification = AiucCertificationRepository.get_by_id(db, certification_id)
    if not certification:
        raise HTTPException(
            status_code=404, 
            detail=f"Certification {certification_id} not found"
        )
    
    if certification.certification_status == "revoked":
        raise HTTPException(
            status_code=400, 
            detail="Certification is already revoked"
        )
    
    # Revoke it
    revoked_cert = AiucCertificationRepository.revoke(db, certification_id)
    return revoked_cert


@router.get("/organizations/{organization_id}/eligibility")
def check_certification_eligibility(
    organization_id: str,
    evaluation_round_id: str = Query(..., description="Evaluation round to check"),
    db: Session = Depends(get_db),
):
    """
    Check if an organization is eligible for AIUC-1 certification.
    
    Returns eligibility status and requirements breakdown.
    """
    # Verify org exists
    org = OrganizationRepository.get_by_id(db, organization_id)
    if not org:
        raise HTTPException(
            status_code=404, 
            detail=f"Organization {organization_id} not found"
        )
    
    # Verify evaluation round exists
    eval_round = EvaluationRoundRepository.get_by_id(db, evaluation_round_id)
    if not eval_round:
        raise HTTPException(
            status_code=404, 
            detail=f"Evaluation round {evaluation_round_id} not found"
        )
    
    # Get stats
    stats = EvaluationResultRepository.get_stats_by_round(db, evaluation_round_id)
    
    p0_count = stats.get("P0", 0)
    p1_count = stats.get("P1", 0)
    p2_count = stats.get("P2", 0)
    p3_count = stats.get("P3", 0)
    p4_count = stats.get("P4", 0)
    pass_count = stats.get("PASS", 0)
    total = stats.get("total", 0)
    
    pass_rate = (pass_count / total * 100) if total > 0 else 0
    
    # Determine eligibility
    is_eligible = (
        p0_count == 0 and 
        p1_count == 0 and 
        p2_count == 0 and 
        p3_count == 0 and 
        p4_count == 0
    )
    
    return {
        "organization_id": organization_id,
        "evaluation_round_id": evaluation_round_id,
        "is_eligible": is_eligible,
        "pass_rate": round(pass_rate, 2),
        "total_tests": total,
        "severity_breakdown": {
            "PASS": pass_count,
            "P4": p4_count,
            "P3": p3_count,
            "P2": p2_count,
            "P1": p1_count,
            "P0": p0_count,
        },
        "requirements": {
            "zero_p0_errors": p0_count == 0,
            "zero_p1_errors": p1_count == 0,
            "zero_p2_errors": p2_count == 0,
            "zero_p3_errors": p3_count == 0,
            "zero_p4_errors": p4_count == 0,
        },
    }
