"""
Mock LLM Service Behaviour Tests

These tests document and verify the behaviour of the Mock LLM Service.
The service is responsible for:
1. Classifying service requests into categories and types
2. Matching requests to estimate templates
3. Generating labor and parts recommendations
4. Adjusting estimates based on vessel specifications

Behaviours Documented:
1. Service classification from description
2. Template matching with keyword detection
3. Labor recommendation generation
4. Parts recommendation generation
5. LOA-based adjustments
6. Estimate range calculation
"""

import pytest
from pathlib import Path

from app.core.mock_llm import (
    MockLLMService,
    get_mock_llm_service,
    ServiceClassification,
    LaborRecommendation,
    PartRecommendation,
    EstimateRecommendation,
)
from app.models import Vessel, SimilarJob, HullType, PropulsionType


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def mock_llm():
    """Create a fresh mock LLM service instance."""
    return MockLLMService()


@pytest.fixture
def sample_vessel():
    """A standard test vessel."""
    return Vessel(
        loa=28.0,
        year=2019,
        engine_make="Volvo Penta",
        engine_model="D4-300",
        hull_type=HullType.FIBERGLASS,
        propulsion_type=PropulsionType.STERNDRIVE,
    )


@pytest.fixture
def small_vessel():
    """A small vessel for LOA adjustment testing."""
    return Vessel(
        loa=18.0,
        year=2020,
        engine_make="Yamaha",
        engine_model="F150",
        hull_type=HullType.FIBERGLASS,
        propulsion_type=PropulsionType.OUTBOARD,
    )


@pytest.fixture
def large_vessel():
    """A large vessel for LOA adjustment testing."""
    return Vessel(
        loa=45.0,
        year=2015,
        engine_make="Caterpillar",
        engine_model="C9",
        hull_type=HullType.FIBERGLASS,
        propulsion_type=PropulsionType.INBOARD,
    )


@pytest.fixture
def sample_similar_jobs():
    """Sample similar jobs for testing."""
    return [
        SimilarJob(
            work_order_id="WO-001",
            similarity_score=0.9,
            vessel_type="Cabin Cruiser",
            loa=28.0,
            engine="Volvo Penta D4-300",
            service_description="Oil change",
            total_labor_hours=1.5,
            total_invoice=300.0,
            completion_date="2024-09-15",
        ),
        SimilarJob(
            work_order_id="WO-002",
            similarity_score=0.85,
            vessel_type="Cabin Cruiser",
            loa=30.0,
            engine="Volvo Penta D4-260",
            service_description="Oil and filter change",
            total_labor_hours=1.75,
            total_invoice=320.0,
            completion_date="2024-08-20",
        ),
    ]


# =============================================================================
# Service Classification Behaviours
# =============================================================================

class TestServiceClassification:
    """Behaviours related to classifying service requests."""
    
    def test_classifies_oil_change_as_engine(self, mock_llm):
        """
        An oil change request is classified under the engine category.
        """
        classification = mock_llm.classify_service("Annual oil change and filter")
        
        assert classification.category == "engine"
        assert classification.service_type == "oil_change"
    
    def test_classifies_winterization_as_annual(self, mock_llm):
        """
        A winterization request is classified under the annual category.
        """
        classification = mock_llm.classify_service("Full winterization service")
        
        assert classification.category == "annual"
        assert classification.service_type == "winterization"
    
    def test_classifies_bottom_paint_as_hull(self, mock_llm):
        """
        A bottom paint request is classified under the hull category.
        """
        classification = mock_llm.classify_service("Bottom paint and haul out")
        
        assert classification.category == "hull"
        assert classification.service_type == "bottom_paint"
    
    def test_classifies_impeller_as_outboard(self, mock_llm):
        """
        An impeller replacement is classified under the outboard category.
        """
        classification = mock_llm.classify_service("Water pump impeller replacement")
        
        assert classification.category == "outboard"
        assert classification.service_type == "impeller"
    
    def test_returns_general_for_unknown_service(self, mock_llm):
        """
        An unrecognized service description falls back to general category.
        """
        classification = mock_llm.classify_service("Something completely unusual")
        
        assert classification.category == "general"
        assert classification.confidence < 0.6
    
    def test_classification_includes_keyword_matches(self, mock_llm):
        """
        Classification includes the keywords that matched.
        """
        classification = mock_llm.classify_service("oil change service needed")
        
        assert isinstance(classification.keyword_matches, list)
        assert len(classification.keyword_matches) > 0
    
    def test_classification_confidence_based_on_match_quality(self, mock_llm):
        """
        Confidence score reflects match quality.
        """
        # Strong match
        strong_match = mock_llm.classify_service("oil and filter change")
        
        # Weak match
        weak_match = mock_llm.classify_service("general maintenance")
        
        assert strong_match.confidence > weak_match.confidence
    
    def test_respects_provided_category(self, mock_llm):
        """
        When service category is provided, search is limited to that category.
        """
        classification = mock_llm.classify_service(
            "general service needed",
            service_category="engine"
        )
        
        # Should search within engine category even if description is vague
        assert classification.category == "engine"


