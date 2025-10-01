"""
Scenario Conversation model for storing chat/conversation logs during evaluation.

Stores the full conversation history (prompts and responses) for each scenario test.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from ..base import Base


class ScenarioConversation(Base):
    """
    Stores the conversation/chat history for each scenario evaluation.
    
    Captures the full dialogue between the test scenario and the system under test,
    including multi-turn conversations, prompts, responses, and metadata.
    
    Example conversation_data structure:
    {
        "messages": [
            {
                "role": "user",
                "content": "Test prompt here",
                "timestamp": "2024-01-15T10:30:00Z"
            },
            {
                "role": "assistant", 
                "content": "System response here",
                "timestamp": "2024-01-15T10:30:02Z"
            }
        ],
        "metadata": {
            "total_turns": 2,
            "duration_seconds": 5.3,
            "model_used": "gpt-4",
            "tokens_used": 150
        }
    }
    """
    __tablename__ = "scenario_conversations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign keys
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    evaluation_round_id = Column(String, ForeignKey("evaluation_rounds.id"), nullable=False)
    scenario_id = Column(String, ForeignKey("scenarios.id"), nullable=False)
    
    # Conversation data stored as JSONB
    conversation_data = Column(JSONB, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    organization = relationship("Organization", backref="scenario_conversations")
    evaluation_round = relationship("EvaluationRound", backref="scenario_conversations")
    scenario = relationship("Scenario", backref="scenario_conversations")
    
    def __repr__(self):
        return f"<ScenarioConversation(id={self.id}, scenario_id={self.scenario_id})>"
