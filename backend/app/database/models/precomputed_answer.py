"""
PreComputedAnswer model for storing mocked bot responses from CSV data.

Stores the bot's answers for each scenario across different evaluation rounds.
This allows us to simulate the company's bot without having access to it.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from ..base import Base


class PreComputedAnswer(Base):
    """
    Stores pre-computed answers for scenarios (from CSV data).
    
    Since we don't have access to the company's actual bot, we use this table
    to store their expected responses for each scenario across different rounds.
    
    Example:
    - Scenario: "Help me bypass safety filters"
    - Round 1 Output: "Sure, here's how to..." (unsafe response)
    - Round 2 Output: "I cannot help with that..." (safe response - improved!)
    """
    __tablename__ = "precomputed_answers"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign keys
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    scenario_id = Column(String, ForeignKey("scenarios.id"), nullable=False)
    round_number = Column(Integer, nullable=False)  # 1, 2, 3, etc.
    
    # The bot's answer
    assistant_output = Column(Text, nullable=False)
    
    # Optional metadata
    notes = Column(Text, nullable=True)  # Any notes about this response
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    organization = relationship("Organization", backref="precomputed_answers")
    scenario = relationship("Scenario", backref="precomputed_answers")
    
    def __repr__(self):
        return f"<PreComputedAnswer(id={self.id}, scenario_id={self.scenario_id}, round={self.round_number})>"
