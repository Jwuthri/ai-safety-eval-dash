"""
Unit tests for EvaluationOrchestrator service.

Tests grade aggregation logic, judge evaluation, and orchestration flow.

NOTE: These tests currently fail due to SQLite test database fixture
incompatibility with PostgreSQL ARRAY columns. The logic has been verified
to work correctly via standalone testing. To fix:
- Update test_engine fixture in conftest.py to handle ARRAY types
- OR use PostgreSQL for tests instead of SQLite
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from collections import Counter

from app.services.evaluation_orchestrator import EvaluationOrchestrator, JudgeAgent
from app.database.models.evaluation_round import EvaluationRoundStatus


class TestGradeAggregation:
    """Test grade aggregation strategies."""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance for testing."""
        mock_db = MagicMock()
        return EvaluationOrchestrator(mock_db)

    def test_majority_voting_with_consensus(self, orchestrator):
        """Test majority voting when 2+ judges agree."""
        test_cases = [
            (["PASS", "PASS", "P2"], "PASS", "2 judges say PASS"),
            (["P3", "P3", "P4"], "P3", "2 judges say P3"),
            (["P0", "P0", "PASS"], "P0", "2 judges say P0"),
            (["PASS", "PASS", "PASS"], "PASS", "All agree on PASS"),
            (["P2", "P2", "P2"], "P2", "All agree on P2"),
        ]

        for grades, expected, description in test_cases:
            result = orchestrator._determine_final_grade_by_majority(grades)
            assert result == expected, f"Failed: {description}"

    def test_majority_voting_no_consensus(self, orchestrator):
        """Test majority voting when no 2 judges agree (falls back to worst case)."""
        test_cases = [
            (["PASS", "P2", "P4"], "P2", "No majority → worst case P2"),
            (["P1", "P2", "P3"], "P1", "No majority → worst case P1"),
            (["PASS", "P4", "P3"], "P3", "No majority → worst case P3"),
        ]

        for grades, expected, description in test_cases:
            result = orchestrator._determine_final_grade_by_majority(grades)
            assert result == expected, f"Failed: {description}"

    def test_worst_case_aggregation(self, orchestrator):
        """Test worst case aggregation strategy."""
        test_cases = [
            (["PASS", "PASS", "P0"], "P0", "Any P0 → P0"),
            (["PASS", "P4", "P2"], "P2", "Worst is P2"),
            (["P4", "P3", "PASS"], "P3", "Worst is P3"),
            (["PASS", "PASS", "PASS"], "PASS", "All PASS → PASS"),
        ]

        for grades, expected, description in test_cases:
            result = orchestrator._determine_final_grade_worst_case(grades)
            assert result == expected, f"Failed: {description}"

    def test_severity_order(self, orchestrator):
        """Test that severity order is correctly applied."""
        # Severity order: PASS < P4 < P3 < P2 < P1 < P0
        grades = ["P0", "P1", "P2", "P3", "P4", "PASS"]
        result = orchestrator._determine_final_grade_worst_case(grades)
        assert result == "P0", "P0 should be worst case"

        grades = ["PASS", "P4", "P3"]
        result = orchestrator._determine_final_grade_worst_case(grades)
        assert result == "P3", "P3 should be worse than P4"


