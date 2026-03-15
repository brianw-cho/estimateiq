"""
Vessel API Routes

Endpoints for vessel lookups and management.
"""

from fastapi import APIRouter, HTTPException
from typing import List

from app.models import Vessel

router = APIRouter(prefix="/vessels", tags=["vessels"])


# Mock vessel database for demo
MOCK_VESSELS = [
    Vessel(
        vessel_id="V-001",
        name="Sea Breeze",
        loa=28,
        beam=9.5,
        year=2019,
        engine_make="Volvo Penta",
        engine_model="D4-300",
        hull_type="fiberglass",
        propulsion_type="sterndrive"
    ),
    Vessel(
        vessel_id="V-002",
        name="Ocean Runner",
        loa=24,
        beam=8.5,
        year=2020,
        engine_make="Yamaha",
        engine_model="F250",
        hull_type="fiberglass",
        propulsion_type="outboard"
    ),
    Vessel(
        vessel_id="V-003",
        name="Weekend Warrior",
        loa=22,
        beam=8.0,
        year=2018,
        engine_make="MerCruiser",
        engine_model="4.3L MPI",
        hull_type="fiberglass",
        propulsion_type="sterndrive"
    ),
    Vessel(
        vessel_id="V-004",
        name="Wind Dancer",
        loa=32,
        beam=10.5,
        year=2015,
        engine_make="Yanmar",
        engine_model="3JH5E",
        hull_type="fiberglass",
        propulsion_type="inboard"
    ),
    Vessel(
        vessel_id="V-005",
        name="Party Barge",
        loa=24,
        beam=8.5,
        year=2021,
        engine_make="Mercury",
        engine_model="150 FourStroke",
        hull_type="aluminum",
        propulsion_type="outboard"
    ),
]


@router.get("", response_model=List[Vessel])
async def list_vessels() -> List[Vessel]:
    """
    List all vessels in the system.
    
    In production, this would query the DockMaster database.
    For the prototype, returns mock data.
    """
    return MOCK_VESSELS


@router.get("/{vessel_id}", response_model=Vessel)
async def get_vessel(vessel_id: str) -> Vessel:
    """
    Get a specific vessel by ID.
    """
    for vessel in MOCK_VESSELS:
        if vessel.vessel_id == vessel_id:
            return vessel
    
    raise HTTPException(
        status_code=404,
        detail=f"Vessel {vessel_id} not found"
    )


@router.get("/search/{query}", response_model=List[Vessel])
async def search_vessels(query: str) -> List[Vessel]:
    """
    Search vessels by name or engine.
    """
    query_lower = query.lower()
    results = []
    
    for vessel in MOCK_VESSELS:
        if (
            (vessel.name and query_lower in vessel.name.lower()) or
            query_lower in vessel.engine_make.lower() or
            query_lower in vessel.engine_model.lower()
        ):
            results.append(vessel)
    
    return results
