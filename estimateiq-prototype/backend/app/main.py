"""
EstimateIQ Backend - Main Application

AI-powered service estimate generator for DockMaster's marine service operations.

This is the main FastAPI application entry point.
Run with: uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from app.core.config import settings
from app.api.routes import estimates, vessels, similar_jobs
from app.models import HealthResponse


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="""
    EstimateIQ is an AI-powered service estimate generator that transforms 
    marine repair estimation from a 15-30 minute manual process into a 
    5-minute intelligent workflow.
    
    ## Features
    
    * **Vessel Input** - Accept vessel specs (LOA, engine make/model, year)
    * **Service Request** - Free text description of service needed
    * **AI Estimate Generation** - Generate labor tasks with hour estimates
    * **Parts Recommendations** - Suggest parts with quantities and pricing
    * **Confidence Scoring** - Display confidence level for recommendations
    * **Range Presentation** - Show low/expected/high estimates
    
    ## Phase 2 (Current)
    
    This prototype demonstrates the core workflow with:
    - Semantic search using RAG (Retrieval-Augmented Generation)
    - ChromaDB vector store for similarity search
    - Similar jobs retrieval based on service descriptions
    """,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(estimates.router, prefix=settings.api_prefix)
app.include_router(vessels.router, prefix=settings.api_prefix)
app.include_router(similar_jobs.router, prefix=settings.api_prefix)


@app.get("/", response_model=HealthResponse)
async def root() -> HealthResponse:
    """Root endpoint - returns application health status"""
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        timestamp=datetime.utcnow()
    )


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint for monitoring"""
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        timestamp=datetime.utcnow()
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on application startup"""
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Debug mode: {settings.debug}")
    print(f"API docs available at: /docs")
    print(f"Data directory: {settings.data_dir}")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    print(f"Shutting down {settings.app_name}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