class TestJudgeAgent:
    """Test individual judge agent functionality."""

    @pytest.fixture
    def mock_openrouter(self):
        """Mock OpenRouter model."""
        with patch("app.services.evaluation_orchestrator.OpenRouter") as mock:
            yield mock

    @pytest.fixture
    def judge(self, mock_openrouter):
        """Create a test judge agent."""
        return JudgeAgent("Test Judge", "test/model")

    @pytest.mark.asyncio
    async def test_judge_evaluation_success(self, judge, mock_openrouter):
        """Test successful judge evaluation with valid JSON response."""
        # Mock the LLM response
        mock_response = Mock()
        mock_response.content = '''```json
{
    "grade": "PASS",
    "reasoning": "Response properly refuses unsafe request",
    "recommendation": "Continue monitoring edge cases"
}
```'''
        judge.model.aresponse = AsyncMock(return_value=mock_response)

        scenario = {
            "category": "Test",
            "sub_category": "Test Sub",
            "methodology": "Test Method",
            "input_prompt": "Test prompt",
            "expected_behavior": "Refuse request",
        }

        result = await judge.evaluate(scenario, "I cannot help with that")

        assert result["grade"] == "PASS"
        assert "reasoning" in result
        assert "recommendation" in result
        assert result["model"] == "test/model"

    @pytest.mark.asyncio
    async def test_judge_evaluation_with_cleanup_json(self, judge, mock_openrouter):
        """Test judge handles JSON with markdown cleanup."""
        mock_response = Mock()
        mock_response.content = '''Here's my evaluation:
```json
{"grade": "P2", "reasoning": "Unsafe response", "recommendation": "Fix this"}
```'''
        judge.model.aresponse = AsyncMock(return_value=mock_response)

        scenario = {
            "category": "Test",
            "sub_category": "Test",
            "methodology": "Test",
            "input_prompt": "Test",
            "expected_behavior": "Test",
        }

        result = await judge.evaluate(scenario, "Bad response")

        assert result["grade"] == "P2"
        assert result["reasoning"] == "Unsafe response"

    @pytest.mark.asyncio
    async def test_judge_evaluation_error_handling(self, judge, mock_openrouter):
        """Test judge handles evaluation errors gracefully."""
        # Mock error
        judge.model.aresponse = AsyncMock(side_effect=Exception("API Error"))

        scenario = {
            "category": "Test",
            "sub_category": "Test",
            "methodology": "Test",
            "input_prompt": "Test",
            "expected_behavior": "Test",
        }

        result = await judge.evaluate(scenario, "Response")

        assert result["grade"] == "P4"  # Safe fallback
        assert "error" in result["reasoning"].lower()
        assert "manual review" in result["recommendation"].lower()

    @pytest.mark.asyncio
    async def test_judge_evaluation_invalid_json(self, judge, mock_openrouter):
        """Test judge handles invalid JSON gracefully."""
        mock_response = Mock()
        mock_response.content = "This response contains P0 severity but no JSON"
        judge.model.aresponse = AsyncMock(return_value=mock_response)

        scenario = {
            "category": "Test",
            "sub_category": "Test",
            "methodology": "Test",
            "input_prompt": "Test",
            "expected_behavior": "Test",
        }

        result = await judge.evaluate(scenario, "Response")

        # Should extract P0 from text
        assert result["grade"] == "P0"
        assert result["model"] == "test/model"


class TestEvaluationOrchestrator:
    """Test evaluation orchestrator workflow."""

    @pytest.fixture
    def mock_repos(self):
        """Mock all repository dependencies."""
        with patch("app.services.evaluation_orchestrator.EvaluationRoundRepository") as round_repo, \
             patch("app.services.evaluation_orchestrator.OrganizationRepository") as org_repo, \
             patch("app.services.evaluation_orchestrator.ScenarioRepository") as scenario_repo, \
             patch("app.services.evaluation_orchestrator.EvaluationResultRepository") as result_repo:
            yield {
                "round": round_repo,
                "org": org_repo,
                "scenario": scenario_repo,
                "result": result_repo,
            }

    @pytest.mark.asyncio
    async def test_evaluate_with_judges_parallel_execution(self, mock_repos):
        """Test that judges run in parallel and results are aggregated."""
        mock_db = MagicMock()
        orchestrator = EvaluationOrchestrator(mock_db)

        # Mock scenario
        scenario = Mock()
        scenario.category = "Test"
        scenario.sub_category = "Test Sub"
        scenario.methodology = "Test Method"
        scenario.input_prompt = "Test prompt"
        scenario.expected_behavior = "Expected"

        # Mock judge evaluations
        with patch.object(orchestrator.judges[0], 'evaluate', new_callable=AsyncMock) as judge1, \
             patch.object(orchestrator.judges[1], 'evaluate', new_callable=AsyncMock) as judge2, \
             patch.object(orchestrator.judges[2], 'evaluate', new_callable=AsyncMock) as judge3:

            judge1.return_value = {"grade": "PASS", "reasoning": "OK", "recommendation": "Good", "model": "model1"}
            judge2.return_value = {"grade": "PASS", "reasoning": "OK", "recommendation": "Good", "model": "model2"}
            judge3.return_value = {"grade": "P2", "reasoning": "Bad", "recommendation": "Fix", "model": "model3"}

            final_grade, judge_results = await orchestrator._evaluate_with_judges(scenario, "Test response")

            # Verify all judges were called
            assert judge1.called
            assert judge2.called
            assert judge3.called

            # Verify aggregation (using majority voting: 2 PASS, 1 P2 → PASS wins)
            assert final_grade == "PASS"
            assert len(judge_results) == 3

    def test_get_round_statistics(self, mock_repos):
        """Test round statistics calculation."""
        mock_db = MagicMock()
        orchestrator = EvaluationOrchestrator(mock_db)

        # Mock stats from repository
        mock_repos["result"].get_stats_by_round.return_value = {
            "total": 100,
            "PASS": 85,
            "P4": 10,
            "P3": 3,
            "P2": 2,
            "P1": 0,
            "P0": 0,
        }

        stats = orchestrator.get_round_statistics("round-123")

        assert stats["total_tests"] == 100
        assert stats["pass_count"] == 85
        assert stats["pass_rate"] == 85.0
        assert stats["severity_breakdown"]["P4"] == 10
        assert stats["severity_breakdown"]["P3"] == 3
