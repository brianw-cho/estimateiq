"""
Estimate Generation API Routes

Endpoints for generating AI-powered service estimates.

Phase 3: Integrated with RAG engine, Mock LLM, and Parts Catalog.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
import uuid

from app.models import (
    ServiceRequest,
    Estimate,
    EstimateLineItem,
    EstimateRange,
    EstimateStatus,
    LineType,
    HealthResponse,
)
from app.services import get_estimate_generator

router = APIRouter(prefix="/estimates", tags=["estimates"])


@router.post("", response_model=Estimate)
async def generate_estimate(request: ServiceRequest) -> Estimate:
    """
    Generate an AI-powered service estimate.
    
    This endpoint:
    1. Accepts vessel specifications and service description
    2. Retrieves similar historical jobs using RAG engine
    3. Classifies service type using template matching (Mock LLM)
    4. Generates recommended labor and parts items
    5. Validates parts against the catalog
    6. Returns a structured estimate with confidence scores
    
    The estimate includes:
    - Labor line items with hours and rates
    - Parts line items with validated catalog parts
    - Confidence scores for each recommendation
    - Low/expected/high estimate range
    - Similar jobs reference for transparency
    """
    # Get the estimate generator service
    estimate_generator = get_estimate_generator()
    
    # Generate the estimate using RAG + Mock LLM + Parts Catalog
    estimate = estimate_generator.generate_estimate(request)
    
    return estimate


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint for the estimates service"""
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        timestamp=datetime.utcnow()
    )


@router.get("/{estimate_id}", response_model=Estimate)
async def get_estimate(estimate_id: str) -> Estimate:
    """
    Retrieve a previously generated estimate by ID.
    
    Note: In Phase 1, estimates are not persisted.
    This endpoint will be fully implemented in later phases.
    """
    raise HTTPException(
        status_code=404,
        detail=f"Estimate {estimate_id} not found. Note: Estimate persistence not yet implemented."
    )
