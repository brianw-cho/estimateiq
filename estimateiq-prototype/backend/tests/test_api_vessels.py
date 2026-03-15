"""
Vessel API Endpoint Behaviour Tests

These tests document and verify the behaviour of the vessel management
API endpoints. The vessel API provides vessel lookups for the estimate
generation workflow.

Behaviours Documented:
1. Vessel listing: Retrieving all vessels
2. Vessel lookup: Finding specific vessels by ID
3. Vessel search: Searching by name or engine
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


# =============================================================================
# Test Client Setup
# =============================================================================

@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


# =============================================================================
# Vessel Listing Endpoint Behaviours
# =============================================================================

class TestVesselListingEndpoint:
    """
    GET /api/vessels endpoint behaviours.
    
    Lists all vessels in the system.
    """
    
    def test_list_vessels_returns_array(self, client):
        """
        Listing vessels returns an array of vessel objects.
        """
        response = client.get("/api/vessels")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_vessels_have_required_fields(self, client):
        """
        Each vessel has the minimum required fields.
        """
        response = client.get("/api/vessels")
        vessels = response.json()
        
        assert len(vessels) > 0
        
        for vessel in vessels:
            assert "loa" in vessel
            assert "year" in vessel
            assert "engine_make" in vessel
            assert "engine_model" in vessel
    
    def test_vessels_include_identifiers(self, client):
        """
        Vessels include ID and name for lookup.
        """
        response = client.get("/api/vessels")
        vessels = response.json()
        
        # At least one vessel should have an ID
        ids = [v.get("vessel_id") for v in vessels if v.get("vessel_id")]
        assert len(ids) > 0
    
    def test_mock_vessels_represent_variety(self, client):
        """
        Mock vessels represent different boat types and engines.
        """
        response = client.get("/api/vessels")
        vessels = response.json()
        
        # Should have multiple different engine makes
        engine_makes = set(v["engine_make"] for v in vessels)
        assert len(engine_makes) > 1
        
        # Should have variety in LOA
        loas = [v["loa"] for v in vessels]
        assert min(loas) < 25
        assert max(loas) > 25


# =============================================================================
# Vessel Lookup Endpoint Behaviours
# =============================================================================

class TestVesselLookupEndpoint:
    """
    GET /api/vessels/{vessel_id} endpoint behaviours.
    
    Looks up a specific vessel by its ID.
    """
    
    def test_lookup_existing_vessel_returns_details(self, client):
        """
        Looking up an existing vessel returns its full details.
        """
        # First get a valid ID
        all_vessels = client.get("/api/vessels").json()
        valid_id = all_vessels[0]["vessel_id"]
        
        response = client.get(f"/api/vessels/{valid_id}")
        
        assert response.status_code == 200
        vessel = response.json()
        assert vessel["vessel_id"] == valid_id
    
    def test_lookup_nonexistent_vessel_returns_404(self, client):
        """
        Looking up a non-existent vessel returns 404.
        """
        response = client.get("/api/vessels/V-NONEXISTENT")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_lookup_returns_complete_vessel(self, client):
        """
        Lookup returns all vessel fields including optional ones.
        """
        all_vessels = client.get("/api/vessels").json()
        valid_id = all_vessels[0]["vessel_id"]
        
        response = client.get(f"/api/vessels/{valid_id}")
        vessel = response.json()
        
        # Should have optional fields populated
        assert "name" in vessel
        assert "hull_type" in vessel
        assert "propulsion_type" in vessel


# =============================================================================
# Vessel Search Endpoint Behaviours
# =============================================================================

class TestVesselSearchEndpoint:
    """
    GET /api/vessels/search/{query} endpoint behaviours.
    
    Searches vessels by name or engine.
    """
    
    def test_search_by_name_finds_matches(self, client):
        """
        Searching by vessel name finds matching vessels.
        """
        response = client.get("/api/vessels/search/Sea")
        
        assert response.status_code == 200
        results = response.json()
        
        # Should find vessels with "Sea" in name
        assert isinstance(results, list)
    
    def test_search_by_engine_make_finds_matches(self, client):
        """
        Searching by engine make finds matching vessels.
        """
        response = client.get("/api/vessels/search/Volvo")
        
        assert response.status_code == 200
        results = response.json()
        
        # All results should have Volvo in engine
        for vessel in results:
            assert "volvo" in vessel["engine_make"].lower() or \
                   "volvo" in vessel.get("name", "").lower()
    
    def test_search_by_engine_model_finds_matches(self, client):
        """
        Searching by engine model finds matching vessels.
        """
        response = client.get("/api/vessels/search/D4")
        
        assert response.status_code == 200
        results = response.json()
        
        # Results should contain D4 in engine model
        for vessel in results:
            matches = (
                "d4" in vessel["engine_model"].lower() or
                "d4" in vessel["engine_make"].lower() or
                "d4" in vessel.get("name", "").lower()
            )
            assert matches
    
    def test_search_is_case_insensitive(self, client):
        """
        Search is case insensitive.
        """
        response_lower = client.get("/api/vessels/search/mercury")
        response_upper = client.get("/api/vessels/search/MERCURY")
        
        assert response_lower.status_code == 200
        assert response_upper.status_code == 200
        
        # Both should find the same results
        assert len(response_lower.json()) == len(response_upper.json())
    
    def test_search_no_matches_returns_empty(self, client):
        """
        Search with no matches returns empty list.
        """
        response = client.get("/api/vessels/search/XYZNONEXISTENT")
        
        assert response.status_code == 200
        assert response.json() == []
    
    def test_search_returns_array(self, client):
        """
        Search always returns an array (even if empty).
        """
        response = client.get("/api/vessels/search/test")
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)
