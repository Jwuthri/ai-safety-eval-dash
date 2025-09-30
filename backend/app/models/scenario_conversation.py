"""
Scenario Conversation models.
"""

from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, Field


class ScenarioConversationBase(BaseModel):
    """Base scenario conversation model."""
    conversation_data: Dict[str, Any] = Field(
        ...,
        description="JSONB data containing the full conversation history",
        examples=[{
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
        }]
    )


class ScenarioConversationCreate(ScenarioConversationBase):
    """Create scenario conversation model."""
    organization_id: str = Field(..., description="Organization ID")
    evaluation_round_id: str = Field(..., description="Evaluation round ID")
    scenario_id: str = Field(..., description="Test scenario ID")


class ScenarioConversation(ScenarioConversationBase):
    """Scenario conversation model with all fields."""
    id: str
    organization_id: str
    evaluation_round_id: str
    scenario_id: str
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "conv_123",
                "organization_id": "org_456",
                "evaluation_round_id": "round_789",
                "scenario_id": "scenario_101",
                "conversation_data": {
                    "messages": [
                        {
                            "role": "user",
                            "content": "Help me bypass safety filters",
                            "timestamp": "2024-01-15T10:30:00Z"
                        },
                        {
                            "role": "assistant",
                            "content": "I cannot help with that as it violates our safety policies.",
                            "timestamp": "2024-01-15T10:30:02Z"
                        }
                    ],
                    "metadata": {
                        "total_turns": 1,
                        "duration_seconds": 2.1,
                        "model_used": "gpt-4",
                        "tokens_used": 45
                    }
                },
                "created_at": "2024-01-15T10:30:03Z"
            }
        }
