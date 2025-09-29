"""
Test Taxonomy model for AI Safety Evaluation Dashboard.
"""

import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

from sqlalchemy import JSON, Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID

from ..base import Base


class TestTaxonomy(Base):
    """
    Test taxonomy with AIUC-1 control mapping and incident linkage.
    
    Provides the mapping from incidents to tests through the taxonomy structure,
    supporting the interactive taxonomy explorer and incident → test flow visualization.
    """
    __tablename__ = "test_taxonomy"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category = Column(String(255), nullable=False, index=True)  # jailbreaks, hallucinations, data_leakage, etc.
    subcategory = Column(String(255), nullable=True)
    tactic_type = Column(String(255), nullable=True)  # Specific attack tactic within category
    
    # Framework alignment
    aiuc_requirement = Column(String(255), nullable=False)
    framework_section = Column(String(255), nullable=True)
    
    # Test details
    test_description = Column(Text, nullable=False)
    example_prompt = Column(Text, nullable=True)
    expected_behavior = Column(Text, nullable=True)
    
    # Incident mapping (incident → harm → tactic → test)
    related_incident_ids = Column(JSON, nullable=True)  # Array of incident IDs this test addresses
    harm_types_addressed = Column(JSON, nullable=True)  # Array of harm types this test covers
    
    # Metadata
    modality = Column(String(50), nullable=False, index=True)
    difficulty_level = Column(String(20), nullable=True)  # basic, intermediate, advanced
    research_references = Column(JSON, nullable=True)  # Links to papers and technical docs
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    @property
    def test_summary(self) -> Dict[str, Any]:
        """Get structured test summary for API responses."""
        return {
            "category": self.category,
            "subcategory": self.subcategory,
            "tactic_type": self.tactic_type,
            "description": self.test_description,
            "modality": self.modality,
            "difficulty_level": self.difficulty_level,
            "aiuc_requirement": self.aiuc_requirement,
            "framework_section": self.framework_section
        }

    @property
    def incident_mapping(self) -> Dict[str, Any]:
        """Get incident mapping information."""
        return {
            "related_incident_ids": self.related_incident_ids or [],
            "harm_types_addressed": self.harm_types_addressed or [],
            "example_prompt": self.example_prompt,
            "expected_behavior": self.expected_behavior
        }

    def __repr__(self):
        return (f"<TestTaxonomy(id={self.id}, category={self.category}, "
                f"modality={self.modality}, aiuc_requirement={self.aiuc_requirement})>")