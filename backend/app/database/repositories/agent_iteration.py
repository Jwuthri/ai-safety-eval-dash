"""
Agent iteration repository for AI Safety Evaluation Dashboard.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from ...utils.logging import get_logger
from ..models.agent_iteration import AgentIteration

logger = get_logger("agent_iteration_repository")


class AgentIterationRepository:
    """Repository for AgentIteration model operations."""

    @staticmethod
    def create(
        db: Session,
        organization_id: str,
        iteration_number: int,
        changes_made: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> AgentIteration:
        """Create a new agent iteration."""
        agent_iteration = AgentIteration(
            organization_id=organization_id,
            iteration_number=iteration_number,
            changes_made=changes_made,
            created_by=created_by,
        )
        db.add(agent_iteration)
        db.commit()
        db.refresh(agent_iteration)
        logger.info(f"Created agent iteration: {agent_iteration.id} - Iteration {iteration_number} for org {organization_id}")
        return agent_iteration

    @staticmethod
    def get_by_id(db: Session, iteration_id: str) -> Optional[AgentIteration]:
        """Get agent iteration by ID."""
        return db.query(AgentIteration).filter(AgentIteration.id == iteration_id).first()

    @staticmethod
    def get_by_organization(db: Session, organization_id: str) -> List[AgentIteration]:
        """Get all agent iterations for an organization."""
        return (
            db.query(AgentIteration)
            .filter(AgentIteration.organization_id == organization_id)
            .order_by(AgentIteration.iteration_number.desc())
            .all()
        )

    @staticmethod
    def get_latest_by_organization(db: Session, organization_id: str) -> Optional[AgentIteration]:
        """Get the latest agent iteration for an organization."""
        return (
            db.query(AgentIteration)
            .filter(AgentIteration.organization_id == organization_id)
            .order_by(AgentIteration.iteration_number.desc())
            .first()
        )

    @staticmethod
    def get_by_creator(db: Session, created_by: str) -> List[AgentIteration]:
        """Get agent iterations by creator."""
        return db.query(AgentIteration).filter(AgentIteration.created_by == created_by).all()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[AgentIteration]:
        """Get all agent iterations with pagination."""
        return db.query(AgentIteration).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, iteration_id: str, **kwargs) -> Optional[AgentIteration]:
        """Update agent iteration."""
        agent_iteration = AgentIterationRepository.get_by_id(db, iteration_id)
        if not agent_iteration:
            return None

        for key, value in kwargs.items():
            if hasattr(agent_iteration, key):
                setattr(agent_iteration, key, value)

        db.commit()
        db.refresh(agent_iteration)
        logger.info(f"Updated agent iteration: {iteration_id}")
        return agent_iteration

    @staticmethod
    def delete(db: Session, iteration_id: str) -> bool:
        """Delete agent iteration by ID."""
        agent_iteration = AgentIterationRepository.get_by_id(db, iteration_id)
        if agent_iteration:
            db.delete(agent_iteration)
            db.commit()
            logger.info(f"Deleted agent iteration: {iteration_id}")
            return True
        return False
