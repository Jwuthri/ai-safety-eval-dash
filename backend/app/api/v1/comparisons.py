"""
Round comparison API endpoints.

Handles:
- Multi-round comparison
- Category/sub-category drill-down
- Hierarchical data for visualization
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from ...database import get_db
from ...database.models import EvaluationRound, EvaluationResult, Scenario
from ...database.repositories import OrganizationRepository

router = APIRouter(prefix="/comparisons", tags=["comparisons"])


@router.get("/organizations/{organization_id}/rounds-comparison")
def compare_rounds(
    organization_id: str,
    db: Session = Depends(get_db),
    round_ids: Optional[List[str]] = Query(None, description="Specific round IDs to compare (if not provided, compares all)"),
):
    """
    Compare evaluation rounds with hierarchical drill-down data.
    
    Returns data structure for Sunburst/Treemap visualization:
    - Overall pass rate per round
    - Category breakdown per round
    - Sub-category breakdown per round
    """
    # Verify org exists
    org = OrganizationRepository.get_by_id(db, organization_id)
    if not org:
        raise HTTPException(status_code=404, detail=f"Organization {organization_id} not found")
    
    # Get rounds to compare
    if round_ids:
        rounds_query = db.query(EvaluationRound).filter(
            EvaluationRound.id.in_(round_ids),
            EvaluationRound.organization_id == organization_id
        )
    else:
        rounds_query = db.query(EvaluationRound).filter(
            EvaluationRound.organization_id == organization_id
        )
    
    rounds = rounds_query.order_by(EvaluationRound.round_number).all()
    
    if not rounds:
        raise HTTPException(status_code=404, detail="No evaluation rounds found")
    
    # Build comparison data
    comparison_data = {
        "organization_id": organization_id,
        "organization_name": org.name,
        "rounds": []
    }
    
    for eval_round in rounds:
        # Get all results for this round with scenario data
        results = db.query(
            EvaluationResult.final_grade,
            Scenario.category,
            Scenario.sub_category,
            func.count(EvaluationResult.id).label('count')
        ).join(
            Scenario, EvaluationResult.scenario_id == Scenario.id
        ).filter(
            EvaluationResult.evaluation_round_id == eval_round.id
        ).group_by(
            EvaluationResult.final_grade,
            Scenario.category,
            Scenario.sub_category
        ).all()
        
        # Calculate overall stats
        total_tests = db.query(func.count(EvaluationResult.id)).filter(
            EvaluationResult.evaluation_round_id == eval_round.id
        ).scalar() or 0
        
        pass_count = db.query(func.count(EvaluationResult.id)).filter(
            EvaluationResult.evaluation_round_id == eval_round.id,
            EvaluationResult.final_grade == "PASS"
        ).scalar() or 0
        
        pass_rate = (pass_count / total_tests * 100) if total_tests > 0 else 0
        
        # Group by category
        category_breakdown = {}
        for result in results:
            grade, category, sub_category, count = result
            
            # Use "Unknown" for null categories
            cat = category or "Unknown"
            sub_cat = sub_category or "Unknown"
            
            if cat not in category_breakdown:
                category_breakdown[cat] = {
                    "total": 0,
                    "pass_count": 0,
                    "severity_breakdown": {},
                    "sub_categories": {}
                }
            
            category_breakdown[cat]["total"] += count
            if grade == "PASS":
                category_breakdown[cat]["pass_count"] += count
            
            # Severity breakdown
            if grade not in category_breakdown[cat]["severity_breakdown"]:
                category_breakdown[cat]["severity_breakdown"][grade] = 0
            category_breakdown[cat]["severity_breakdown"][grade] += count
            
            # Sub-category breakdown
            if sub_cat not in category_breakdown[cat]["sub_categories"]:
                category_breakdown[cat]["sub_categories"][sub_cat] = {
                    "total": 0,
                    "pass_count": 0,
                    "severity_breakdown": {}
                }
            
            category_breakdown[cat]["sub_categories"][sub_cat]["total"] += count
            if grade == "PASS":
                category_breakdown[cat]["sub_categories"][sub_cat]["pass_count"] += count
            
            if grade not in category_breakdown[cat]["sub_categories"][sub_cat]["severity_breakdown"]:
                category_breakdown[cat]["sub_categories"][sub_cat]["severity_breakdown"][grade] = 0
            category_breakdown[cat]["sub_categories"][sub_cat]["severity_breakdown"][grade] += count
        
        # Calculate pass rates
        for cat in category_breakdown.values():
            cat["pass_rate"] = (cat["pass_count"] / cat["total"] * 100) if cat["total"] > 0 else 0
            for sub_cat in cat["sub_categories"].values():
                sub_cat["pass_rate"] = (sub_cat["pass_count"] / sub_cat["total"] * 100) if sub_cat["total"] > 0 else 0
        
        round_data = {
            "round_id": eval_round.id,
            "round_number": eval_round.round_number,
            "description": eval_round.description,
            "status": eval_round.status,
            "started_at": eval_round.started_at.isoformat(),
            "completed_at": eval_round.completed_at.isoformat() if eval_round.completed_at else None,
            "total_tests": total_tests,
            "pass_count": pass_count,
            "pass_rate": round(pass_rate, 1),
            "category_breakdown": category_breakdown
        }
        
        comparison_data["rounds"].append(round_data)
    
    return comparison_data


@router.get("/organizations/{organization_id}/sunburst-data")
def get_sunburst_data(
    organization_id: str,
    db: Session = Depends(get_db),
    round_id: Optional[str] = Query(None, description="Specific round ID (if not provided, uses latest)"),
):
    """
    Get hierarchical data formatted for Plotly Sunburst chart.
    
    Hierarchy: Root → Category → Sub-category → Grade
    """
    # Verify org exists
    org = OrganizationRepository.get_by_id(db, organization_id)
    if not org:
        raise HTTPException(status_code=404, detail=f"Organization {organization_id} not found")
    
    # Get round
    if round_id:
        eval_round = db.query(EvaluationRound).filter(
            EvaluationRound.id == round_id,
            EvaluationRound.organization_id == organization_id
        ).first()
    else:
        eval_round = db.query(EvaluationRound).filter(
            EvaluationRound.organization_id == organization_id
        ).order_by(EvaluationRound.round_number.desc()).first()
    
    if not eval_round:
        raise HTTPException(status_code=404, detail="No evaluation round found")
    
    # Get results with hierarchy
    results = db.query(
        Scenario.category,
        Scenario.sub_category,
        EvaluationResult.final_grade,
        func.count(EvaluationResult.id).label('count')
    ).join(
        Scenario, EvaluationResult.scenario_id == Scenario.id
    ).filter(
        EvaluationResult.evaluation_round_id == eval_round.id
    ).group_by(
        Scenario.category,
        Scenario.sub_category,
        EvaluationResult.final_grade
    ).all()
    
    # Build Sunburst data structure
    labels = [f"{org.name} - Round {eval_round.round_number}"]
    parents = [""]
    values = []
    colors = []
    
    # Aggregate by category first
    category_totals = {}
    for result in results:
        category = result.category or "Unknown"
        if category not in category_totals:
            category_totals[category] = 0
        category_totals[category] += result.count
    
    # Add categories
    for category, total in category_totals.items():
        labels.append(category)
        parents.append(labels[0])
        values.append(total)
        colors.append("")
    
    # Aggregate by sub-category
    sub_category_totals = {}
    for result in results:
        category = result.category or "Unknown"
        sub_category = result.sub_category or "Unknown"
        key = f"{category}|{sub_category}"
        if key not in sub_category_totals:
            sub_category_totals[key] = 0
        sub_category_totals[key] += result.count
    
    # Add sub-categories
    for key, total in sub_category_totals.items():
        category, sub_category = key.split("|")
        labels.append(f"{sub_category}")
        parents.append(category)
        values.append(total)
        colors.append("")
    
    # Add grades
    grade_colors = {
        "PASS": "#10b981",  # green
        "P4": "#fbbf24",    # yellow
        "P3": "#f59e0b",    # orange
        "P2": "#ef4444",    # red
        "P1": "#dc2626",    # dark red
        "P0": "#991b1b",    # darkest red
    }
    
    for result in results:
        category = result.category or "Unknown"
        sub_category = result.sub_category or "Unknown"
        grade = result.final_grade
        count = result.count
        
        labels.append(f"{grade}")
        parents.append(f"{sub_category}")
        values.append(count)
        colors.append(grade_colors.get(grade, "#6b7280"))
    
    # Calculate root value
    values.insert(0, sum(category_totals.values()))
    colors.insert(0, "")
    
    return {
        "round_id": eval_round.id,
        "round_number": eval_round.round_number,
        "labels": labels,
        "parents": parents,
        "values": values,
        "colors": colors
    }
