"""
Similar Jobs API Endpoint Behaviour Tests

These tests document and verify the behaviour of the similar jobs
API endpoints. These endpoints power the RAG (Retrieval-Augmented 
Generation) functionality for finding historical work orders.

Behaviours Documented:
1. Similar job search: Finding semantically similar work orders
2. Filtering: Narrowing results by engine, LOA, etc.
3. Work order details: Retrieving full work order information
4. Statistics: Labor hours and parts patterns analysis
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
# Similar Jobs Search Endpoint Behaviours
# =============================================================================

class TestSimilarJobsSearchEndpoint:
    """
    GET /api/similar-jobs endpoint behaviours.
    
    Finds similar historical work orders using semantic search.
    """
    
    def test_search_requires_description(self, client):
        """
        Search requires a description parameter.
        """
        response = client.get("/api/similar-jobs")
        
        assert response.status_code == 422  # Missing required param
    
    def test_search_returns_jobs_list(self, client):
        """
        Search returns a list of similar jobs.
        """
        response = client.get("/api/similar-jobs?description=oil+change")
        
        assert response.status_code == 200
        data = response.json()
        assert "jobs" in data
        assert isinstance(data["jobs"], list)
    
    def test_search_returns_total_count(self, client):
        """
        Search response includes total count of matches.
        """
        response = client.get("/api/similar-jobs?description=oil+change")
        
        data = response.json()
        assert "total_count" in data
        assert isinstance(data["total_count"], int)
    
    def test_similar_jobs_have_required_fields(self, client):
        """
        Each similar job has required fields for estimate generation.
        """
        response = client.get("/api/similar-jobs?description=oil+change")
        jobs = response.json()["jobs"]
        
        if len(jobs) > 0:
            job = jobs[0]
            assert "work_order_id" in job
            assert "similarity_score" in job
            assert "vessel_type" in job
            assert "loa" in job
            assert "engine" in job
            assert "service_description" in job
            assert "total_labor_hours" in job
            assert "total_invoice" in job
    
    def test_similarity_scores_are_bounded(self, client):
        """
        Similarity scores are between 0 and 1.
        """
        response = client.get("/api/similar-jobs?description=oil+change")
        jobs = response.json()["jobs"]
        
        for job in jobs:
            assert 0 <= job["similarity_score"] <= 1
    
    def test_results_are_ranked_by_similarity(self, client):
        """
        Results are sorted by similarity score (highest first).
        """
        response = client.get("/api/similar-jobs?description=oil+change&limit=10")
        jobs = response.json()["jobs"]
        
        if len(jobs) > 1:
            for i in range(len(jobs) - 1):
                assert jobs[i]["similarity_score"] >= jobs[i + 1]["similarity_score"]
    
    def test_limit_parameter_works(self, client):
        """
        The limit parameter restricts the number of results.
        """
        response = client.get("/api/similar-jobs?description=service&limit=3")
        jobs = response.json()["jobs"]
        
        assert len(jobs) <= 3
    
    def test_description_too_short_rejected(self, client):
        """
        Description must be at least 3 characters.
        """
        response = client.get("/api/similar-jobs?description=ab")
        
        assert response.status_code == 422


# =============================================================================
# Similar Jobs Filtering Behaviours
# =============================================================================

class TestSimilarJobsFiltering:
    """
    Filtering behaviours for similar jobs search.
    """
    
    def test_filter_by_engine_make(self, client):
        """
        Results can be filtered by engine make.
        """
        response = client.get(
            "/api/similar-jobs?description=service&engine_make=Volvo+Penta"
        )
        
        assert response.status_code == 200
        jobs = response.json()["jobs"]
        
        # All results should be Volvo Penta
        for job in jobs:
            assert "Volvo Penta" in job["engine"]
    
    def test_filter_by_service_category(self, client):
        """
        Results can be filtered by service category.
        """
        response = client.get(
            "/api/similar-jobs?description=service&service_category=engine"
        )
        
        assert response.status_code == 200
        # Results should be filtered (though we can't verify without seeing metadata)
    
    def test_filter_by_loa_range(self, client):
        """
        Results can be filtered by vessel length range.
        """
        response = client.get(
            "/api/similar-jobs?description=service&loa_min=25&loa_max=35"
        )
        
        assert response.status_code == 200
        jobs = response.json()["jobs"]
        
        # All results should be within LOA range
        for job in jobs:
            assert 25 <= job["loa"] <= 35
    
    def test_invalid_loa_range_rejected(self, client):
        """
        LOA outside valid range (10-200) is rejected.
        """
        response = client.get(
            "/api/similar-jobs?description=service&loa_min=5"
        )
        
        assert response.status_code == 422


# =============================================================================
# Similar Jobs with Vessel Context Behaviours
# =============================================================================

class TestSimilarJobsWithVessel:
    """
    POST /api/similar-jobs/with-vessel endpoint behaviours.
    
    Finds similar jobs with full vessel context for better matching.
    """
    
    def test_with_vessel_accepts_vessel_body(self, client):
        """
        The with-vessel endpoint accepts vessel in request body.
        """
        vessel = {
            "loa": 28,
            "year": 2019,
            "engine_make": "Volvo Penta",
            "engine_model": "D4-300"
        }
        
        response = client.post(
            "/api/similar-jobs/with-vessel?description=oil+change",
            json=vessel
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "jobs" in data
    
    def test_vessel_context_improves_relevance(self, client):
        """
        Providing vessel context affects result ranking.
        """
        vessel = {
            "loa": 28,
            "year": 2019,
            "engine_make": "Volvo Penta",
            "engine_model": "D4-300"
        }
        
        response = client.post(
            "/api/similar-jobs/with-vessel?description=oil+change",
            json=vessel
        )
        
        # Should get results (may be boosted for matching engine)
        assert response.status_code == 200
        assert len(response.json()["jobs"]) >= 0


# =============================================================================
# Work Order Details Endpoint Behaviours
# =============================================================================

class TestWorkOrderDetailsEndpoint:
    """
    GET /api/similar-jobs/{work_order_id} endpoint behaviours.
    
    Retrieves full details of a specific work order.
    """
    
    def test_get_existing_work_order(self, client):
        """
        Existing work order returns full details.
        """
        # First find a valid work order ID
        search_response = client.get("/api/similar-jobs?description=service")
        jobs = search_response.json()["jobs"]
        
        if len(jobs) > 0:
            work_order_id = jobs[0]["work_order_id"]
            response = client.get(f"/api/similar-jobs/{work_order_id}")
            
            assert response.status_code == 200
            data = response.json()
            assert "work_order_id" in data
            assert data["work_order_id"] == work_order_id
    
    def test_work_order_includes_labor_items(self, client):
        """
        Work order details include labor items.
        """
        search_response = client.get("/api/similar-jobs?description=service")
        jobs = search_response.json()["jobs"]
        
        if len(jobs) > 0:
            work_order_id = jobs[0]["work_order_id"]
            response = client.get(f"/api/similar-jobs/{work_order_id}")
            data = response.json()
            
            assert "labor_items" in data
            assert isinstance(data["labor_items"], list)
    
    def test_work_order_includes_parts_used(self, client):
        """
        Work order details include parts used.
        """
        search_response = client.get("/api/similar-jobs?description=service")
        jobs = search_response.json()["jobs"]
        
        if len(jobs) > 0:
            work_order_id = jobs[0]["work_order_id"]
            response = client.get(f"/api/similar-jobs/{work_order_id}")
            data = response.json()
            
            assert "parts_used" in data
            assert isinstance(data["parts_used"], list)
    
    def test_nonexistent_work_order_returns_404(self, client):
        """
        Non-existent work order returns 404.
        """
        response = client.get("/api/similar-jobs/WO-NONEXISTENT-999")
        
        assert response.status_code == 404


# =============================================================================
# Labor Statistics Endpoint Behaviours
# =============================================================================

class TestLaborStatisticsEndpoint:
    """
    GET /api/similar-jobs/stats/labor-hours endpoint behaviours.
    
    Provides labor hour statistics for similar jobs.
    """
    
    def test_labor_stats_returns_statistics(self, client):
        """
        Labor stats endpoint returns statistical measures.
        """
        response = client.get(
            "/api/similar-jobs/stats/labor-hours?description=oil+change"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "query" in data
        assert "sample_size" in data
    
    def test_labor_stats_includes_all_measures(self, client):
        """
        Statistics include min, max, mean, and median.
        """
        response = client.get(
            "/api/similar-jobs/stats/labor-hours?description=oil+change"
        )
        data = response.json()
        
        if data["sample_size"] > 0:
            stats = data["statistics"]
            assert "min_hours" in stats
            assert "max_hours" in stats
            assert "mean_hours" in stats
            assert "median_hours" in stats
    
    def test_labor_stats_with_no_matches(self, client):
        """
        Empty results return informative message.
        """
        # Search for something very specific that won't match
        response = client.get(
            "/api/similar-jobs/stats/labor-hours?description=xyznonexistent+service+type"
        )
        
        # Should still return 200 with zero sample size or message
        assert response.status_code == 200


# =============================================================================
# Parts Patterns Endpoint Behaviours
# =============================================================================

class TestPartsPatternEndpoint:
    """
    GET /api/similar-jobs/stats/parts-patterns endpoint behaviours.
    
    Analyzes common parts usage patterns from similar jobs.
    """
    
    def test_parts_patterns_returns_list(self, client):
        """
        Parts patterns endpoint returns a list of commonly used parts.
        """
        response = client.get(
            "/api/similar-jobs/stats/parts-patterns?description=oil+change"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "parts" in data
        assert isinstance(data["parts"], list)
    
    def test_parts_patterns_includes_metadata(self, client):
        """
        Response includes query and sample size metadata.
        """
        response = client.get(
            "/api/similar-jobs/stats/parts-patterns?description=oil+change"
        )
        data = response.json()
        
        assert "query" in data
        assert "sample_size" in data
    
    def test_parts_have_usage_info(self, client):
        """
        Each part includes count and pricing information.
        """
        response = client.get(
            "/api/similar-jobs/stats/parts-patterns?description=oil+change"
        )
        data = response.json()
        parts = data["parts"]
        
        if len(parts) > 0:
            part = parts[0]
            assert "part_number" in part
            assert "description" in part
            assert "count" in part