# =============================================================================
# Estimate Generation Behaviours
# =============================================================================

class TestEstimateGeneration:
    """Behaviours related to generating complete estimates."""
    
    def test_generates_labor_recommendations(
        self, mock_llm, sample_vessel, sample_similar_jobs
    ):
        """
        Estimate generation includes labor recommendations.
        """
        recommendation = mock_llm.generate_estimate(
            service_description="Annual oil change",
            vessel=sample_vessel,
            similar_jobs=sample_similar_jobs,
        )
        
        assert isinstance(recommendation.labor_recommendations, list)
        assert len(recommendation.labor_recommendations) > 0
    
    def test_generates_parts_recommendations(
        self, mock_llm, sample_vessel, sample_similar_jobs
    ):
        """
        Estimate generation includes parts recommendations.
        """
        recommendation = mock_llm.generate_estimate(
            service_description="Annual oil change",
            vessel=sample_vessel,
            similar_jobs=sample_similar_jobs,
        )
        
        assert isinstance(recommendation.parts_recommendations, list)
        assert len(recommendation.parts_recommendations) > 0
    
    def test_labor_recommendations_have_required_fields(
        self, mock_llm, sample_vessel, sample_similar_jobs
    ):
        """
        Each labor recommendation has all required fields.
        """
        recommendation = mock_llm.generate_estimate(
            service_description="Annual oil change",
            vessel=sample_vessel,
            similar_jobs=sample_similar_jobs,
        )
        
        for labor in recommendation.labor_recommendations:
            assert isinstance(labor.description, str)
            assert labor.hours > 0
            assert labor.rate > 0
            assert labor.total > 0
            assert 0 <= labor.confidence <= 1
    
    def test_parts_recommendations_have_required_fields(
        self, mock_llm, sample_vessel, sample_similar_jobs
    ):
        """
        Each parts recommendation has all required fields.
        """
        recommendation = mock_llm.generate_estimate(
            service_description="Annual oil change",
            vessel=sample_vessel,
            similar_jobs=sample_similar_jobs,
        )
        
        for part in recommendation.parts_recommendations:
            assert isinstance(part.category, str)
            assert isinstance(part.part_type, str)
            assert part.quantity > 0
            assert isinstance(part.is_required, bool)
    
    def test_includes_service_classification(
        self, mock_llm, sample_vessel, sample_similar_jobs
    ):
        """
        Estimate includes the service classification.
        """
        recommendation = mock_llm.generate_estimate(
            service_description="Annual oil change",
            vessel=sample_vessel,
            similar_jobs=sample_similar_jobs,
        )
        
        assert recommendation.service_classification is not None
        assert recommendation.service_classification.category == "engine"
    
    def test_calculates_total_hours(
        self, mock_llm, sample_vessel, sample_similar_jobs
    ):
        """
        Estimate includes total estimated hours.
        """
        recommendation = mock_llm.generate_estimate(
            service_description="Annual oil change",
            vessel=sample_vessel,
            similar_jobs=sample_similar_jobs,
        )
        
        expected_total = sum(l.hours for l in recommendation.labor_recommendations)
        assert recommendation.estimated_total_hours == expected_total


# =============================================================================
# LOA Adjustment Behaviours
# =============================================================================

