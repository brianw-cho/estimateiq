"""
Main Application Behaviour Tests

These tests document and verify the behaviour of the main EstimateIQ
FastAPI application, including startup, health checks, and CORS.

Behaviours Documented:
1. Application startup: Proper initialization
2. Health endpoints: Monitoring and readiness
3. CORS configuration: Cross-origin resource sharing
4. API routing: All routes are accessible
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
# Application Startup Behaviours
# =============================================================================

class TestApplicationStartup:
    """
    Application initialization behaviours.
    """
    
    def test_app_starts_successfully(self, client):
        """
        The application starts and responds to requests.
        """
        response = client.get("/")
        assert response.status_code == 200
    
    def test_root_returns_health_info(self, client):
        """
        Root endpoint returns health information.
        """
        response = client.get("/")
        data = response.json()
        
        assert "status" in data
        assert "version" in data
        assert "timestamp" in data
    
    def test_openapi_docs_available(self, client):
        """
        OpenAPI documentation is available at /docs.
        """
        response = client.get("/docs")
        
        assert response.status_code == 200
    
    def test_openapi_schema_available(self, client):
        """
        OpenAPI schema is available for API clients.
        """
        response = client.get("/openapi.json")
        
        assert response.status_code == 200
        schema = response.json()
        
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema


# =============================================================================
# Health Check Behaviours
# =============================================================================

class TestHealthChecks:
    """
    Health check endpoint behaviours for monitoring.
    """
    
    def test_health_endpoint_returns_healthy(self, client):
        """
        The /health endpoint indicates healthy status.
        """
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_health_includes_version(self, client):
        """
        Health response includes application version.
        """
        response = client.get("/health")
        data = response.json()
        
        assert "version" in data
        assert data["version"]  # Not empty
    
    def test_health_includes_timestamp(self, client):
        """
        Health response includes timestamp for freshness check.
        """
        response = client.get("/health")
        data = response.json()
        
        assert "timestamp" in data


# =============================================================================
# CORS Configuration Behaviours
# =============================================================================

class TestCORSConfiguration:
    """
    CORS (Cross-Origin Resource Sharing) behaviours.
    
    CORS allows the frontend to communicate with the backend API.
    """
    
    def test_cors_allows_localhost(self, client):
        """
        CORS is configured to allow localhost origins.
        """
        response = client.options(
            "/api/estimates",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
            }
        )
        
        # Should include CORS headers (200 or 405 depending on OPTIONS handling)
        # The important thing is it's not a CORS rejection
        assert response.status_code in [200, 405]
    
    def test_cors_headers_on_response(self, client):
        """
        Responses include CORS headers for allowed origins.
        """
        response = client.get(
            "/health",
            headers={"Origin": "http://localhost:3000"}
        )
        
        # CORS headers should be present
        assert "access-control-allow-origin" in response.headers


# =============================================================================
# API Routing Behaviours
# =============================================================================

class TestAPIRouting:
    """
    API route availability behaviours.
    """
    
    def test_estimates_route_available(self, client):
        """
        The estimates API route is mounted and accessible.
        """
        response = client.get("/api/estimates/health")
        
        assert response.status_code == 200
    
    def test_vessels_route_available(self, client):
        """
        The vessels API route is mounted and accessible.
        """
        response = client.get("/api/vessels")
        
        assert response.status_code == 200
    
    def test_similar_jobs_route_available(self, client):
        """
        The similar jobs API route is mounted and accessible.
        """
        response = client.get("/api/similar-jobs?description=test+query")
        
        # Should return 200 (or 500 if vector store not initialized)
        # We're testing route availability, not functionality
        assert response.status_code in [200, 500]
    
    def test_api_prefix_is_correct(self, client):
        """
        All API routes are under /api prefix.
        """
        # These should all be under /api
        estimates_response = client.post(
            "/api/estimates",
            json={
                "vessel": {
                    "loa": 28, "year": 2019,
                    "engine_make": "Test", "engine_model": "Test"
                },
                "description": "Test service"
            }
        )
        
        vessels_response = client.get("/api/vessels")
        
        # Both should work (proving /api prefix is correct)
        assert estimates_response.status_code == 200
        assert vessels_response.status_code == 200
    
    def test_nonexistent_route_returns_404(self, client):
        """
        Non-existent routes return 404.
        """
        response = client.get("/api/nonexistent")
        
        assert response.status_code == 404


# =============================================================================
# Application Configuration Behaviours
# =============================================================================

class TestApplicationConfiguration:
    """
    Application configuration behaviours.
    """
    
    def test_app_has_title(self, client):
        """
        The application has a proper title in OpenAPI schema.
        """
        response = client.get("/openapi.json")
        schema = response.json()
        
        assert schema["info"]["title"] == "EstimateIQ"
    
    def test_app_has_description(self, client):
        """
        The application has a description in OpenAPI schema.
        """
        response = client.get("/openapi.json")
        schema = response.json()
        
        assert "description" in schema["info"]
        assert len(schema["info"]["description"]) > 0
