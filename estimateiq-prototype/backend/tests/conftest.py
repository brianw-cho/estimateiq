"""
EstimateIQ Test Configuration

Shared fixtures and configuration for the test suite.
"""

import pytest
import sys
import tempfile
import shutil
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models import (
    Vessel,
    ServiceRequest,
    Estimate,
    EstimateLineItem,
    EstimateRange,
    SimilarJob,
    HullType,
    PropulsionType,
    ServiceCategory,
    Urgency,
    LineType,
)


# =============================================================================
# Sample Vessel Fixtures
# =============================================================================

@pytest.fixture
def sample_vessel() -> Vessel:
    """
    A standard cabin cruiser vessel for testing.
    
    Represents a typical mid-size vessel with common specifications:
    - 28' length (common size for cabin cruisers)
    - Volvo Penta D4-300 (popular marine diesel)
    - 2019 model year
    """
    return Vessel(
        vessel_id="V-TEST-001",
        name="Test Vessel",
        loa=28.0,
        beam=9.5,
        year=2019,
        engine_make="Volvo Penta",
        engine_model="D4-300",
        hull_type=HullType.FIBERGLASS,
        propulsion_type=PropulsionType.STERNDRIVE,
    )


@pytest.fixture
def small_outboard_vessel() -> Vessel:
    """
    A small outboard-powered runabout.
    
    Represents entry-level recreational boats with outboard motors.
    """
    return Vessel(
        loa=18.0,
        year=2020,
        engine_make="Yamaha",
        engine_model="F150",
        hull_type=HullType.FIBERGLASS,
        propulsion_type=PropulsionType.OUTBOARD,
    )


@pytest.fixture
def large_inboard_vessel() -> Vessel:
    """
    A large sailboat with inboard diesel.
    
    Represents larger vessels with different service requirements.
    """
    return Vessel(
        vessel_id="V-TEST-003",
        name="Wind Dancer",
        loa=42.0,
        beam=12.5,
        year=2012,
        engine_make="Yanmar",
        engine_model="4JH5E",
        hull_type=HullType.FIBERGLASS,
        propulsion_type=PropulsionType.INBOARD,
    )


# =============================================================================
# Service Request Fixtures
# =============================================================================

@pytest.fixture
def oil_change_request(sample_vessel) -> ServiceRequest:
    """
    A routine oil change service request.
    
    This is the most common marine service - should have high confidence matches.
    """
    return ServiceRequest(
        vessel=sample_vessel,
        description="Annual oil change and filter replacement",
        service_category=ServiceCategory.ENGINE,
        urgency=Urgency.ROUTINE,
        region="Northeast",
    )


@pytest.fixture
def winterization_request(sample_vessel) -> ServiceRequest:
    """
    A seasonal winterization service request.
    
    Common annual service with predictable parts and labor.
    """
    return ServiceRequest(
        vessel=sample_vessel,
        description="Full winterization service including engine, water systems, and fuel stabilizer",
        service_category=ServiceCategory.ANNUAL,
        urgency=Urgency.ROUTINE,
        region="Northeast",
    )


@pytest.fixture
def diagnostic_request(sample_vessel) -> ServiceRequest:
    """
    A troubleshooting/diagnostic service request.
    
    Less predictable service - should have lower confidence scores.
    """
    return ServiceRequest(
        vessel=sample_vessel,
        description="Engine running rough at idle, occasional stalling",
        service_category=ServiceCategory.DIAGNOSTIC,
        urgency=Urgency.PRIORITY,
        region="Northeast",
    )


# =============================================================================
# Sample Work Order Fixtures
# =============================================================================

@pytest.fixture
def sample_work_order() -> dict:
    """
    A sample historical work order for testing RAG functionality.
    """
    return {
        "work_order_id": "WO-TEST-001",
        "vessel_type": "Cabin Cruiser",
        "loa": 28.5,
        "loa_range": "25-30",
        "year": 2019,
        "engine_make": "Volvo Penta",
        "engine_model": "D4-300",
        "service_category": "engine",
        "service_description": "Oil and filter change",
        "labor_items": [
            {"task": "Oil and filter change", "hours": 1.5, "rate": 125.0}
        ],
        "parts_used": [
            {"part_number": "FLT-001", "description": "Oil Filter", "quantity": 1, "unit_price": 42.99},
            {"part_number": "OIL-001", "description": "Engine Oil 15W-40", "quantity": 2, "unit_price": 32.99},
        ],
        "total_labor_hours": 1.5,
        "total_parts_cost": 108.97,
        "total_invoice": 296.47,
        "completion_date": "2024-09-15",
        "region": "Northeast",
        "season": "fall",
    }


