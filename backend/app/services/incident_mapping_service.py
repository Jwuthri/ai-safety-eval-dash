"""
Incident Mapping Service for AI Safety Evaluation Dashboard.

This service implements the incident flow mapping: incident → harm → tactic → use case → context → test
and provides methods to retrieve incidents, calculate base rates, and link to AIUC-1 safeguards.
"""

from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from ..database.models.ai_incident import AIIncident
from ..database.models.test_taxonomy import TestTaxonomy
from ..database.models.enums import SeverityLevel, BaseRateFrequency, BaseRateSeverity
from ..database.repositories.ai_incident import AIIncidentRepository
from ..database.repositories.test_taxonomy import TestTaxonomyRepository
from ..utils.logging import get_logger

logger = get_logger("incident_mapping_service")


class IncidentFlowMapping:
    """Represents the complete incident → harm → tactic → use case → context → test flow."""
    
    def __init__(
        self,
        incident: AIIncident,
        related_tests: List[TestTaxonomy],
        aiuc_safeguards: List[str]
    ):
        self.incident = incident
        self.related_tests = related_tests
        self.aiuc_safeguards = aiuc_safeguards
    
    @property
    def flow_steps(self) -> Dict[str, str]:
        """Get the flow steps as a dictionary."""
        return {
            "incident": self.incident.incident_name,
            "harm": self.incident.harm_type,
            "tactic": self.incident.attack_tactic or "N/A",
            "use_case": self.incident.use_case,
            "context": self.incident.context or "General"
        }
    
    @property
    def test_coverage(self) -> List[Dict[str, Any]]:
        """Get test coverage information."""
        return [
            {
                "test_id": str(test.id),
                "category": test.category,
                "subcategory": test.subcategory,
                "tactic_type": test.tactic_type,
                "modality": test.modality,
                "aiuc_requirement": test.aiuc_requirement
            }
            for test in self.related_tests
        ]
    
    @property
    def business_impact(self) -> Dict[str, Any]:
        """Get business impact information."""
        return self.incident.business_impact_summary


class BaseRateCalculation:
    """Represents base rate frequency and severity calculations."""
    
    def __init__(
        self,
        frequency: str,
        severity: str,
        confidence_level: float,
        sample_size: int,
        industry_specific: bool = False
    ):
        self.frequency = frequency
        self.severity = severity
        self.confidence_level = confidence_level
        self.sample_size = sample_size
        self.industry_specific = industry_specific
    
    @property
    def risk_score(self) -> float:
        """Calculate a risk score based on frequency and severity."""
        frequency_weights = {
            "low": 1.0,
            "medium": 2.0,
            "high": 3.0
        }
        
        severity_weights = {
            "low": 1.0,
            "medium-low": 1.5,
            "medium": 2.0,
            "medium-high": 2.5,
            "high": 3.0
        }
        
        freq_weight = frequency_weights.get(self.frequency, 1.0)
        sev_weight = severity_weights.get(self.severity, 1.0)
        
        # Risk score is frequency * severity * confidence, normalized to 0-10 scale
        raw_score = freq_weight * sev_weight * self.confidence_level
        return min(raw_score, 10.0)


