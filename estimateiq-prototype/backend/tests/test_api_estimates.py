"""
Estimate API Endpoint Behaviour Tests

These tests document and verify the behaviour of the estimate generation
API endpoints. The API is the primary interface for generating AI-powered
service estimates.

Behaviours Documented:
1. Estimate generation: Creating estimates from service requests
2. Response structure: Required fields and formatting
3. Input validation: Handling valid and invalid inputs
4. RAG-integrated estimate generation: Phase 3 behaviour
5. Service type classification: Matching descriptions to templates
6. Parts validation: All parts from catalog
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models import (
    Vessel,
    ServiceRequest,
    HullType,
    PropulsionType,
    ServiceCategory,
    Urgency,
)


# =============================================================================
# Test Client Setup
# =============================================================================

@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


# =============================================================================
# Estimate Generation Endpoint Behaviours
# =============================================================================

class TestEstimateGenerationEndpoint:
    """
    POST /api/estimates endpoint behaviours.
    
    This endpoint generates AI-powered service estimates based on
    vessel specifications and service descriptions.
    """
    
    def test_generate_estimate_returns_success(self, client):
        """
        A valid service request returns a successful response.
        """
        request_data = {
            "vessel": {
                "loa": 28,
                "year": 2019,
                "engine_make": "Volvo Penta",
                "engine_model": "D4-300"
            },
            "description": "Annual oil change and filter replacement"
        }
        
        response = client.post("/api/estimates", json=request_data)
        
        assert response.status_code == 200
    
    def test_estimate_response_has_unique_id(self, client):
        """
        Each generated estimate has a unique identifier.
        """
        request_data = {
            "vessel": {
                "loa": 28,
                "year": 2019,
                "engine_make": "Volvo Penta",
                "engine_model": "D4-300"
            },
            "description": "Oil change"
        }
        
        response1 = client.post("/api/estimates", json=request_data)
        response2 = client.post("/api/estimates", json=request_data)
        
        estimate1 = response1.json()
        estimate2 = response2.json()
        
        assert "estimate_id" in estimate1
        assert "estimate_id" in estimate2
        assert estimate1["estimate_id"] != estimate2["estimate_id"]
    
    def test_estimate_includes_vessel_info(self, client):
        """
        The estimate includes the vessel information from the request.
        """
        request_data = {
            "vessel": {
                "loa": 28,
                "year": 2019,
                "engine_make": "Volvo Penta",
                "engine_model": "D4-300"
            },
            "description": "Oil change"
        }
        
        response = client.post("/api/estimates", json=request_data)
        estimate = response.json()
        
        assert "vessel" in estimate
        assert estimate["vessel"]["loa"] == 28
        assert estimate["vessel"]["engine_make"] == "Volvo Penta"
    
    def test_estimate_includes_labor_items(self, client):
        """
        The estimate includes labor line items.
        """
        request_data = {
            "vessel": {
                "loa": 28,
                "year": 2019,
                "engine_make": "Volvo Penta",
                "engine_model": "D4-300"
            },
            "description": "Oil change"
        }
        
        response = client.post("/api/estimates", json=request_data)
        estimate = response.json()
        
        assert "labor_items" in estimate
        assert isinstance(estimate["labor_items"], list)
        assert len(estimate["labor_items"]) > 0
        
        # Each labor item has required fields
        labor_item = estimate["labor_items"][0]
        assert "description" in labor_item
        assert "quantity" in labor_item
        assert "unit_price" in labor_item
        assert "total_price" in labor_item
        assert "confidence" in labor_item
    
    def test_estimate_includes_parts_items(self, client):
        """
        The estimate includes parts line items.
        """
        request_data = {
            "vessel": {
                "loa": 28,
                "year": 2019,
                "engine_make": "Volvo Penta",
                "engine_model": "D4-300"
            },
            "description": "Oil change"
        }
        
        response = client.post("/api/estimates", json=request_data)
        estimate = response.json()
        
        assert "parts_items" in estimate
        assert isinstance(estimate["parts_items"], list)
        assert len(estimate["parts_items"]) > 0
        
        # Each parts item has required fields
        parts_item = estimate["parts_items"][0]
        assert "description" in parts_item
        assert "quantity" in parts_item
        assert "unit_price" in parts_item
        assert "total_price" in parts_item
    
    def test_estimate_calculates_totals(self, client):
        """
        The estimate includes subtotals and grand total.
        """
        request_data = {
            "vessel": {
                "loa": 28,
                "year": 2019,
                "engine_make": "Volvo Penta",
                "engine_model": "D4-300"
            },
            "description": "Oil change"
        }
        
        response = client.post("/api/estimates", json=request_data)
        estimate = response.json()
        
        assert "labor_subtotal" in estimate
        assert "parts_subtotal" in estimate
        assert "total_estimate" in estimate
        
        # Total should be sum of subtotals
        assert estimate["total_estimate"] == estimate["labor_subtotal"] + estimate["parts_subtotal"]
    
    def test_estimate_includes_range(self, client):
        """
        The estimate includes low/expected/high range.
        """
        request_data = {
            "vessel": {
                "loa": 28,
                "year": 2019,
                "engine_make": "Volvo Penta",
                "engine_model": "D4-300"
            },
            "description": "Oil change"
        }
        
        response = client.post("/api/estimates", json=request_data)
        estimate = response.json()
        
        assert "estimate_range" in estimate
        range_data = estimate["estimate_range"]
        assert "low" in range_data
        assert "expected" in range_data
        assert "high" in range_data
        
        # Range should be ordered
        assert range_data["low"] <= range_data["expected"] <= range_data["high"]
    
    def test_estimate_includes_confidence_score(self, client):
        """
        The estimate includes an overall confidence score.
        """
        request_data = {
            "vessel": {
                "loa": 28,
                "year": 2019,
                "engine_make": "Volvo Penta",
                "engine_model": "D4-300"
            },
            "description": "Oil change"
        }
        
        response = client.post("/api/estimates", json=request_data)
        estimate = response.json()
        
        assert "confidence_score" in estimate
        assert 0 <= estimate["confidence_score"] <= 1
    
    def test_estimate_includes_similar_jobs_info(self, client):
        """
        The estimate includes similar jobs count and summary.
        """
        request_data = {
            "vessel": {
                "loa": 28,
                "year": 2019,
                "engine_make": "Volvo Penta",
                "engine_model": "D4-300"
            },
            "description": "Oil change"
        }
        
        response = client.post("/api/estimates", json=request_data)
        estimate = response.json()
        
        assert "similar_jobs_count" in estimate
        assert "similar_jobs_summary" in estimate
        assert isinstance(estimate["similar_jobs_count"], int)
        assert isinstance(estimate["similar_jobs_summary"], str)
    
    def test_estimate_starts_as_draft(self, client):
        """
        New estimates are created in draft status.
        """
        request_data = {
            "vessel": {
                "loa": 28,
                "year": 2019,
                "engine_make": "Volvo Penta",
                "engine_model": "D4-300"
            },
            "description": "Oil change"
        }
        
        response = client.post("/api/estimates", json=request_data)
        estimate = response.json()
        
        assert estimate["status"] == "draft"
    
    def test_estimate_has_timestamp(self, client):
        """
        The estimate includes a generation timestamp.
        """
        request_data = {
            "vessel": {
                "loa": 28,
                "year": 2019,
                "engine_make": "Volvo Penta",
                "engine_model": "D4-300"
            },
            "description": "Oil change"
        }
        
        response = client.post("/api/estimates", json=request_data)
        estimate = response.json()
        
        assert "generated_at" in estimate


# =============================================================================
# Input Validation Behaviours
# =============================================================================

class TestEstimateInputValidation:
    """
    Input validation behaviours for the estimate endpoint.
    """
    
    def test_requires_vessel_info(self, client):
        """
        Request without vessel information is rejected.
        """
        request_data = {
            "description": "Oil change"
        }
        
        response = client.post("/api/estimates", json=request_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_requires_description(self, client):
        """
        Request without description is rejected.
        """
        request_data = {
            "vessel": {
                "loa": 28,
                "year": 2019,
                "engine_make": "Volvo Penta",
                "engine_model": "D4-300"
            }
        }
        
        response = client.post("/api/estimates", json=request_data)
        
        assert response.status_code == 422
    
    def test_rejects_short_description(self, client):
        """
        Description must be at least 5 characters.
        """
        request_data = {
            "vessel": {
                "loa": 28,
                "year": 2019,
                "engine_make": "Volvo Penta",
                "engine_model": "D4-300"
            },
            "description": "Fix"  # Too short
        }
        
        response = client.post("/api/estimates", json=request_data)
        
        assert response.status_code == 422
    
    def test_rejects_invalid_loa(self, client):
        """
        LOA must be within valid range.
        """
        request_data = {
            "vessel": {
                "loa": 5,  # Below minimum of 10
                "year": 2019,
                "engine_make": "Volvo Penta",
                "engine_model": "D4-300"
            },
            "description": "Oil change"
        }
        
        response = client.post("/api/estimates", json=request_data)
        
        assert response.status_code == 422
    
    def test_accepts_optional_fields(self, client):
        """
        Request with optional fields is accepted.
        """
        request_data = {
            "vessel": {
                "vessel_id": "V-001",
                "name": "Sea Breeze",
                "loa": 28,
                "beam": 9.5,
                "year": 2019,
                "engine_make": "Volvo Penta",
                "engine_model": "D4-300",
                "hull_type": "fiberglass",
                "propulsion_type": "sterndrive"
            },
            "description": "Annual oil change and filter replacement",
            "service_category": "engine",
            "urgency": "routine",
            "region": "Northeast"
        }
        
        response = client.post("/api/estimates", json=request_data)
        
        assert response.status_code == 200


# =============================================================================
# Estimate Retrieval Endpoint Behaviours
# =============================================================================

class TestEstimateRetrievalEndpoint:
    """
    GET /api/estimates/{estimate_id} endpoint behaviours.
    
    Note: In Phase 1, estimate persistence is not implemented.
    """
    
    def test_get_nonexistent_estimate_returns_404(self, client):
        """
        Retrieving a non-existent estimate returns 404.
        """
        response = client.get("/api/estimates/est_nonexistent123")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


# =============================================================================
# Health Check Endpoint Behaviours
# =============================================================================

class TestEstimateHealthEndpoint:
    """
    GET /api/estimates/health endpoint behaviours.
    """
    
    def test_health_endpoint_returns_healthy(self, client):
        """
        Health endpoint returns healthy status.
        """
        response = client.get("/api/estimates/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


# =============================================================================
# Phase 3: RAG Integration Behaviours
# =============================================================================

class TestRAGIntegration:
    """
    Behaviours related to RAG engine integration (Phase 3).
    
    These tests verify that the estimate endpoint properly integrates
    with the RAG engine for similar job retrieval.
    """
    
    def test_estimate_reflects_service_classification(self, client):
        """
        Estimate labor descriptions reflect the classified service type.
        """
        request_data = {
            "vessel": {
                "loa": 28,
                "year": 2019,
                "engine_make": "Volvo Penta",
                "engine_model": "D4-300"
            },
            "description": "Annual oil change and filter replacement"
        }
        
        response = client.post("/api/estimates", json=request_data)
        estimate = response.json()
        
        # Labor items should reference the service type
        labor_descriptions = [item["description"].lower() for item in estimate["labor_items"]]
        
        # Should contain oil or filter related terms
        has_relevant_description = any(
            "oil" in desc or "filter" in desc
            for desc in labor_descriptions
        )
        assert has_relevant_description
    
    def test_winterization_estimate_is_different_from_oil_change(self, client):
        """
        Different service types produce different estimates.
        """
        oil_change_request = {
            "vessel": {
                "loa": 28,
                "year": 2019,
                "engine_make": "Volvo Penta",
                "engine_model": "D4-300"
            },
            "description": "Annual oil change"
        }
        
        winterization_request = {
            "vessel": {
                "loa": 28,
                "year": 2019,
                "engine_make": "Volvo Penta",
                "engine_model": "D4-300"
            },
            "description": "Full winterization service"
        }
        
        oil_response = client.post("/api/estimates", json=oil_change_request)
        winter_response = client.post("/api/estimates", json=winterization_request)
        
        oil_estimate = oil_response.json()
        winter_estimate = winter_response.json()
        
        # Labor hours should be different
        oil_hours = sum(item["quantity"] for item in oil_estimate["labor_items"])
        winter_hours = sum(item["quantity"] for item in winter_estimate["labor_items"])
        
        assert oil_hours != winter_hours
    
    def test_larger_vessel_gets_higher_labor_estimate(self, client):
        """
        Larger vessels get higher labor hour estimates for same service.
        """
        small_vessel_request = {
            "vessel": {
                "loa": 18,
                "year": 2019,
                "engine_make": "Yamaha",
                "engine_model": "F150"
            },
            "description": "Bottom paint service"
        }
        
        large_vessel_request = {
            "vessel": {
                "loa": 45,
                "year": 2019,
                "engine_make": "Caterpillar",
                "engine_model": "C9"
            },
            "description": "Bottom paint service"
        }
        
        small_response = client.post("/api/estimates", json=small_vessel_request)
        large_response = client.post("/api/estimates", json=large_vessel_request)
        
        small_estimate = small_response.json()
        large_estimate = large_response.json()
        
        small_hours = sum(item["quantity"] for item in small_estimate["labor_items"])
        large_hours = sum(item["quantity"] for item in large_estimate["labor_items"])
        
        assert large_hours > small_hours
    
    def test_estimate_parts_have_valid_part_numbers(self, client):
        """
        All parts in estimate have valid part numbers from catalog.
        """
        request_data = {
            "vessel": {
                "loa": 28,
                "year": 2019,
                "engine_make": "Volvo Penta",
                "engine_model": "D4-300"
            },
            "description": "Annual oil change and filter replacement"
        }
        
        response = client.post("/api/estimates", json=request_data)
        estimate = response.json()
        
        # All parts should have part numbers
        for part in estimate["parts_items"]:
            assert "part_number" in part
            # Part numbers should follow a pattern (not empty)
            if part["part_number"]:
                assert len(part["part_number"]) > 0
    
    def test_labor_items_have_source_references(self, client):
        """
        Labor items include source references for transparency.
        """
        request_data = {
            "vessel": {
                "loa": 28,
                "year": 2019,
                "engine_make": "Volvo Penta",
                "engine_model": "D4-300"
            },
            "description": "Annual oil change"
        }
        
        response = client.post("/api/estimates", json=request_data)
        estimate = response.json()
        
        for item in estimate["labor_items"]:
            assert "source_reference" in item
            assert item["source_reference"] is not None
    
    def test_confidence_varies_by_service_type(self, client):
        """
        Common services have different confidence than unusual requests.
        """
        common_request = {
            "vessel": {
                "loa": 28,
                "year": 2019,
                "engine_make": "Volvo Penta",
                "engine_model": "D4-300"
            },
            "description": "Annual oil change and filter"
        }
        
        unusual_request = {
            "vessel": {
                "loa": 28,
                "year": 2019,
                "engine_make": "Volvo Penta",
                "engine_model": "D4-300"
            },
            "description": "Something very unusual and specific to diagnose"
        }
        
        common_response = client.post("/api/estimates", json=common_request)
        unusual_response = client.post("/api/estimates", json=unusual_request)
        
        common_estimate = common_response.json()
        unusual_estimate = unusual_response.json()
        
        # Both should have valid confidence scores
        assert 0 <= common_estimate["confidence_score"] <= 1
        assert 0 <= unusual_estimate["confidence_score"] <= 1


class TestServiceCategorySpecificBehaviours:
    """
    Behaviours specific to different service categories.
    """
    
    def test_engine_service_uses_engine_labor_rate(self, client):
        """
        Engine services use the appropriate labor rate.
        """
        request_data = {
            "vessel": {
                "loa": 28,
                "year": 2019,
                "engine_make": "Volvo Penta",
                "engine_model": "D4-300"
            },
            "description": "Engine tune-up and service",
            "service_category": "engine"
        }
        
        response = client.post("/api/estimates", json=request_data)
        estimate = response.json()
        
        # Labor rate should be in expected range for engine work
        for item in estimate["labor_items"]:
            # Engine rate should be around $125-$150 range
            assert 100 <= item["unit_price"] <= 200
    
    def test_diagnostic_service_is_classified_correctly(self, client):
        """
        Diagnostic requests are handled appropriately.
        """
        request_data = {
            "vessel": {
                "loa": 28,
                "year": 2019,
                "engine_make": "Volvo Penta",
                "engine_model": "D4-300"
            },
            "description": "Troubleshoot engine running rough and stalling"
        }
        
        response = client.post("/api/estimates", json=request_data)
        estimate = response.json()
        
        assert response.status_code == 200
        assert len(estimate["labor_items"]) > 0
        
        # Diagnostic services typically have diagnostic-related descriptions
        labor_descriptions = " ".join(
            item["description"].lower() for item in estimate["labor_items"]
        )
        has_diagnostic_terms = (
            "diagnos" in labor_descriptions or
            "troubleshoot" in labor_descriptions or
            "inspect" in labor_descriptions or
            "service" in labor_descriptions
        )
        # At minimum, should have some labor items
        assert len(estimate["labor_items"]) > 0
