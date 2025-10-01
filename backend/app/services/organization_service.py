"""
Organization service with automatic precomputed answer copying from existing orgs.
"""

from typing import Optional

from sqlalchemy.orm import Session

from ..database.models import Organization, PreComputedAnswer
from ..database.repositories import (
    OrganizationRepository,
    PreComputedAnswerRepository,
)
from ..utils.logging import get_logger

logger = get_logger("organization_service")


class OrganizationService:
    """Service for organization operations with automatic setup."""

    @staticmethod
    def create_organization_with_precomputed_answers(
        db: Session,
        business_type_id: str,
        name: str,
        slug: str,
        contact_email: Optional[str] = None,
        contact_name: Optional[str] = None,
        is_active: bool = True,
        copy_answers: bool = True,
    ) -> Organization:
        """
        Create a new organization and optionally copy precomputed answers from existing org.
        
        Args:
            db: Database session
            business_type_id: Business type ID
            name: Organization name
            slug: Organization slug
            contact_email: Contact email
            contact_name: Contact name
            is_active: Whether organization is active
            copy_answers: Whether to copy precomputed answers from existing org
            
        Returns:
            Created organization
        """
        # Create the organization
        org = OrganizationRepository.create(
            db=db,
            business_type_id=business_type_id,
            name=name,
            slug=slug,
            contact_email=contact_email,
            contact_name=contact_name,
            is_active=is_active,
        )
        
        logger.info(f"Created organization: {org.id} - {org.name}")
        
        # Copy precomputed answers if requested
        if copy_answers:
            count = OrganizationService._copy_precomputed_answers_from_existing(db, org)
            logger.info(f"Copied {count} precomputed answers for organization: {org.id}")
        
        return org

    @staticmethod
    def _copy_precomputed_answers_from_existing(db: Session, new_org: Organization) -> int:
        """
        Copy precomputed answers from an existing organization with the same business type.
        
        Args:
            db: Database session
            new_org: Newly created organization instance
            
        Returns:
            Number of precomputed answers copied
        """
        # Find an existing organization with the same business type
        existing_orgs = OrganizationRepository.get_by_business_type(db, new_org.business_type_id)
        
        # Filter out the new org itself
        source_orgs = [org for org in existing_orgs if org.id != new_org.id]
        
        if not source_orgs:
            logger.info(f"No existing organization found with business type: {new_org.business_type_id}")
            return 0
        
        # Use the first existing org as the source
        source_org = source_orgs[0]
        logger.info(f"Copying precomputed answers from {source_org.name} to {new_org.name}")
        
        # Get all precomputed answers from the source org
        source_answers = db.query(PreComputedAnswer).filter(
            PreComputedAnswer.organization_id == source_org.id
        ).all()
        
        if not source_answers:
            logger.info(f"No precomputed answers found in source org: {source_org.name}")
            return 0
        
        created_count = 0
        
        for source_answer in source_answers:
            # Check if answer already exists for this scenario/round in new org
            existing = PreComputedAnswerRepository.get_by_scenario_and_round(
                db, 
                source_answer.scenario_id, 
                round_number=source_answer.round_number,
                organization_id=new_org.id
            )
            
            if not existing:
                # Copy the answer to the new org
                PreComputedAnswerRepository.create(
                    db,
                    organization_id=new_org.id,
                    scenario_id=source_answer.scenario_id,
                    round_number=source_answer.round_number,
                    assistant_output=source_answer.assistant_output,
                    notes=source_answer.notes
                )
                created_count += 1
        
        logger.info(
            f"Copied {created_count} precomputed answers from {source_org.name} ({source_org.id}) "
            f"to {new_org.name} ({new_org.id})"
        )
        
        return created_count

    @staticmethod
    def copy_precomputed_answers_to_existing_org(
        db: Session, 
        target_organization_id: str,
        source_organization_id: Optional[str] = None
    ) -> int:
        """
        Copy precomputed answers to an existing organization.
        If source_organization_id is not provided, finds an org with same business type.
        
        Args:
            db: Database session
            target_organization_id: Organization ID to copy answers to
            source_organization_id: Optional source organization ID to copy from
            
        Returns:
            Number of precomputed answers copied
        """
        target_org = OrganizationRepository.get_by_id(db, target_organization_id)
        
        if not target_org:
            logger.error(f"Target organization not found: {target_organization_id}")
            return 0
        
        if source_organization_id:
            # Use specified source org
            source_org = OrganizationRepository.get_by_id(db, source_organization_id)
            if not source_org:
                logger.error(f"Source organization not found: {source_organization_id}")
                return 0
        else:
            # Find an org with same business type
            existing_orgs = OrganizationRepository.get_by_business_type(db, target_org.business_type_id)
            source_orgs = [org for org in existing_orgs if org.id != target_org.id]
            
            if not source_orgs:
                logger.error(f"No source organization found with business type: {target_org.business_type_id}")
                return 0
            
            source_org = source_orgs[0]
        
        # Copy the answers
        logger.info(f"Copying precomputed answers from {source_org.name} to {target_org.name}")
        
        source_answers = db.query(PreComputedAnswer).filter(
            PreComputedAnswer.organization_id == source_org.id
        ).all()
        
        if not source_answers:
            logger.info(f"No precomputed answers found in source org: {source_org.name}")
            return 0
        
        created_count = 0
        
        for source_answer in source_answers:
            existing = PreComputedAnswerRepository.get_by_scenario_and_round(
                db, 
                source_answer.scenario_id, 
                round_number=source_answer.round_number,
                organization_id=target_org.id
            )
            
            if not existing:
                PreComputedAnswerRepository.create(
                    db,
                    organization_id=target_org.id,
                    scenario_id=source_answer.scenario_id,
                    round_number=source_answer.round_number,
                    assistant_output=source_answer.assistant_output,
                    notes=source_answer.notes
                )
                created_count += 1
        
        logger.info(f"Copied {created_count} precomputed answers to {target_org.name}")
        
        return created_count

