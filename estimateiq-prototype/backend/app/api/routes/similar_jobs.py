"""
Similar Jobs API Routes

Endpoints for retrieving similar historical work orders using RAG.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List

from app.models import SimilarJob, SimilarJobsResponse, Vessel
from app.services.rag_engine import get_rag_engine


router = APIRouter(prefix="/similar-jobs", tags=["similar-jobs"])


@router.get("", response_model=SimilarJobsResponse)
async def find_similar_jobs(
    description: str = Query(
        ..., 
        min_length=3,
        description="Service description text to search for similar jobs"
    ),
    engine_make: Optional[str] = Query(
        None,
        description="Filter by engine make (e.g., 'Volvo Penta', 'Mercury')"
    ),
    loa_min: Optional[float] = Query(
        None,
        ge=10,
        le=200,
        description="Minimum vessel length in feet"
    ),
    loa_max: Optional[float] = Query(
        None,
        ge=10,
        le=200,
        description="Maximum vessel length in feet"
    ),
    service_category: Optional[str] = Query(
        None,
        description="Filter by service category (e.g., 'engine', 'hull', 'electrical')"
    ),
    limit: int = Query(
        10,
        ge=1,
        le=50,
        description="Maximum number of results to return"
    )
) -> SimilarJobsResponse:
    """
    Find similar historical work orders using semantic search.
    
    This endpoint uses RAG (Retrieval-Augmented Generation) to find 
    historically similar jobs based on:
    - Semantic similarity to the service description
    - Optional filtering by engine make, vessel size, and service category
    
    Results are ranked by similarity score (0-1, higher is more similar).
    
    Example usage:
    ```
    GET /api/similar-jobs?description=oil change&engine_make=Volvo Penta&limit=5
    ```
    """
    try:
        rag_engine = get_rag_engine()
        
        # Retrieve similar jobs
        similar_jobs = rag_engine.retrieve_similar_jobs(
            service_description=description,
            vessel=None,  # No vessel context for direct API calls
            top_k=limit,
            engine_make_filter=engine_make,
            loa_min=loa_min,
            loa_max=loa_max,
            service_category_filter=service_category,
        )
        
        # Get total count from the retrieval
        total_count = len(similar_jobs)
        
        return SimilarJobsResponse(
            jobs=similar_jobs,
            total_count=total_count
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving similar jobs: {str(e)}"
        )


@router.post("/with-vessel", response_model=SimilarJobsResponse)
async def find_similar_jobs_with_vessel(
    description: str = Query(
        ..., 
        min_length=3,
        description="Service description text to search for similar jobs"
    ),
    vessel: Vessel = ...,
    limit: int = Query(
        10,
        ge=1,
        le=50,
        description="Maximum number of results to return"
    )
) -> SimilarJobsResponse:
    """
    Find similar historical work orders with full vessel context.
    
    This endpoint provides more accurate results by using vessel specifications
    to boost similarity scores for matching engine makes and vessel sizes.
    
    Example usage:
    ```
    POST /api/similar-jobs/with-vessel?description=oil change&limit=5
    Body: {
        "loa": 28,
        "year": 2019,
        "engine_make": "Volvo Penta",
        "engine_model": "D4-300"
    }
    ```
    """
    try:
        rag_engine = get_rag_engine()
        
        # Retrieve similar jobs with vessel context
        similar_jobs = rag_engine.retrieve_similar_jobs(
            service_description=description,
            vessel=vessel,
            top_k=limit,
        )
        
        return SimilarJobsResponse(
            jobs=similar_jobs,
            total_count=len(similar_jobs)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving similar jobs: {str(e)}"
        )


@router.get("/{work_order_id}")
async def get_work_order_details(work_order_id: str) -> dict:
    """
    Get full details of a specific work order.
    
    Returns all labor items, parts used, and invoice details for a work order.
    Useful for inspecting the details of a similar job found through search.
    """
    try:
        rag_engine = get_rag_engine()
        
        work_order = rag_engine.get_full_work_order(work_order_id)
        
        if not work_order:
            raise HTTPException(
                status_code=404,
                detail=f"Work order {work_order_id} not found"
            )
        
        return work_order
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving work order: {str(e)}"
        )


@router.get("/stats/labor-hours")
async def get_labor_statistics(
    description: str = Query(
        ..., 
        min_length=3,
        description="Service description to find similar jobs"
    ),
    limit: int = Query(
        20,
        ge=1,
        le=50,
        description="Number of similar jobs to analyze"
    )
) -> dict:
    """
    Get labor hour statistics from similar historical jobs.
    
    Returns min, max, mean, and median labor hours for jobs similar
    to the provided service description. Useful for understanding
    typical labor requirements for a service type.
    """
    try:
        rag_engine = get_rag_engine()
        
        # Get similar jobs
        similar_jobs = rag_engine.retrieve_similar_jobs(
            service_description=description,
            top_k=limit,
        )
        
        if not similar_jobs:
            return {
                "query": description,
                "sample_size": 0,
                "statistics": None,
                "message": "No similar jobs found"
            }
        
        # Calculate statistics
        stats = rag_engine.get_labor_statistics(similar_jobs)
        
        return {
            "query": description,
            "sample_size": len(similar_jobs),
            "statistics": {
                "min_hours": round(stats['min'], 2),
                "max_hours": round(stats['max'], 2),
                "mean_hours": round(stats['mean'], 2),
                "median_hours": round(stats['median'], 2),
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating statistics: {str(e)}"
        )


@router.get("/stats/parts-patterns")
async def get_parts_patterns(
    description: str = Query(
        ..., 
        min_length=3,
        description="Service description to find similar jobs"
    ),
    limit: int = Query(
        20,
        ge=1,
        le=50,
        description="Number of similar jobs to analyze"
    )
) -> dict:
    """
    Get common parts usage patterns from similar historical jobs.
    
    Returns parts that are frequently used in jobs similar to the
    provided service description. Useful for recommending parts
    during estimate generation.
    """
    try:
        rag_engine = get_rag_engine()
        
        # Get similar jobs
        similar_jobs = rag_engine.retrieve_similar_jobs(
            service_description=description,
            top_k=limit,
        )
        
        if not similar_jobs:
            return {
                "query": description,
                "sample_size": 0,
                "parts": [],
                "message": "No similar jobs found"
            }
        
        # Get work order IDs
        work_order_ids = [job.work_order_id for job in similar_jobs]
        
        # Get parts patterns
        parts_patterns = rag_engine.get_parts_patterns(work_order_ids)
        
        return {
            "query": description,
            "sample_size": len(similar_jobs),
            "parts": parts_patterns[:20],  # Top 20 most common parts
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing parts patterns: {str(e)}"
        )