class TestLOAAdjustments:
    """Behaviours related to vessel size adjustments."""
    
    def test_small_vessel_has_lower_labor_hours(
        self, mock_llm, small_vessel, sample_similar_jobs
    ):
        """
        Smaller vessels get reduced labor hour estimates.
        """
        small_estimate = mock_llm.generate_estimate(
            service_description="Annual oil change",
            vessel=small_vessel,
            similar_jobs=[],
        )
        
        # The estimate should have labor hours
        assert small_estimate.estimated_total_hours > 0
    
    def test_large_vessel_has_higher_labor_hours(
        self, mock_llm, large_vessel, sample_vessel, sample_similar_jobs
    ):
        """
        Larger vessels get increased labor hour estimates.
        """
        large_estimate = mock_llm.generate_estimate(
            service_description="Annual oil change",
            vessel=large_vessel,
            similar_jobs=[],
        )
        
        standard_estimate = mock_llm.generate_estimate(
            service_description="Annual oil change",
            vessel=sample_vessel,
            similar_jobs=[],
        )
        
        # Large vessel should have more hours
        assert large_estimate.estimated_total_hours > standard_estimate.estimated_total_hours
    
    def test_loa_affects_hull_services_more(
        self, mock_llm, large_vessel, sample_vessel
    ):
        """
        Hull services (like bottom paint) are more affected by LOA.
        """
        large_hull = mock_llm.generate_estimate(
            service_description="Bottom paint and haul out",
            vessel=large_vessel,
            similar_jobs=[],
        )
        
        standard_hull = mock_llm.generate_estimate(
            service_description="Bottom paint and haul out",
            vessel=sample_vessel,
            similar_jobs=[],
        )
        
        # Large vessel hull work should be significantly more
        ratio = large_hull.estimated_total_hours / standard_hull.estimated_total_hours
        assert ratio > 1.3  # At least 30% more


# =============================================================================
# Similar Jobs Integration Behaviours
# =============================================================================

class TestSimilarJobsIntegration:
    """Behaviours related to using similar job data."""
    
    def test_similar_jobs_increase_confidence(
        self, mock_llm, sample_vessel, sample_similar_jobs
    ):
        """
        Having similar jobs increases estimate confidence.
        """
        with_similar = mock_llm.generate_estimate(
            service_description="Annual oil change",
            vessel=sample_vessel,
            similar_jobs=sample_similar_jobs,
        )
        
        without_similar = mock_llm.generate_estimate(
            service_description="Annual oil change",
            vessel=sample_vessel,
            similar_jobs=[],
        )
        
        assert with_similar.labor_confidence > without_similar.labor_confidence
    
    def test_similar_jobs_influence_labor_hours(
        self, mock_llm, sample_vessel
    ):
        """
        Similar job data influences the labor hour estimates.
        """
        # Create similar jobs with specific labor hours
        similar_with_low_hours = [
            SimilarJob(
                work_order_id="WO-001",
                similarity_score=0.9,
                vessel_type="Cabin Cruiser",
                loa=28.0,
                engine="Volvo Penta D4-300",
                service_description="Oil change",
                total_labor_hours=1.0,
                total_invoice=200.0,
                completion_date="2024-09-15",
            ),
            SimilarJob(
                work_order_id="WO-002",
                similarity_score=0.85,
                vessel_type="Cabin Cruiser",
                loa=28.0,
                engine="Volvo Penta D4-300",
                service_description="Oil change",
                total_labor_hours=1.0,
                total_invoice=200.0,
                completion_date="2024-08-15",
            ),
            SimilarJob(
                work_order_id="WO-003",
                similarity_score=0.8,
                vessel_type="Cabin Cruiser",
                loa=28.0,
                engine="Volvo Penta D4-300",
                service_description="Oil change",
                total_labor_hours=1.0,
                total_invoice=200.0,
                completion_date="2024-07-15",
            ),
        ]
        
        estimate = mock_llm.generate_estimate(
            service_description="Annual oil change",
            vessel=sample_vessel,
            similar_jobs=similar_with_low_hours,
        )
        
        # Should be influenced by the similar jobs' low hours
        assert estimate.estimated_total_hours > 0


