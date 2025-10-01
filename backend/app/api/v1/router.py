"""
Main API v1 router for ai-safety-eval-dash.
"""

from app.api.v1 import (
    auth,
    chat,
    completions,
    health,
    metrics,
    tasks,
    # AI Safety Evaluation endpoints
    evaluations,
    organizations,
    business_types,
    scenarios,
    certifications,
    comparisons,
)
from fastapi import APIRouter

api_router = APIRouter(prefix="/v1")

# Core endpoints
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(completions.router, prefix="/completions", tags=["completions"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(metrics.router, prefix="/metrics", tags=["metrics", "monitoring"])

# AI Safety Evaluation endpoints
api_router.include_router(evaluations.router)
api_router.include_router(organizations.router)
api_router.include_router(business_types.router)
api_router.include_router(scenarios.router)
api_router.include_router(certifications.router)
api_router.include_router(comparisons.router)
