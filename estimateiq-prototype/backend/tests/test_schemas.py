"""
Schema Behaviour Tests

These tests document and verify the behaviour of EstimateIQ's data models.
The schemas enforce business rules through validation constraints.

Behaviours Documented:
1. Vessel validation: LOA range, year constraints, required fields
2. Service request validation: Required vessel, minimum description length
3. Estimate structure: Proper calculation of totals and ranges
4. Enum constraints: Only valid values accepted for categorical fields
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from app.models import (
    Vessel,
    ServiceRequest,
    Estimate,
    EstimateLineItem,
    EstimateRange,
    SimilarJob,
    HistoricalWorkOrder,
    LaborItem,
    PartItem,
    Part,
    HullType,
    PropulsionType,
    ServiceCategory,
    Urgency,
    EstimateStatus,
    LineType,
    Season,
)


# =============================================================================
# Vessel Model Behaviours
# =============================================================================

class TestVesselBehaviour:
    """
    Vessel model validation behaviours.
    
    The Vessel model enforces constraints that ensure data quality for
    accurate estimate generation based on vessel specifications.
    """
    
    def test_vessel_requires_core_specifications(self):
        """
        A vessel must have LOA, year, engine make, and engine model.
        
        These are the minimum specifications needed for estimate matching.
        """
        vessel = Vessel(
            loa=28.0,
            year=2019,
            engine_make="Volvo Penta",
            engine_model="D4-300",
        )
        
        assert vessel.loa == 28.0
        assert vessel.year == 2019
        assert vessel.engine_make == "Volvo Penta"
        assert vessel.engine_model == "D4-300"
    
    def test_vessel_has_sensible_loa_bounds(self):
        """
        LOA must be between 10 and 200 feet.
        
        This range covers recreational boats through small commercial vessels.
        """
        # Minimum LOA
        small_vessel = Vessel(loa=10.0, year=2020, engine_make="Mercury", engine_model="9.9")
        assert small_vessel.loa == 10.0
        
        # Maximum LOA
        large_vessel = Vessel(loa=200.0, year=2015, engine_make="Caterpillar", engine_model="C32")
        assert large_vessel.loa == 200.0
    
    def test_vessel_rejects_unrealistic_loa(self):
        """
        LOA outside 10-200 feet is rejected as invalid.
        """
        with pytest.raises(ValidationError) as exc_info:
            Vessel(loa=5.0, year=2020, engine_make="Mercury", engine_model="9.9")
        
        assert "loa" in str(exc_info.value)
    
    def test_vessel_year_has_reasonable_bounds(self):
        """
        Year must be between 1950 and 2030.
        
        This allows for vintage vessels while preventing unrealistic future dates.
        """
        vintage_vessel = Vessel(loa=25.0, year=1950, engine_make="Chris-Craft", engine_model="V8")
        assert vintage_vessel.year == 1950
        
        with pytest.raises(ValidationError):
            Vessel(loa=25.0, year=1940, engine_make="Test", engine_model="Test")
    
    def test_vessel_optional_fields_have_defaults(self):
        """
        Optional fields default to sensible values when not provided.
        """
        vessel = Vessel(
            loa=28.0,
            year=2019,
            engine_make="Volvo Penta",
            engine_model="D4-300",
        )
        
        # Optional fields should have defaults or be None
        assert vessel.hull_type == HullType.FIBERGLASS  # Default to most common type
        assert vessel.vessel_id is None
        assert vessel.name is None
    
    def test_vessel_accepts_all_hull_types(self):
        """
        All defined hull types are valid values.
        """
        hull_types = [HullType.FIBERGLASS, HullType.ALUMINUM, HullType.WOOD, HullType.STEEL]
        
        for hull_type in hull_types:
            vessel = Vessel(
                loa=25.0,
                year=2020,
                engine_make="Test",
                engine_model="Test",
                hull_type=hull_type,
            )
            assert vessel.hull_type == hull_type
    
    def test_vessel_accepts_all_propulsion_types(self):
        """
        All defined propulsion types are valid values.
        """
        propulsion_types = [
            PropulsionType.INBOARD,
            PropulsionType.OUTBOARD,
            PropulsionType.STERNDRIVE,
            PropulsionType.JET,
        ]
        
        for prop_type in propulsion_types:
            vessel = Vessel(
                loa=25.0,
                year=2020,
                engine_make="Test",
                engine_model="Test",
                propulsion_type=prop_type,
            )
            assert vessel.propulsion_type == prop_type


# =============================================================================
# Service Request Behaviours
# =============================================================================

class TestServiceRequestBehaviour:
    """
    Service request validation behaviours.
    
    Service requests combine vessel info with service descriptions,
    forming the input for estimate generation.
    """
    
    def test_service_request_requires_vessel_and_description(self, sample_vessel):
        """
        A service request must have a vessel and description.
        """
        request = ServiceRequest(
            vessel=sample_vessel,
            description="Annual oil change and filter replacement",
        )
        
        assert request.vessel == sample_vessel
        assert request.description == "Annual oil change and filter replacement"
    
    def test_description_must_be_meaningful(self, sample_vessel):
        """
        Description must be at least 5 characters to be useful.
        
        Short descriptions don't provide enough context for accurate matching.
        """
        # Valid description
        valid_request = ServiceRequest(
            vessel=sample_vessel,
            description="Oil change",  # 10 chars
        )
        assert len(valid_request.description) >= 5
        
        # Invalid description (too short)
        with pytest.raises(ValidationError):
            ServiceRequest(
                vessel=sample_vessel,
                description="Fix",  # Only 3 chars
            )
    
    def test_service_category_is_optional_but_typed(self, sample_vessel):
        """
        Service category is optional but must be a valid category when provided.
        
        The system can auto-detect category, but explicit category improves accuracy.
        """
        # Without category
        auto_detect = ServiceRequest(
            vessel=sample_vessel,
            description="Oil change needed",
        )
        assert auto_detect.service_category is None
        
        # With valid category
        explicit = ServiceRequest(
            vessel=sample_vessel,
            description="Oil change needed",
            service_category=ServiceCategory.ENGINE,
        )
        assert explicit.service_category == ServiceCategory.ENGINE
    
    def test_urgency_defaults_to_routine(self, sample_vessel):
        """
        Most service requests are routine, so that's the default.
        """
        request = ServiceRequest(
            vessel=sample_vessel,
            description="Annual maintenance",
        )
        assert request.urgency == Urgency.ROUTINE
    
    def test_region_defaults_to_northeast(self, sample_vessel):
        """
        Region defaults to Northeast as the primary market.
        """
        request = ServiceRequest(
            vessel=sample_vessel,
            description="Spring commissioning",
        )
        assert request.region == "Northeast"


# =============================================================================
# Estimate Line Item Behaviours
# =============================================================================

class TestEstimateLineItemBehaviour:
    """
    Estimate line item validation behaviours.
    
    Line items represent individual labor tasks or parts in an estimate.
    """
    
    def test_labor_item_has_hours_and_rate(self):
        """
        Labor items are measured in hours with an hourly rate.
        """
        labor = EstimateLineItem(
            line_type=LineType.LABOR,
            description="Oil and filter change",
            quantity=1.5,
            unit="hours",
            unit_price=125.00,
            total_price=187.50,
            confidence=0.95,
        )
        
        assert labor.line_type == LineType.LABOR
        assert labor.quantity == 1.5
        assert labor.unit == "hours"
        assert labor.unit_price == 125.00
    
    def test_parts_item_has_quantity_and_part_number(self):
        """
        Parts items include part number for catalog validation.
        """
        part = EstimateLineItem(
            line_type=LineType.PARTS,
            description="Oil Filter",
            quantity=1,
            unit="each",
            unit_price=42.99,
            total_price=42.99,
            confidence=0.90,
            part_number="FLT-001",
        )
        
        assert part.line_type == LineType.PARTS
        assert part.part_number == "FLT-001"
    
    def test_confidence_score_is_bounded(self):
        """
        Confidence must be between 0 and 1 (0-100%).
        """
        # Valid confidence
        valid = EstimateLineItem(
            line_type=LineType.LABOR,
            description="Test",
            quantity=1.0,
            unit="hours",
            unit_price=100.00,
            total_price=100.00,
            confidence=0.5,
        )
        assert 0 <= valid.confidence <= 1
        
        # Invalid confidence (over 1)
        with pytest.raises(ValidationError):
            EstimateLineItem(
                line_type=LineType.LABOR,
                description="Test",
                quantity=1.0,
                unit="hours",
                unit_price=100.00,
                total_price=100.00,
                confidence=1.5,
            )
    
    def test_quantities_and_prices_must_be_non_negative(self):
        """
        Negative quantities or prices are invalid.
        """
        with pytest.raises(ValidationError):
            EstimateLineItem(
                line_type=LineType.PARTS,
                description="Test",
                quantity=-1,
                unit="each",
                unit_price=10.00,
                total_price=-10.00,
                confidence=0.5,
            )


# =============================================================================
# Estimate Range Behaviours
# =============================================================================

class TestEstimateRangeBehaviour:
    """
    Estimate range represents low/expected/high projections.
    """
    
    def test_range_captures_estimate_uncertainty(self):
        """
        Range shows low (optimistic), expected, and high (conservative) values.
        """
        estimate_range = EstimateRange(
            low=250.00,
            expected=300.00,
            high=380.00,
        )
        
        assert estimate_range.low < estimate_range.expected
        assert estimate_range.expected < estimate_range.high
    
    def test_range_values_must_be_non_negative(self):
        """
        Estimate values cannot be negative.
        """
        with pytest.raises(ValidationError):
            EstimateRange(
                low=-50.00,
                expected=300.00,
                high=380.00,
            )


# =============================================================================
# Full Estimate Behaviours
# =============================================================================

class TestEstimateBehaviour:
    """
    Complete estimate model behaviours.
    """
    
    def test_estimate_aggregates_labor_and_parts(self, sample_vessel):
        """
        An estimate combines labor items, parts items, and calculates totals.
        """
        labor_items = [
            EstimateLineItem(
                line_type=LineType.LABOR,
                description="Oil change",
                quantity=1.5,
                unit="hours",
                unit_price=125.00,
                total_price=187.50,
                confidence=0.95,
            )
        ]
        
        parts_items = [
            EstimateLineItem(
                line_type=LineType.PARTS,
                description="Oil Filter",
                quantity=1,
                unit="each",
                unit_price=42.99,
                total_price=42.99,
                confidence=0.90,
                part_number="FLT-001",
            )
        ]
        
        estimate = Estimate(
            estimate_id="est_test123",
            vessel=sample_vessel,
            service_description="Oil change",
            labor_items=labor_items,
            parts_items=parts_items,
            labor_subtotal=187.50,
            parts_subtotal=42.99,
            total_estimate=230.49,
            estimate_range=EstimateRange(low=207.44, expected=230.49, high=276.59),
            confidence_score=0.92,
            similar_jobs_count=15,
            similar_jobs_summary="Based on 15 similar jobs",
        )
        
        assert estimate.labor_subtotal == 187.50
        assert estimate.parts_subtotal == 42.99
        assert estimate.total_estimate == estimate.labor_subtotal + estimate.parts_subtotal
    
    def test_estimate_starts_as_draft(self, sample_vessel):
        """
        New estimates start in draft status pending review.
        """
        estimate = Estimate(
            estimate_id="est_test123",
            vessel=sample_vessel,
            service_description="Test",
            labor_items=[],
            parts_items=[],
            labor_subtotal=0,
            parts_subtotal=0,
            total_estimate=0,
            estimate_range=EstimateRange(low=0, expected=0, high=0),
            confidence_score=0.5,
            similar_jobs_count=0,
            similar_jobs_summary="No similar jobs",
        )
        
        assert estimate.status == EstimateStatus.DRAFT
    
    def test_estimate_has_generation_timestamp(self, sample_vessel):
        """
        Estimates are timestamped when generated.
        """
        estimate = Estimate(
            estimate_id="est_test123",
            vessel=sample_vessel,
            service_description="Test",
            labor_items=[],
            parts_items=[],
            labor_subtotal=0,
            parts_subtotal=0,
            total_estimate=0,
            estimate_range=EstimateRange(low=0, expected=0, high=0),
            confidence_score=0.5,
            similar_jobs_count=0,
            similar_jobs_summary="No similar jobs",
        )
        
        assert estimate.generated_at is not None
        assert isinstance(estimate.generated_at, datetime)


# =============================================================================
# Similar Job Behaviours
# =============================================================================

class TestSimilarJobBehaviour:
    """
    Similar job model for RAG retrieval results.
    """
    
    def test_similar_job_has_similarity_score(self):
        """
        Each similar job has a similarity score for ranking.
        """
        job = SimilarJob(
            work_order_id="WO-001",
            similarity_score=0.85,
            vessel_type="Cabin Cruiser",
            loa=28.0,
            engine="Volvo Penta D4-300",
            service_description="Oil change",
            total_labor_hours=1.5,
            total_invoice=250.00,
            completion_date="2024-09-15",
        )
        
        assert 0 <= job.similarity_score <= 1
    
    def test_similar_job_captures_historical_data(self):
        """
        Similar jobs contain key info for estimate generation.
        """
        job = SimilarJob(
            work_order_id="WO-001",
            similarity_score=0.85,
            vessel_type="Cabin Cruiser",
            loa=28.0,
            engine="Volvo Penta D4-300",
            service_description="Oil change",
            total_labor_hours=1.5,
            total_invoice=250.00,
            completion_date="2024-09-15",
        )
        
        # Key data for estimate calculation
        assert job.total_labor_hours > 0
        assert job.total_invoice > 0
        assert job.vessel_type is not None
        assert job.engine is not None


# =============================================================================
# Historical Work Order Behaviours
# =============================================================================

class TestHistoricalWorkOrderBehaviour:
    """
    Historical work order model for training data.
    """
    
    def test_work_order_contains_complete_job_record(self):
        """
        Work orders capture all details of completed jobs.
        """
        labor = LaborItem(task="Oil change", hours=1.5, rate=125.0)
        part = PartItem(part_number="FLT-001", description="Oil Filter", quantity=1, unit_price=42.99)
        
        wo = HistoricalWorkOrder(
            work_order_id="WO-2024-001",
            vessel_type="Cabin Cruiser",
            loa=28.0,
            loa_range="25-30",
            year=2019,
            engine_make="Volvo Penta",
            engine_model="D4-300",
            service_category=ServiceCategory.ENGINE,
            service_description="Annual oil change",
            labor_items=[labor],
            parts_used=[part],
            total_labor_hours=1.5,
            total_parts_cost=42.99,
            total_invoice=230.49,
            completion_date="2024-09-15",
            region="Northeast",
            season=Season.FALL,
        )
        
        assert len(wo.labor_items) > 0
        assert len(wo.parts_used) > 0
        assert wo.total_invoice == wo.total_labor_hours * labor.rate + wo.total_parts_cost


# =============================================================================
# Parts Catalog Behaviours
# =============================================================================

class TestPartBehaviour:
    """
    Parts catalog model behaviours.
    """
    
    def test_part_has_engine_compatibility(self):
        """
        Parts track which engines they're compatible with.
        """
        part = Part(
            part_number="FLT-VP-001",
            description="Volvo Penta Oil Filter",
            category="Filters",
            compatible_engines=["Volvo Penta"],
            list_price=42.99,
            unit="each",
        )
        
        assert "Volvo Penta" in part.compatible_engines
    
    def test_part_price_must_be_non_negative(self):
        """
        Parts cannot have negative prices.
        """
        with pytest.raises(ValidationError):
            Part(
                part_number="TEST-001",
                description="Test Part",
                category="Test",
                list_price=-10.00,
            )
