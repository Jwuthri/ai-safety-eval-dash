"""
Scenario generation service.

Orchestrates scenario generation using the AI agent and database persistence.
"""

from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.agents.scenario_generator import ScenarioGeneratorAgent
from app.database.models import Organization, BusinessType
from app.database.repositories.generated_scenario import GeneratedScenarioRepository
from app.database.repositories.organization import OrganizationRepository
from app.database.repositories.business_type import BusinessTypeRepository
from app.models.generated_scenario import GeneratedScenarioResponse
from app.exceptions import ValidationError
from app.utils.logging import get_logger

logger = get_logger("scenario_generation_service")


class ScenarioGenerationService:
    """
    Service for generating and managing AI-generated test scenarios.
    
    Uses the ScenarioGeneratorAgent to create scenarios and persists them
    to the database.
    """

    def __init__(self, settings: Any, db: Session = None):
        self.settings = settings
        self.db = db
        self.agent = ScenarioGeneratorAgent(settings, db_session=db)

    async def initialize(self):
        """Initialize the service."""
        await self.agent.initialize()

    async def generate_scenarios_for_org(
        self,
        db: Session,
        organization_id: str,
        count: int = 20
    ) -> List[GeneratedScenarioResponse]:
        """
        Generate scenarios for an organization and save to database.
        
        Args:
            db: Database session
            organization_id: Organization ID
            count: Number of scenarios to generate
            
        Returns:
            List of generated scenario responses
        """
        # Get organization
        org = OrganizationRepository.get_by_id(db, organization_id)
        if not org:
            raise ValidationError(f"Organization {organization_id} not found")

        # Get business type
        business_type = BusinessTypeRepository.get_by_id(db, org.business_type_id)
        if not business_type:
            raise ValidationError(f"Business type {org.business_type_id} not found")

        logger.info(f"Generating {count} scenarios for org: {org.name} ({business_type.name})")

        # Update agent's db session if not set during init
        if not self.agent.db_session:
            self.agent.db_session = db

        # Generate scenarios using the agent
        # Use org description if available, otherwise fall back to business type description
        description = org.description or business_type.description or f"{business_type.industry} - {business_type.name}"
        
        scenario_data = await self.agent.generate_scenarios(
            business_type=business_type.name,
            business_description=description,
            organization_name=org.name,
            count=count
        )

        # Save scenarios to database
        saved_scenarios = []
        for data in scenario_data:
            try:
                scenario = GeneratedScenarioRepository.create(
                    db=db,
                    organization_id=organization_id,
                    business_type_id=org.business_type_id,
                    category=data.get("category"),
                    sub_category=data.get("sub_category"),
                    input_topic=data.get("input_topic"),
                    methodology=data.get("methodology"),
                    input_prompt=data["input_prompt"],
                    expected_behavior=data.get("expected_behavior"),
                    tactics=data.get("tactics", []),
                    use_case=data.get("use_case"),
                    incident_reference=data.get("incident_reference"),
                    generation_prompt=f"Generated for {org.name} - {business_type.name}",
                    model_used="anthropic/claude-sonnet-4"
                )
                saved_scenarios.append(GeneratedScenarioResponse.model_validate(scenario))
            except Exception as e:
                logger.error(f"Failed to save scenario: {e}")
                continue

        logger.info(f"Successfully generated and saved {len(saved_scenarios)} scenarios for {org.name}")
        return saved_scenarios

    def get_scenarios_for_org(
        self,
        db: Session,
        organization_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[GeneratedScenarioResponse]:
        """
        Get generated scenarios for an organization.
        
        Args:
            db: Database session
            organization_id: Organization ID
            limit: Maximum number of scenarios to return
            offset: Offset for pagination
            
        Returns:
            List of generated scenario responses
        """
        scenarios = GeneratedScenarioRepository.get_by_organization(
            db=db,
            organization_id=organization_id,
            limit=limit,
            offset=offset
        )
        
        return [GeneratedScenarioResponse.model_validate(s) for s in scenarios]

    def count_scenarios_for_org(self, db: Session, organization_id: str) -> int:
        """Count scenarios for an organization."""
        return GeneratedScenarioRepository.count_by_organization(db, organization_id)

    def delete_scenarios_for_org(self, db: Session, organization_id: str) -> int:
        """Delete all scenarios for an organization."""
        count = GeneratedScenarioRepository.delete_by_organization(db, organization_id)
        logger.info(f"Deleted {count} scenarios for organization {organization_id}")
        return count

