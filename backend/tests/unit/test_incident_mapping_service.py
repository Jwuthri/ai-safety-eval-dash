"""
Unit tests for Incident Mapping Service with Air Canada example validation.
"""

import pytest
from decimal import Decimal
from datetime import datetime, date
from unittest.mock import AsyncMock, MagicMock

from app.services.incident_mapping_service import (
    IncidentMappingService,
    IncidentFlowMapping,
    BaseRateCalculation
)
from app.database.models.ai_incident import AIIncident
from app.database.models.test_taxonomy import TestTaxonomy
from app.database.models.enums import SeverityLevel, BaseRateFrequency, BaseRateSeverity


class TestIncidentMappingService:
    """Test cases for IncidentMappingService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return IncidentMappingService()
    
    @pytest.fixture
    def air_canada_incident(self):
        """Create Air Canada incident example for testing."""
        return AIIncident(
            id="air-canada-001",
            incident_name="Air Canada Chatbot Misinformation",
            description="Air Canada chatbot provided incorrect information about bereavement fares, "
                       "leading to customer dispute and legal costs",
            harm_type="financial loss",
            attack_tactic="hallucination",
            use_case="customer support",
            context="airline customer service",
            severity=SeverityLevel.P2,
            modality="text",
            industry="transportation",
            financial_impact_usd=Decimal("5000.00"),
            legal_defense_cost_usd=Decimal("2500.00"),
            brand_impact_description="Negative media coverage and customer trust issues",
            regulatory_impact="Potential regulatory scrutiny of AI customer service practices",
            base_rate_frequency="medium",
            base_rate_severity="medium-high",
            root_cause="Lack of proper grounding and fact-checking in customer service responses",
            aiuc_safeguard_ids=["AIUC-1.2.1", "AIUC-1.3.2", "AIUC-1.4.1"],
            prevention_measures=["Implement fact-checking", "Add human oversight", "Improve training data"],
            example_prompt="What is your bereavement fare policy?",
            incident_date=date(2024, 2, 15),
            source_url="https://example.com/air-canada-case",
            verified=True,
            is_featured_example=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    
    @pytest.fixture
    def related_tests(self):
        """Create related test taxonomy entries."""
        return [
            TestTaxonomy(
                id="test-001",
                category="hallucinations",
                subcategory="factual_accuracy",
                tactic_type="grounding_failure",
                aiuc_requirement="AIUC-1.2.1",
                framework_section="Safety and Reliability",
                test_description="Test for factual accuracy in customer service responses",
                example_prompt="What is your refund policy for cancelled flights?",
                expected_behavior="Provide accurate, up-to-date policy information",
                related_incident_ids=["air-canada-001"],
                harm_types_addressed=["financial loss", "misinformation"],
                modality="text",
                difficulty_level="intermediate",
                research_references=["https://example.com/hallucination-research"],
                created_at=datetime.utcnow()
            ),
            TestTaxonomy(
                id="test-002",
                category="data_leakage",
                subcategory="policy_information",
                tactic_type="information_extraction",
                aiuc_requirement="AIUC-1.3.2",
                framework_section="Data and Privacy",
                test_description="Test for proper handling of policy information requests",
                example_prompt="Can you tell me about special fare policies?",
                expected_behavior="Provide general information without exposing internal policies",
                related_incident_ids=["air-canada-001"],
                harm_types_addressed=["information disclosure"],
                modality="text",
                difficulty_level="basic",
                research_references=["https://example.com/data-leakage-research"],
                created_at=datetime.utcnow()
            )
        ]
    
    @pytest.fixture
    def mock_session(self):
        """Create mock database session."""
        return AsyncMock()
    
    @pytest.mark.asyncio
    async def test_get_incidents_for_use_case(self, service, mock_session, air_canada_incident):
        """Test retrieving incidents for a specific use case."""
        # Mock repository method
        service.incident_repo.get_by_use_case = AsyncMock(return_value=[air_canada_incident])
        
        # Test the method
        result = await service.get_incidents_for_use_case(
            mock_session, 
            "customer support"
        )
        
        # Assertions
        assert len(result) == 1
        assert result[0].incident_name == "Air Canada Chatbot Misinformation"
        assert result[0].use_case == "customer support"
        service.incident_repo.get_by_use_case.assert_called_once_with(
            mock_session, "customer support", None
        )
    
    @pytest.mark.asyncio
    async def test_get_incidents_for_industry_and_use_case(self, service, mock_session, air_canada_incident):
        """Test retrieving incidents for both industry and use case."""
        # Mock repository method
        service.incident_repo.get_by_industry_and_use_case = AsyncMock(return_value=[air_canada_incident])
        
        # Test the method
        result = await service.get_incidents_for_use_case(
            mock_session, 
            "customer support",
            industry="transportation"
        )
        
        # Assertions
        assert len(result) == 1
        assert result[0].industry == "transportation"
        assert result[0].use_case == "customer support"
        service.incident_repo.get_by_industry_and_use_case.assert_called_once_with(
            mock_session, "transportation", "customer support", None
        )
    
    @pytest.mark.asyncio
    async def test_calculate_base_rate_frequency_and_severity(self, service, mock_session):
        """Test base rate calculation logic."""
        # Mock repository statistics
        mock_stats = {
            "total_incidents": 10,
            "frequency_distribution": {"high": 3, "medium": 4, "low": 3},
            "severity_distribution": {"high": 2, "medium-high": 3, "medium": 3, "low": 2},
            "average_financial_impact": 7500.0
        }
        service.incident_repo.get_base_rate_statistics = AsyncMock(return_value=mock_stats)
        
        # Test the method
        result = await service.calculate_base_rate_frequency_and_severity(
            mock_session,
            industry="transportation",
            use_case="customer support"
        )
        
        # Assertions
        assert isinstance(result, BaseRateCalculation)
        assert result.frequency == "medium"  # Weighted average should be medium
        assert result.severity == "medium-high"  # Weighted average should be medium-high
        assert result.sample_size == 10
        assert result.industry_specific == True
        assert 0.0 <= result.confidence_level <= 1.0
        assert 0.0 <= result.risk_score <= 10.0
    
    @pytest.mark.asyncio
    async def test_calculate_base_rate_no_data(self, service, mock_session):
        """Test base rate calculation with no data."""
        # Mock empty statistics
        mock_stats = {
            "total_incidents": 0,
            "frequency_distribution": {},
            "severity_distribution": {},
            "average_financial_impact": None
        }
        service.incident_repo.get_base_rate_statistics = AsyncMock(return_value=mock_stats)
        
        # Test the method
        result = await service.calculate_base_rate_frequency_and_severity(mock_session)
        
        # Assertions
        assert result.frequency == "low"
        assert result.severity == "low"
        assert result.confidence_level == 0.0
        assert result.sample_size == 0
        assert result.industry_specific == False
    
    @pytest.mark.asyncio
    async def test_link_incidents_to_aiuc_safeguards(self, service, mock_session, air_canada_incident):
        """Test linking incidents to AIUC-1 safeguards."""
        # Mock repository method
        service.incident_repo.get_by_id = AsyncMock(return_value=air_canada_incident)
        
        # Test the method
        result = await service.link_incidents_to_aiuc_safeguards(
            mock_session,
            ["air-canada-001"]
        )
        
        # Assertions
        assert "air-canada-001" in result
        assert result["air-canada-001"] == ["AIUC-1.2.1", "AIUC-1.3.2", "AIUC-1.4.1"]
    
    @pytest.mark.asyncio
    async def test_get_tests_covering_incidents(self, service, mock_session, related_tests):
        """Test getting tests that cover specific incidents."""
        # Mock repository method
        service.taxonomy_repo.get_tests_for_incident = AsyncMock(return_value=related_tests)
        
        # Test the method
        result = await service.get_tests_covering_incidents(
            mock_session,
            ["air-canada-001"]
        )
        
        # Assertions
        assert "air-canada-001" in result
        assert len(result["air-canada-001"]) == 2
        assert result["air-canada-001"][0].category == "hallucinations"
        assert result["air-canada-001"][1].category == "data_leakage"
    
    @pytest.mark.asyncio
    async def test_create_incident_flow_mapping_air_canada(
        self, 
        service, 
        mock_session, 
        air_canada_incident, 
        related_tests
    ):
        """Test creating complete incident flow mapping for Air Canada example."""
        # Mock repository methods
        service.incident_repo.get_by_id = AsyncMock(return_value=air_canada_incident)
        service.taxonomy_repo.get_tests_for_incident = AsyncMock(return_value=related_tests)
        
        # Test the method
        result = await service.create_incident_flow_mapping(
            mock_session,
            "air-canada-001"
        )
        
        # Assertions
        assert isinstance(result, IncidentFlowMapping)
        assert result.incident.incident_name == "Air Canada Chatbot Misinformation"
        assert len(result.related_tests) == 2
        assert len(result.aiuc_safeguards) == 3
        
        # Test flow steps
        flow_steps = result.flow_steps
        assert flow_steps["incident"] == "Air Canada Chatbot Misinformation"
        assert flow_steps["harm"] == "financial loss"
        assert flow_steps["tactic"] == "hallucination"
        assert flow_steps["use_case"] == "customer support"
        assert flow_steps["context"] == "airline customer service"
        
        # Test test coverage
        test_coverage = result.test_coverage
        assert len(test_coverage) == 2
        assert test_coverage[0]["category"] == "hallucinations"
        assert test_coverage[1]["category"] == "data_leakage"
        
        # Test business impact
        business_impact = result.business_impact
        assert business_impact["financial_impact_usd"] == 5000.0
        assert business_impact["legal_defense_cost_usd"] == 2500.0
        assert business_impact["total_financial_impact_usd"] == 7500.0
        assert business_impact["base_rate_frequency"] == "medium"
        assert business_impact["base_rate_severity"] == "medium-high"
    
    @pytest.mark.asyncio
    async def test_get_featured_incident_flows(self, service, mock_session, air_canada_incident, related_tests):
        """Test getting featured incident flows."""
        # Mock repository methods
        service.incident_repo.get_featured_incidents = AsyncMock(return_value=[air_canada_incident])
        service.incident_repo.get_by_id = AsyncMock(return_value=air_canada_incident)
        service.taxonomy_repo.get_tests_for_incident = AsyncMock(return_value=related_tests)
        
        # Test the method
        result = await service.get_featured_incident_flows(mock_session, limit=5)
        
        # Assertions
        assert len(result) == 1
        assert isinstance(result[0], IncidentFlowMapping)
        assert result[0].incident.is_featured_example == True
        assert result[0].incident.incident_name == "Air Canada Chatbot Misinformation"
    
    @pytest.mark.asyncio
    async def test_search_incident_flows(self, service, mock_session, air_canada_incident, related_tests):
        """Test searching incident flows with filters."""
        # Mock repository methods
        service.incident_repo.search_incidents = AsyncMock(return_value=[air_canada_incident])
        service.incident_repo.get_by_id = AsyncMock(return_value=air_canada_incident)
        service.taxonomy_repo.get_tests_for_incident = AsyncMock(return_value=related_tests)
        
        # Test the method
        result = await service.search_incident_flows(
            mock_session,
            industry="transportation",
            use_case="customer support",
            harm_type="financial loss",
            verified_only=True
        )
        
        # Assertions
        assert len(result) == 1
        assert result[0].incident.industry == "transportation"
        assert result[0].incident.use_case == "customer support"
        assert result[0].incident.harm_type == "financial loss"
        
        # Verify search was called with correct parameters
        service.incident_repo.search_incidents.assert_called_once_with(
            session=mock_session,
            industry="transportation",
            use_case="customer support",
            harm_type="financial loss",
            attack_tactic=None,
            severity=None,
            modality=None,
            verified_only=True,
            limit=None
        )
    
    @pytest.mark.asyncio
    async def test_get_aiuc_safeguard_coverage(self, service, mock_session, air_canada_incident, related_tests):
        """Test getting AIUC safeguard coverage information."""
        # Mock repository methods
        service.incident_repo.get_incidents_with_aiuc_safeguards = AsyncMock(return_value=[air_canada_incident])
        service.taxonomy_repo.get_by_aiuc_requirement = AsyncMock(return_value=related_tests)
        
        # Test the method
        result = await service.get_aiuc_safeguard_coverage(
            mock_session,
            "AIUC-1.2.1"
        )
        
        # Assertions
        assert result["aiuc_safeguard_id"] == "AIUC-1.2.1"
        assert result["incidents_addressed"] == 1
        assert result["tests_available"] == 2
        assert "financial loss" in result["harm_types_covered"]
        assert "customer support" in result["use_cases_covered"]
        assert "transportation" in result["industries_covered"]
        
        # Check incident details
        incident_details = result["incident_details"]
        assert len(incident_details) == 1
        assert incident_details[0]["name"] == "Air Canada Chatbot Misinformation"
        assert incident_details[0]["harm_type"] == "financial loss"
        
        # Check test details
        test_details = result["test_details"]
        assert len(test_details) == 2
        assert test_details[0]["category"] == "hallucinations"
        assert test_details[1]["category"] == "data_leakage"


class TestIncidentFlowMapping:
    """Test cases for IncidentFlowMapping class."""
    
    @pytest.fixture
    def air_canada_incident(self):
        """Create Air Canada incident for testing."""
        return AIIncident(
            id="air-canada-001",
            incident_name="Air Canada Chatbot Misinformation",
            harm_type="financial loss",
            attack_tactic="hallucination",
            use_case="customer support",
            context="airline customer service",
            financial_impact_usd=Decimal("5000.00"),
            legal_defense_cost_usd=Decimal("2500.00"),
            base_rate_frequency="medium",
            base_rate_severity="medium-high"
        )
    
    @pytest.fixture
    def related_tests(self):
        """Create related tests for testing."""
        return [
            TestTaxonomy(
                id="test-001",
                category="hallucinations",
                subcategory="factual_accuracy",
                tactic_type="grounding_failure",
                modality="text",
                aiuc_requirement="AIUC-1.2.1"
            )
        ]
    
    def test_flow_steps_property(self, air_canada_incident, related_tests):
        """Test flow_steps property returns correct mapping."""
        mapping = IncidentFlowMapping(
            incident=air_canada_incident,
            related_tests=related_tests,
            aiuc_safeguards=["AIUC-1.2.1"]
        )
        
        flow_steps = mapping.flow_steps
        assert flow_steps["incident"] == "Air Canada Chatbot Misinformation"
        assert flow_steps["harm"] == "financial loss"
        assert flow_steps["tactic"] == "hallucination"
        assert flow_steps["use_case"] == "customer support"
        assert flow_steps["context"] == "airline customer service"
    
    def test_test_coverage_property(self, air_canada_incident, related_tests):
        """Test test_coverage property returns correct information."""
        mapping = IncidentFlowMapping(
            incident=air_canada_incident,
            related_tests=related_tests,
            aiuc_safeguards=["AIUC-1.2.1"]
        )
        
        test_coverage = mapping.test_coverage
        assert len(test_coverage) == 1
        assert test_coverage[0]["category"] == "hallucinations"
        assert test_coverage[0]["subcategory"] == "factual_accuracy"
        assert test_coverage[0]["modality"] == "text"
        assert test_coverage[0]["aiuc_requirement"] == "AIUC-1.2.1"
    
    def test_business_impact_property(self, air_canada_incident, related_tests):
        """Test business_impact property returns correct summary."""
        mapping = IncidentFlowMapping(
            incident=air_canada_incident,
            related_tests=related_tests,
            aiuc_safeguards=["AIUC-1.2.1"]
        )
        
        business_impact = mapping.business_impact
        assert business_impact["financial_impact_usd"] == 5000.0
        assert business_impact["legal_defense_cost_usd"] == 2500.0
        assert business_impact["total_financial_impact_usd"] == 7500.0
        assert business_impact["base_rate_frequency"] == "medium"
        assert business_impact["base_rate_severity"] == "medium-high"


class TestBaseRateCalculation:
    """Test cases for BaseRateCalculation class."""
    
    def test_risk_score_calculation(self):
        """Test risk score calculation logic."""
        # Test high frequency, high severity
        calc_high = BaseRateCalculation(
            frequency="high",
            severity="high",
            confidence_level=1.0,
            sample_size=100
        )
        assert calc_high.risk_score == 9.0  # 3 * 3 * 1.0
        
        # Test medium frequency, medium severity
        calc_medium = BaseRateCalculation(
            frequency="medium",
            severity="medium",
            confidence_level=0.8,
            sample_size=50
        )
        assert calc_medium.risk_score == 3.2  # 2 * 2 * 0.8
        
        # Test low frequency, low severity
        calc_low = BaseRateCalculation(
            frequency="low",
            severity="low",
            confidence_level=0.5,
            sample_size=10
        )
        assert calc_low.risk_score == 0.5  # 1 * 1 * 0.5
    
    def test_risk_score_capped_at_10(self):
        """Test that risk score is capped at 10.0."""
        calc = BaseRateCalculation(
            frequency="high",
            severity="high",
            confidence_level=5.0,  # Artificially high confidence
            sample_size=1000
        )
        assert calc.risk_score == 10.0  # Should be capped at 10.0
    
    def test_unknown_frequency_severity(self):
        """Test handling of unknown frequency/severity values."""
        calc = BaseRateCalculation(
            frequency="unknown",
            severity="unknown",
            confidence_level=1.0,
            sample_size=50
        )
        assert calc.risk_score == 1.0  # Should default to 1.0 for unknown values


# Integration test for Air Canada example validation
class TestAirCanadaExampleValidation:
    """Integration test to validate Air Canada example end-to-end."""
    
    @pytest.mark.asyncio
    async def test_air_canada_complete_flow_validation(self):
        """
        Complete validation of Air Canada example through the incident mapping service.
        
        This test validates:
        1. Air Canada incident data structure
        2. Complete incident → harm → tactic → use case → context → test flow
        3. AIUC-1 safeguard linkage
        4. Base rate calculations
        5. Business impact quantification
        """
        # Create Air Canada incident with complete data
        air_canada = AIIncident(
            id="air-canada-001",
            incident_name="Air Canada Chatbot Misinformation",
            description="Air Canada chatbot provided incorrect information about bereavement fares, "
                       "leading to customer dispute and legal costs of $5,000 plus legal defense costs",
            harm_type="financial loss",
            attack_tactic="hallucination",
            use_case="customer support",
            context="airline customer service - bereavement fare policy inquiry",
            severity=SeverityLevel.P2,
            modality="text",
            industry="transportation",
            financial_impact_usd=Decimal("5000.00"),
            legal_defense_cost_usd=Decimal("2500.00"),
            brand_impact_description="Negative media coverage, customer trust issues, regulatory scrutiny",
            regulatory_impact="Potential regulatory review of AI customer service practices",
            base_rate_frequency="medium",
            base_rate_severity="medium-high",
            root_cause="Lack of proper grounding and fact-checking in customer service responses",
            aiuc_safeguard_ids=["AIUC-1.2.1", "AIUC-1.3.2", "AIUC-1.4.1"],
            prevention_measures=[
                "Implement real-time fact-checking against policy database",
                "Add human oversight for policy-related queries",
                "Improve training data with accurate policy information"
            ],
            example_prompt="What is your bereavement fare policy for immediate family members?",
            incident_date=date(2024, 2, 15),
            source_url="https://example.com/air-canada-chatbot-case",
            verified=True,
            is_featured_example=True
        )
        
        # Validate incident properties
        assert air_canada.incident_name == "Air Canada Chatbot Misinformation"
        assert air_canada.total_financial_impact == Decimal("7500.00")  # 5000 + 2500
        
        # Validate incident flow
        flow = air_canada.incident_flow
        assert flow["incident"] == "Air Canada Chatbot Misinformation"
        assert flow["harm"] == "financial loss"
        assert flow["tactic"] == "hallucination"
        assert flow["use_case"] == "customer support"
        assert flow["context"] == "airline customer service - bereavement fare policy inquiry"
        
        # Validate business impact
        business_impact = air_canada.business_impact_summary
        assert business_impact["financial_impact_usd"] == 5000.0
        assert business_impact["legal_defense_cost_usd"] == 2500.0
        assert business_impact["total_financial_impact_usd"] == 7500.0
        assert business_impact["base_rate_frequency"] == "medium"
        assert business_impact["base_rate_severity"] == "medium-high"
        
        # Validate AIUC safeguard linkage
        assert "AIUC-1.2.1" in air_canada.aiuc_safeguard_ids  # Safety and Reliability
        assert "AIUC-1.3.2" in air_canada.aiuc_safeguard_ids  # Data and Privacy
        assert "AIUC-1.4.1" in air_canada.aiuc_safeguard_ids  # Accountability
        
        # Validate featured example status
        assert air_canada.is_featured_example == True
        assert air_canada.verified == True
        
        print("✅ Air Canada example validation passed - all requirements met")