@pytest.fixture
def sample_work_orders() -> list:
    """
    A collection of sample work orders for batch testing.
    """
    return [
        {
            "work_order_id": "WO-TEST-001",
            "vessel_type": "Cabin Cruiser",
            "loa": 28.0,
            "loa_range": "25-30",
            "year": 2019,
            "engine_make": "Volvo Penta",
            "engine_model": "D4-300",
            "service_category": "engine",
            "service_description": "Oil and filter change",
            "labor_items": [{"task": "Oil change", "hours": 1.5, "rate": 125.0}],
            "parts_used": [{"part_number": "FLT-001", "description": "Oil Filter", "quantity": 1, "unit_price": 42.99}],
            "total_labor_hours": 1.5,
            "total_parts_cost": 42.99,
            "total_invoice": 230.49,
            "completion_date": "2024-09-15",
            "region": "Northeast",
            "season": "fall",
        },
        {
            "work_order_id": "WO-TEST-002",
            "vessel_type": "Center Console",
            "loa": 24.0,
            "loa_range": "20-25",
            "year": 2020,
            "engine_make": "Yamaha",
            "engine_model": "F250",
            "service_category": "outboard",
            "service_description": "Lower unit service and impeller replacement",
            "labor_items": [{"task": "Lower unit service", "hours": 2.5, "rate": 125.0}],
            "parts_used": [{"part_number": "IMP-001", "description": "Impeller", "quantity": 1, "unit_price": 65.00}],
            "total_labor_hours": 2.5,
            "total_parts_cost": 65.00,
            "total_invoice": 377.50,
            "completion_date": "2024-08-20",
            "region": "Southeast",
            "season": "summer",
        },
        {
            "work_order_id": "WO-TEST-003",
            "vessel_type": "Runabout",
            "loa": 22.0,
            "loa_range": "20-25",
            "year": 2018,
            "engine_make": "MerCruiser",
            "engine_model": "4.3L MPI",
            "service_category": "annual",
            "service_description": "Winterization",
            "labor_items": [{"task": "Winterization", "hours": 3.0, "rate": 125.0}],
            "parts_used": [
                {"part_number": "ANT-001", "description": "Antifreeze", "quantity": 4, "unit_price": 12.99},
                {"part_number": "STA-001", "description": "Fuel Stabilizer", "quantity": 1, "unit_price": 18.99},
            ],
            "total_labor_hours": 3.0,
            "total_parts_cost": 70.95,
            "total_invoice": 445.95,
            "completion_date": "2024-11-10",
            "region": "Northeast",
            "season": "fall",
        },
    ]


# =============================================================================
# Similar Job Fixtures
# =============================================================================

@pytest.fixture
def sample_similar_jobs() -> list:
    """
    A list of similar jobs for testing confidence scoring.
    """
    return [
        SimilarJob(
            work_order_id="WO-001",
            similarity_score=0.95,
            vessel_type="Cabin Cruiser",
            loa=28.0,
            engine="Volvo Penta D4-300",
            service_description="Oil and filter change",
            total_labor_hours=1.5,
            total_invoice=296.47,
            completion_date="2024-09-15",
        ),
        SimilarJob(
            work_order_id="WO-002",
            similarity_score=0.88,
            vessel_type="Cabin Cruiser",
            loa=30.0,
            engine="Volvo Penta D4-260",
            service_description="Oil change with filter",
            total_labor_hours=1.75,
            total_invoice=312.00,
            completion_date="2024-08-20",
        ),
        SimilarJob(
            work_order_id="WO-003",
            similarity_score=0.82,
            vessel_type="Center Console",
            loa=26.0,
            engine="Yamaha F250",
            service_description="Oil and filter service",
            total_labor_hours=1.25,
            total_invoice=245.00,
            completion_date="2024-07-10",
        ),
    ]


# =============================================================================
# Temporary Directory Fixtures
# =============================================================================

@pytest.fixture
def temp_chroma_dir():
    """
    Create a temporary directory for ChromaDB during tests.
    
    This ensures tests don't interfere with production data.
    """
    temp_dir = tempfile.mkdtemp(prefix="estimateiq_test_")
    yield temp_dir
    # Cleanup after test
    shutil.rmtree(temp_dir, ignore_errors=True)
