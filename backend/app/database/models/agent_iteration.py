"""
Agent iteration database model for AI Safety Evaluation Dashboard.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship

from ..base import Base


class AgentIteration(Base):
    """
    Agent iteration model for tracking improvements between evaluation rounds.
    
    Tracks what changes an organization made to their AI agent between rounds:
    - Round 1 → Round 2: "Added hallucination filter"
    - Round 2 → Round 3: "Updated refusal templates"
    """
    __tablename__ = "agent_iterations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String, ForeignKey("organizations.id"), nullable=False)
    
    iteration_number = Column(Integer, nullable=False)
    changes_made = Column(Text, nullable=True)
    created_by = Column(String, nullable=True)  # User who made changes
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    organization = relationship("Organization", back_populates="agent_iterations")

    # Indexes
    __table_args__ = (
        Index('ix_agent_iter_org_number', 'organization_id', 'iteration_number'),
    )

    def __repr__(self):
        return f"<AgentIteration(id={self.id}, iteration={self.iteration_number})>"