# =============================================================================
# Estimate Range Calculation Behaviours
# =============================================================================

class TestEstimateRangeCalculation:
    """Behaviours related to calculating estimate ranges."""
    
    def test_calculates_low_expected_high(self, mock_llm, sample_similar_jobs):
        """
        Calculates low, expected, and high estimates.
        """
        low, expected, high = mock_llm.calculate_estimate_range(
            base_total=500.0,
            confidence=0.85,
            similar_jobs=sample_similar_jobs,
        )
        
        assert low < expected
        assert expected < high
    
    def test_range_widens_with_lower_confidence(self, mock_llm, sample_similar_jobs):
        """
        Lower confidence results in wider estimate range.
        """
        low_conf_low, _, low_conf_high = mock_llm.calculate_estimate_range(
            base_total=500.0,
            confidence=0.5,
            similar_jobs=sample_similar_jobs,
        )
        
        high_conf_low, _, high_conf_high = mock_llm.calculate_estimate_range(
            base_total=500.0,
            confidence=0.95,
            similar_jobs=sample_similar_jobs,
        )
        
        low_conf_range = low_conf_high - low_conf_low
        high_conf_range = high_conf_high - high_conf_low
        
        assert low_conf_range > high_conf_range
    
    def test_range_based_on_similar_jobs_variance(self, mock_llm):
        """
        Range is influenced by variance in similar jobs.
        """
        # High variance similar jobs
        high_variance_jobs = [
            SimilarJob(
                work_order_id="WO-001",
                similarity_score=0.9,
                vessel_type="Cabin Cruiser",
                loa=28.0,
                engine="Volvo Penta",
                service_description="Oil change",
                total_labor_hours=1.0,
                total_invoice=200.0,
                completion_date="2024-09-15",
            ),
            SimilarJob(
                work_order_id="WO-002",
                similarity_score=0.85,
                vessel_type="Cabin Cruiser",
                loa=28.0,
                engine="Volvo Penta",
                service_description="Oil change",
                total_labor_hours=1.0,
                total_invoice=600.0,  # Very different
                completion_date="2024-08-15",
            ),
        ]
        
        # Low variance similar jobs
        low_variance_jobs = [
            SimilarJob(
                work_order_id="WO-003",
                similarity_score=0.9,
                vessel_type="Cabin Cruiser",
                loa=28.0,
                engine="Volvo Penta",
                service_description="Oil change",
                total_labor_hours=1.0,
                total_invoice=300.0,
                completion_date="2024-09-15",
            ),
            SimilarJob(
                work_order_id="WO-004",
                similarity_score=0.85,
                vessel_type="Cabin Cruiser",
                loa=28.0,
                engine="Volvo Penta",
                service_description="Oil change",
                total_labor_hours=1.0,
                total_invoice=310.0,  # Very similar
                completion_date="2024-08-15",
            ),
        ]
        
        high_var_low, _, high_var_high = mock_llm.calculate_estimate_range(
            base_total=500.0,
            confidence=0.8,
            similar_jobs=high_variance_jobs,
        )
        
        low_var_low, _, low_var_high = mock_llm.calculate_estimate_range(
            base_total=500.0,
            confidence=0.8,
            similar_jobs=low_variance_jobs,
        )
        
        high_var_range = high_var_high - high_var_low
        low_var_range = low_var_high - low_var_low
        
        assert high_var_range > low_var_range


# =============================================================================
# Singleton Instance Behaviours
# =============================================================================

class TestSingletonInstance:
    """Behaviours of the global singleton instance."""
    
    def test_returns_same_instance(self):
        """
        get_mock_llm_service returns the same instance each time.
        """
        service1 = get_mock_llm_service()
        service2 = get_mock_llm_service()
        
        assert service1 is service2
    
    def test_instance_is_functional(self, sample_vessel):
        """
        The singleton instance is fully functional.
        """
        service = get_mock_llm_service()
        
        classification = service.classify_service("oil change")
        assert classification is not None
        
        recommendation = service.generate_estimate(
            service_description="oil change",
            vessel=sample_vessel,
            similar_jobs=[],
        )
        assert recommendation is not None
