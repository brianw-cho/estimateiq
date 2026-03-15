"""
EstimateIQ Data Models

Pydantic schemas for request/response validation and data serialization.
"""

from .schemas import (
    # Enums
    HullType,
    PropulsionType,
    ServiceCategory,
    Urgency,
    EstimateStatus,
    LineType,
    Season,
    # Vessel
    Vessel,
    # Service Request
    ServiceRequest,
    # Estimate Items
    EstimateLineItem,
    EstimateRange,
    Estimate,
    # Historical Data
    LaborItem,
    PartItem,
    HistoricalWorkOrder,
    # Parts
    Part,
    # Similar Jobs
    SimilarJob,
    SimilarJobsResponse,
    # API
    HealthResponse,
    ErrorResponse,
)

__all__ = [
    "HullType",
    "PropulsionType",
    "ServiceCategory",
    "Urgency",
    "EstimateStatus",
    "LineType",
    "Season",
    "Vessel",
    "ServiceRequest",
    "EstimateLineItem",
    "EstimateRange",
    "Estimate",
    "LaborItem",
    "PartItem",
    "HistoricalWorkOrder",
    "Part",
    "SimilarJob",
    "SimilarJobsResponse",
    "HealthResponse",
    "ErrorResponse",
]
