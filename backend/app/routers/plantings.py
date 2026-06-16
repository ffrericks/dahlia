from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from ..db import get_session
from ..schemas.planting import PlantingCreate
from ..services.locations import serialize_planting
from ..services.plantings import plant_into

router = APIRouter(prefix="/plantings", tags=["plantings"])


@router.post("", status_code=201)
def create_planting(
    data: PlantingCreate, session: Session = Depends(get_session)
) -> dict:
    """Plant a plant into a location, starting its season."""
    try:
        planting = plant_into(session, data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return serialize_planting(session, planting)
