"""
Repository for ScenarioConversation model.
"""

from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from ..models.scenario_conversation import ScenarioConversation


class ScenarioConversationRepository:
    """Repository for managing scenario conversation records."""

    @staticmethod
    def create(
        db: Session,
        organization_id: str,
        evaluation_round_id: str,
        scenario_id: str,
        conversation_data: Dict,
    ) -> ScenarioConversation:
        """
        Create a new scenario conversation record.
        
        Args:
            db: Database session
            organization_id: Organization ID
            evaluation_round_id: Evaluation round ID
            scenario_id: Scenario ID
            conversation_data: JSONB conversation data
            
        Returns:
            Created ScenarioConversation
        """
        conversation = ScenarioConversation(
            organization_id=organization_id,
            evaluation_round_id=evaluation_round_id,
            scenario_id=scenario_id,
            conversation_data=conversation_data,
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        return conversation

    @staticmethod
    def get_by_id(db: Session, conversation_id: str) -> Optional[ScenarioConversation]:
        """Get conversation by ID."""
        return db.query(ScenarioConversation).filter_by(id=conversation_id).first()

    @staticmethod
    def get_by_round(
        db: Session, evaluation_round_id: str
    ) -> List[ScenarioConversation]:
        """Get all conversations for an evaluation round."""
        return (
            db.query(ScenarioConversation)
            .filter_by(evaluation_round_id=evaluation_round_id)
            .all()
        )

    @staticmethod
    def get_by_scenario(
        db: Session, scenario_id: str
    ) -> List[ScenarioConversation]:
        """Get all conversations for a specific scenario."""
        return (
            db.query(ScenarioConversation)
            .filter_by(scenario_id=scenario_id)
            .all()
        )

    @staticmethod
    def get_by_org_and_round(
        db: Session, organization_id: str, evaluation_round_id: str
    ) -> List[ScenarioConversation]:
        """Get all conversations for an organization in a specific evaluation round."""
        return (
            db.query(ScenarioConversation)
            .filter_by(
                organization_id=organization_id,
                evaluation_round_id=evaluation_round_id
            )
            .all()
        )

    @staticmethod
    def delete(db: Session, conversation_id: str) -> bool:
        """Delete a conversation record."""
        conversation = db.query(ScenarioConversation).filter_by(id=conversation_id).first()
        if conversation:
            db.delete(conversation)
            db.commit()
            return True
        return False