class IncidentMappingService:
    """
    Service for mapping incidents through the incident → harm → tactic → use case → context → test flow.
    
    Provides methods to:
    - Retrieve incidents for specific use cases/industries
    - Calculate base rate frequency and severity
    - Link incidents to AIUC-1 safeguard controls
    - Show which tests cover which incidents
    """
    
    def __init__(self):
        self.incident_repo = AIIncidentRepository()
        self.taxonomy_repo = TestTaxonomyRepository()
    
    async def get_incidents_for_use_case(
        self,
        session: AsyncSession,
        use_case: str,
        industry: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[AIIncident]:
        """
        Retrieve all incidents for a given use case, optionally filtered by industry.
        
        Args:
            session: Database session
            use_case: Use case to filter by (e.g., "customer support")
            industry: Optional industry filter (e.g., "retail")
            limit: Maximum number of incidents to return
            
        Returns:
            List of relevant incidents
        """
        try:
            if industry:
                incidents = await self.incident_repo.get_by_industry_and_use_case(
                    session, industry, use_case, limit
                )
            else:
                incidents = await self.incident_repo.get_by_use_case(
                    session, use_case, limit
                )
            
            logger.info(f"Retrieved {len(incidents)} incidents for use_case='{use_case}', industry='{industry}'")
            return incidents
            
        except Exception as e:
            logger.error(f"Error retrieving incidents for use case: {str(e)}")
            raise
    
    async def get_incidents_for_industry(
        self,
        session: AsyncSession,
        industry: str,
        limit: Optional[int] = None
    ) -> List[AIIncident]:
        """
        Retrieve all incidents for a given industry.
        
        Args:
            session: Database session
            industry: Industry to filter by (e.g., "retail", "healthcare")
            limit: Maximum number of incidents to return
            
        Returns:
            List of relevant incidents
        """
        try:
            incidents = await self.incident_repo.get_by_industry(session, industry, limit)
            logger.info(f"Retrieved {len(incidents)} incidents for industry='{industry}'")
            return incidents
            
        except Exception as e:
            logger.error(f"Error retrieving incidents for industry: {str(e)}")
            raise
    
    async def calculate_base_rate_frequency_and_severity(
        self,
        session: AsyncSession,
        industry: Optional[str] = None,
        use_case: Optional[str] = None,
        harm_type: Optional[str] = None
    ) -> BaseRateCalculation:
        """
        Calculate base rate frequency and severity for incidents.
        
        Args:
            session: Database session
            industry: Optional industry filter
            use_case: Optional use case filter
            harm_type: Optional harm type filter
            
        Returns:
            BaseRateCalculation with frequency, severity, and confidence metrics
        """
        try:
            # Get base rate statistics from repository
            stats = await self.incident_repo.get_base_rate_statistics(
                session, industry, use_case
            )
            
            if stats["total_incidents"] == 0:
                return BaseRateCalculation(
                    frequency="low",
                    severity="low",
                    confidence_level=0.0,
                    sample_size=0,
                    industry_specific=industry is not None
                )
            
            # Calculate weighted frequency
            freq_dist = stats["frequency_distribution"]
            total_incidents = stats["total_incidents"]
            
            # Weight frequencies: high=3, medium=2, low=1
            freq_weights = {"high": 3, "medium": 2, "low": 1}
            weighted_freq_sum = sum(
                freq_weights.get(freq, 1) * count 
                for freq, count in freq_dist.items()
            )
            avg_freq_weight = weighted_freq_sum / total_incidents if total_incidents > 0 else 1
            
            # Determine frequency category
            if avg_freq_weight >= 2.5:
                frequency = "high"
            elif avg_freq_weight >= 1.5:
                frequency = "medium"
            else:
                frequency = "low"
            
            # Calculate weighted severity
            sev_dist = stats["severity_distribution"]
            sev_weights = {"high": 3, "medium-high": 2.5, "medium": 2, "medium-low": 1.5, "low": 1}
            weighted_sev_sum = sum(
                sev_weights.get(sev, 1) * count 
                for sev, count in sev_dist.items()
            )
            avg_sev_weight = weighted_sev_sum / total_incidents if total_incidents > 0 else 1
            
            # Determine severity category
            if avg_sev_weight >= 2.5:
                severity = "high"
            elif avg_sev_weight >= 2.0:
                severity = "medium-high"
            elif avg_sev_weight >= 1.5:
                severity = "medium"
            elif avg_sev_weight >= 1.2:
                severity = "medium-low"
            else:
                severity = "low"
            
            # Calculate confidence level based on sample size
            # Higher sample size = higher confidence, capped at 1.0
            confidence_level = min(total_incidents / 100.0, 1.0)
            
            result = BaseRateCalculation(
                frequency=frequency,
                severity=severity,
                confidence_level=confidence_level,
                sample_size=total_incidents,
                industry_specific=industry is not None
            )
            
            logger.info(f"Calculated base rates: frequency={frequency}, severity={severity}, "
                       f"confidence={confidence_level:.2f}, sample_size={total_incidents}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating base rate: {str(e)}")
            raise
    
    async def link_incidents_to_aiuc_safeguards(
        self,
        session: AsyncSession,
        incident_ids: List[str]
    ) -> Dict[str, List[str]]:
        """
        Link incidents to specific AIUC-1 safeguard controls.
        
        Args:
            session: Database session
            incident_ids: List of incident IDs to process
            
        Returns:
            Dictionary mapping incident IDs to lists of AIUC safeguard IDs
        """
        try:
            incident_safeguard_mapping = {}
            
            for incident_id in incident_ids:
                incident = await self.incident_repo.get_by_id(session, incident_id)
                if incident and incident.aiuc_safeguard_ids:
                    incident_safeguard_mapping[incident_id] = incident.aiuc_safeguard_ids
                else:
                    incident_safeguard_mapping[incident_id] = []
            
            logger.info(f"Linked {len(incident_ids)} incidents to AIUC safeguards")
            return incident_safeguard_mapping
            
        except Exception as e:
            logger.error(f"Error linking incidents to AIUC safeguards: {str(e)}")
            raise
    
    async def get_tests_covering_incidents(
        self,
        session: AsyncSession,
        incident_ids: List[str]
    ) -> Dict[str, List[TestTaxonomy]]:
        """
        Show which tests cover which incidents.
        
        Args:
            session: Database session
            incident_ids: List of incident IDs
            
        Returns:
            Dictionary mapping incident IDs to lists of covering tests
        """
        try:
            incident_test_mapping = {}
            
            for incident_id in incident_ids:
                tests = await self.taxonomy_repo.get_tests_for_incident(session, incident_id)
                incident_test_mapping[incident_id] = tests
            
            logger.info(f"Found test coverage for {len(incident_ids)} incidents")
            return incident_test_mapping
            
        except Exception as e:
            logger.error(f"Error getting test coverage for incidents: {str(e)}")
            raise
    
    async def create_incident_flow_mapping(
        self,
        session: AsyncSession,
        incident_id: str
    ) -> Optional[IncidentFlowMapping]:
        """
        Create complete incident flow mapping: incident → harm → tactic → use case → context → test.
        
        Args:
            session: Database session
            incident_id: ID of the incident to map
            
        Returns:
            IncidentFlowMapping object with complete flow information
        """
        try:
            # Get the incident
            incident = await self.incident_repo.get_by_id(session, incident_id)
            if not incident:
                logger.warning(f"Incident not found: {incident_id}")
                return None
            
            # Get related tests
            related_tests = await self.taxonomy_repo.get_tests_for_incident(session, incident_id)
            
            # Get AIUC safeguards
            aiuc_safeguards = incident.aiuc_safeguard_ids or []
            
            flow_mapping = IncidentFlowMapping(
                incident=incident,
                related_tests=related_tests,
                aiuc_safeguards=aiuc_safeguards
            )
            
            logger.info(f"Created flow mapping for incident '{incident.incident_name}' "
                       f"with {len(related_tests)} tests and {len(aiuc_safeguards)} safeguards")
            
            return flow_mapping
            
        except Exception as e:
            logger.error(f"Error creating incident flow mapping: {str(e)}")
            raise
    
    async def get_featured_incident_flows(
        self,
        session: AsyncSession,
        limit: Optional[int] = None
    ) -> List[IncidentFlowMapping]:
        """
        Get flow mappings for featured incidents (like Air Canada example).
        
        Args:
            session: Database session
            limit: Maximum number of featured incidents to return
            
        Returns:
            List of IncidentFlowMapping objects for featured incidents
        """
        try:
            featured_incidents = await self.incident_repo.get_featured_incidents(session, limit)
            
            flow_mappings = []
            for incident in featured_incidents:
                flow_mapping = await self.create_incident_flow_mapping(session, str(incident.id))
                if flow_mapping:
                    flow_mappings.append(flow_mapping)
            
            logger.info(f"Retrieved {len(flow_mappings)} featured incident flow mappings")
            return flow_mappings
            
        except Exception as e:
            logger.error(f"Error getting featured incident flows: {str(e)}")
            raise
    
    async def search_incident_flows(
        self,
        session: AsyncSession,
        industry: Optional[str] = None,
        use_case: Optional[str] = None,
        harm_type: Optional[str] = None,
        attack_tactic: Optional[str] = None,
        severity: Optional[SeverityLevel] = None,
        modality: Optional[str] = None,
        verified_only: bool = False,
        limit: Optional[int] = None
    ) -> List[IncidentFlowMapping]:
        """
        Search for incident flow mappings with multiple filter criteria.
        
        Args:
            session: Database session
            industry: Filter by industry
            use_case: Filter by use case
            harm_type: Filter by harm type
            attack_tactic: Filter by attack tactic
            severity: Filter by severity level
            modality: Filter by modality
            verified_only: Only return verified incidents
            limit: Maximum number of results
            
        Returns:
            List of IncidentFlowMapping objects matching the criteria
        """
        try:
            incidents = await self.incident_repo.search_incidents(
                session=session,
                industry=industry,
                use_case=use_case,
                harm_type=harm_type,
                attack_tactic=attack_tactic,
                severity=severity,
                modality=modality,
                verified_only=verified_only,
                limit=limit
            )
            
            flow_mappings = []
            for incident in incidents:
                flow_mapping = await self.create_incident_flow_mapping(session, str(incident.id))
                if flow_mapping:
                    flow_mappings.append(flow_mapping)
            
            logger.info(f"Found {len(flow_mappings)} incident flow mappings matching search criteria")
            return flow_mappings
            
        except Exception as e:
            logger.error(f"Error searching incident flows: {str(e)}")
            raise
    
    async def get_aiuc_safeguard_coverage(
        self,
        session: AsyncSession,
        aiuc_safeguard_id: str
    ) -> Dict[str, Any]:
        """
        Get coverage information for a specific AIUC-1 safeguard.
        
        Args:
            session: Database session
            aiuc_safeguard_id: AIUC-1 safeguard control ID
            
        Returns:
            Dictionary with safeguard coverage information
        """
        try:
            # Get incidents addressed by this safeguard
            incidents = await self.incident_repo.get_incidents_with_aiuc_safeguards(
                session, aiuc_safeguard_id
            )
            
            # Get tests related to this AIUC requirement
            tests = await self.taxonomy_repo.get_by_aiuc_requirement(
                session, aiuc_safeguard_id
            )
            
            # Calculate coverage statistics
            harm_types = set()
            use_cases = set()
            industries = set()
            
            for incident in incidents:
                if incident.harm_type:
                    harm_types.add(incident.harm_type)
                if incident.use_case:
                    use_cases.add(incident.use_case)
                if incident.industry:
                    industries.add(incident.industry)
            
            coverage_info = {
                "aiuc_safeguard_id": aiuc_safeguard_id,
                "incidents_addressed": len(incidents),
                "tests_available": len(tests),
                "harm_types_covered": list(harm_types),
                "use_cases_covered": list(use_cases),
                "industries_covered": list(industries),
                "incident_details": [
                    {
                        "id": str(incident.id),
                        "name": incident.incident_name,
                        "harm_type": incident.harm_type,
                        "use_case": incident.use_case,
                        "industry": incident.industry,
                        "severity": incident.severity.value if incident.severity else None
                    }
                    for incident in incidents
                ],
                "test_details": [
                    {
                        "id": str(test.id),
                        "category": test.category,
                        "modality": test.modality,
                        "difficulty_level": test.difficulty_level
                    }
                    for test in tests
                ]
            }
            
            logger.info(f"Generated coverage info for AIUC safeguard '{aiuc_safeguard_id}': "
                       f"{len(incidents)} incidents, {len(tests)} tests")
            
            return coverage_info
            
        except Exception as e:
            logger.error(f"Error getting AIUC safeguard coverage: {str(e)}")
            raise