"""
EstimateIQ Pydantic Schemas

This module defines all the data models used throughout the EstimateIQ application.
These schemas are used for:
- API request/response validation
- Data serialization/deserialization
- Type hints throughout the codebase

Based on the EstimateIQ Prototype Plan specification.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum


# ============================================================================
# Enums
# ============================================================================

class HullType(str, Enum):
    """Types of boat hulls"""
    FIBERGLASS = "fiberglass"
    ALUMINUM = "aluminum"
    WOOD = "wood"
    STEEL = "steel"


class PropulsionType(str, Enum):
    """Types of boat propulsion systems"""
    INBOARD = "inboard"
    OUTBOARD = "outboard"
    STERNDRIVE = "sterndrive"
    JET = "jet"


class ServiceCategory(str, Enum):
    """Categories of marine services"""
    ENGINE = "engine"
    HULL = "hull"
    ELECTRICAL = "electrical"
    MECHANICAL = "mechanical"
    OUTBOARD = "outboard"
    INBOARD = "inboard"
    ANNUAL = "annual"
    DIAGNOSTIC = "diagnostic"


class Urgency(str, Enum):
    """Service urgency levels"""
    ROUTINE = "routine"
    PRIORITY = "priority"
    EMERGENCY = "emergency"


class EstimateStatus(str, Enum):
    """Status of an estimate in the workflow"""
    DRAFT = "draft"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    SENT = "sent"


class LineType(str, Enum):
    """Type of line item"""
    LABOR = "labor"
    PARTS = "parts"


class Season(str, Enum):
    """Seasons for regional/seasonal patterns"""
    SPRING = "spring"
    SUMMER = "summer"
    FALL = "fall"
    WINTER = "winter"


# ============================================================================
# Vessel Models
# ============================================================================

class Vessel(BaseModel):
    """
    Represents a boat/vessel with all relevant specifications.
    
    Used for:
    - Input when creating estimates
    - Matching to similar historical jobs
    - Determining parts compatibility
    """
    vessel_id: Optional[str] = Field(None, description="Unique vessel identifier from DockMaster DB")
    name: Optional[str] = Field(None, description="Vessel name")
    loa: float = Field(..., ge=10, le=200, description="Length Overall in feet")
    beam: Optional[float] = Field(None, ge=4, le=50, description="Beam width in feet")
    year: int = Field(..., ge=1950, le=2030, description="Year vessel was built")
    engine_make: str = Field(..., min_length=1, description="Engine manufacturer (e.g., Mercury, Yamaha)")
    engine_model: str = Field(..., min_length=1, description="Engine model (e.g., F250, D4-300)")
    engine_year: Optional[int] = Field(None, ge=1980, le=2030, description="Year of engine")
    hull_type: Optional[HullType] = Field(HullType.FIBERGLASS, description="Type of hull material")
    propulsion_type: Optional[PropulsionType] = Field(None, description="Type of propulsion system")

    class Config:
        json_schema_extra = {
            "example": {
                "loa": 28,
                "year": 2019,
                "engine_make": "Volvo Penta",
                "engine_model": "D4-300",
                "hull_type": "fiberglass",
                "propulsion_type": "sterndrive"
            }
        }


# ============================================================================
# Service Request Models
# ============================================================================

class ServiceRequest(BaseModel):
    """
    Input model for requesting a service estimate.
    
    Combines vessel information with service description to generate
    an AI-powered estimate.
    """
    vessel: Vessel = Field(..., description="Vessel specifications")
    description: str = Field(..., min_length=5, description="Free text service request description")
    service_category: Optional[ServiceCategory] = Field(None, description="Category of service (auto-detected if not provided)")
    urgency: Optional[Urgency] = Field(Urgency.ROUTINE, description="Urgency level of the service")
    region: Optional[str] = Field("Northeast", description="Geographic region for pricing patterns")

    class Config:
        json_schema_extra = {
            "example": {
                "vessel": {
                    "loa": 28,
                    "year": 2019,
                    "engine_make": "Volvo Penta",
                    "engine_model": "D4-300",
                    "hull_type": "fiberglass",
                    "propulsion_type": "sterndrive"
                },
                "description": "Annual oil change and filter replacement",
                "service_category": "engine",
                "urgency": "routine"
            }
        }


# ============================================================================
# Estimate Line Item Models
# ============================================================================

class EstimateLineItem(BaseModel):
    """
    A single line item in an estimate (either labor or parts).
    
    Includes confidence scoring to indicate reliability of the recommendation.
    """
    line_type: LineType = Field(..., description="Type of line item: labor or parts")
    description: str = Field(..., description="Human-readable description of the item")
    quantity: float = Field(..., ge=0, description="Quantity (hours for labor, units for parts)")
    unit: str = Field(..., description="Unit of measure (hours, each, gallon, etc.)")
    unit_price: float = Field(..., ge=0, description="Price per unit in USD")
    total_price: float = Field(..., ge=0, description="Total price (quantity * unit_price)")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score 0.0 to 1.0")
    source_reference: Optional[str] = Field(None, description="Reference to similar historical jobs")
    part_number: Optional[str] = Field(None, description="Part number (for parts items only)")

    class Config:
        json_schema_extra = {
            "example": {
                "line_type": "labor",
                "description": "Oil and filter change - Volvo D4",
                "quantity": 1.5,
                "unit": "hours",
                "unit_price": 125.00,
                "total_price": 187.50,
                "confidence": 0.95
            }
        }


# ============================================================================
# Estimate Range Model
# ============================================================================

class EstimateRange(BaseModel):
    """
    Represents the low/expected/high range for an estimate.
    
    Helps service writers set customer expectations appropriately.
    """
    low: float = Field(..., ge=0, description="Low-end estimate (optimistic)")
    expected: float = Field(..., ge=0, description="Expected estimate (most likely)")
    high: float = Field(..., ge=0, description="High-end estimate (conservative)")

    class Config:
        json_schema_extra = {
            "example": {
                "low": 266.82,
                "expected": 296.47,
                "high": 355.76
            }
        }


# ============================================================================
# Full Estimate Model
# ============================================================================

class Estimate(BaseModel):
    """
    Complete estimate response including all line items, totals, and metadata.
    
    This is the primary output of the estimate generation process.
    """
    estimate_id: str = Field(..., description="Unique estimate identifier")
    vessel: Vessel = Field(..., description="Vessel details")
    service_description: str = Field(..., description="Original service request description")
    labor_items: List[EstimateLineItem] = Field(default_factory=list, description="List of labor line items")
    parts_items: List[EstimateLineItem] = Field(default_factory=list, description="List of parts line items")
    labor_subtotal: float = Field(..., ge=0, description="Sum of all labor items")
    parts_subtotal: float = Field(..., ge=0, description="Sum of all parts items")
    total_estimate: float = Field(..., ge=0, description="Grand total (labor + parts)")
    estimate_range: EstimateRange = Field(..., description="Low/expected/high range")
    confidence_score: float = Field(..., ge=0, le=1, description="Overall confidence score")
    similar_jobs_count: int = Field(..., ge=0, description="Number of similar historical jobs found")
    similar_jobs_summary: str = Field(..., description="Human-readable summary of similar jobs")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of generation")
    status: EstimateStatus = Field(EstimateStatus.DRAFT, description="Workflow status")

    class Config:
        json_schema_extra = {
            "example": {
                "estimate_id": "est_abc123",
                "service_description": "Annual oil change and filter replacement",
                "labor_subtotal": 187.50,
                "parts_subtotal": 108.97,
                "total_estimate": 296.47,
                "confidence_score": 0.94,
                "similar_jobs_count": 23,
                "similar_jobs_summary": "Based on 23 similar oil changes on 25-30' vessels with Volvo D4 engines",
                "status": "draft"
            }
        }


# ============================================================================
# Historical Work Order Models (for RAG)
# ============================================================================

class LaborItem(BaseModel):
    """Labor item from a historical work order"""
    task: str = Field(..., description="Task description")
    hours: float = Field(..., ge=0, description="Hours spent")
    rate: float = Field(..., ge=0, description="Hourly rate")


class PartItem(BaseModel):
    """Part item from a historical work order"""
    part_number: str = Field(..., description="Part number/SKU")
    description: str = Field(..., description="Part description")
    quantity: float = Field(..., ge=0, description="Quantity used")
    unit_price: float = Field(..., ge=0, description="Price per unit")


class HistoricalWorkOrder(BaseModel):
    """
    Historical work order used for RAG retrieval.
    
    These records are embedded and stored in the vector database
    for similarity search when generating new estimates.
    """
    work_order_id: str = Field(..., description="Unique work order ID")
    vessel_type: str = Field(..., description="Type of vessel (e.g., Cabin Cruiser)")
    loa: float = Field(..., description="Length Overall in feet")
    loa_range: str = Field(..., description="LOA range bucket (e.g., '25-30')")
    year: int = Field(..., description="Vessel year")
    engine_make: str = Field(..., description="Engine manufacturer")
    engine_model: str = Field(..., description="Engine model")
    service_category: ServiceCategory = Field(..., description="Category of service")
    service_description: str = Field(..., description="Text description of service performed")
    labor_items: List[LaborItem] = Field(default_factory=list, description="Labor tasks performed")
    parts_used: List[PartItem] = Field(default_factory=list, description="Parts used")
    total_labor_hours: float = Field(..., ge=0, description="Total labor hours")
    total_parts_cost: float = Field(..., ge=0, description="Total parts cost")
    total_invoice: float = Field(..., ge=0, description="Grand total invoice amount")
    completion_date: str = Field(..., description="Date work was completed (ISO format)")
    region: str = Field(..., description="Geographic region")
    season: Season = Field(..., description="Season when work was completed")

    class Config:
        json_schema_extra = {
            "example": {
                "work_order_id": "WO-2024-1234",
                "vessel_type": "Cabin Cruiser",
                "loa": 28,
                "loa_range": "25-30",
                "year": 2019,
                "engine_make": "Volvo Penta",
                "engine_model": "D4-300",
                "service_category": "engine",
                "service_description": "Annual oil and filter change, inspected belts",
                "total_labor_hours": 1.5,
                "total_parts_cost": 108.97,
                "total_invoice": 296.47,
                "completion_date": "2024-09-15",
                "region": "Northeast",
                "season": "fall"
            }
        }


# ============================================================================
# Parts Catalog Models
# ============================================================================

class Part(BaseModel):
    """
    A part in the parts catalog.
    
    Used to validate parts suggestions and provide real pricing.
    """
    part_number: str = Field(..., description="Unique part number/SKU")
    description: str = Field(..., description="Human-readable description")
    category: str = Field(..., description="Part category (e.g., Filters, Fluids)")
    compatible_engines: List[str] = Field(default_factory=list, description="List of compatible engine makes")
    list_price: float = Field(..., ge=0, description="List price in USD")
    unit: str = Field("each", description="Unit of measure")

    class Config:
        json_schema_extra = {
            "example": {
                "part_number": "21549542",
                "description": "Volvo Penta Oil Filter",
                "category": "Filters",
                "compatible_engines": ["Volvo Penta"],
                "list_price": 42.99,
                "unit": "each"
            }
        }


# ============================================================================
# Similar Jobs Response (for RAG endpoint)
# ============================================================================

class SimilarJob(BaseModel):
    """A similar historical job returned from RAG search"""
    work_order_id: str
    similarity_score: float = Field(..., ge=0, le=1)
    vessel_type: str
    loa: float
    engine: str
    service_description: str
    total_labor_hours: float
    total_invoice: float
    completion_date: str


class SimilarJobsResponse(BaseModel):
    """Response from the similar jobs endpoint"""
    jobs: List[SimilarJob]
    total_count: int


# ============================================================================
# API Response Wrappers
# ============================================================================

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    version: str = "0.1.0"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
