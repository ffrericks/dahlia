from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..db import get_session
from ..models import Location, Plant, Planting, Variety
from ..schemas.location import LocationCreate, LocationUpdate
from ..services.locations import (
    active_plantings,
    create_location,
    serialize_location,
)
from ..services.numbering import format_number

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("")
def list_locations(session: Session = Depends(get_session)) -> list[dict]:
    locations = session.exec(
        select(Location).order_by(Location.kind, Location.number)
    ).all()
    return [serialize_location(session, loc) for loc in locations]


@router.post("", status_code=201)
def create_location_endpoint(
    data: LocationCreate, session: Session = Depends(get_session)
) -> dict:
    location = create_location(session, data.kind, data.name)
    session.commit()
    session.refresh(location)
    return serialize_location(session, location)


@router.get("/{location_id}")
def get_location(location_id: int, session: Session = Depends(get_session)) -> dict:
    location = session.get(Location, location_id)
    if location is None:
        raise HTTPException(status_code=404, detail="Locatie niet gevonden.")

    data = serialize_location(session, location)
    # Which plants currently stand here, and where in the bak.
    plants = []
    for planting in active_plantings(session, location_id):
        plant = session.get(Plant, planting.plant_id)
        variety = session.get(Variety, plant.variety_id)
        plants.append(
            {
                "plant_id": plant.id,
                "full_code": f"{variety.code}{format_number(plant.ss, plant.ddd)}",
                "variety_name": variety.name,
                "position": planting.position,
            }
        )
    data["plants"] = plants
    return data


@router.patch("/{location_id}")
def update_location(
    location_id: int, data: LocationUpdate, session: Session = Depends(get_session)
) -> dict:
    location = session.get(Location, location_id)
    if location is None:
        raise HTTPException(status_code=404, detail="Locatie niet gevonden.")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(location, field, value)
    session.add(location)
    session.commit()
    session.refresh(location)
    return serialize_location(session, location)


@router.delete("/{location_id}", status_code=204)
def delete_location(location_id: int, session: Session = Depends(get_session)) -> None:
    location = session.get(Location, location_id)
    if location is None:
        raise HTTPException(status_code=404, detail="Locatie niet gevonden.")
    # Keep planting history: a location that has ever been used stays in the system.
    if session.exec(
        select(Planting.id).where(Planting.location_id == location_id)
    ).first():
        raise HTTPException(
            status_code=409,
            detail="Deze locatie is gebruikt en blijft bestaan (kan niet verwijderd worden).",
        )
    session.delete(location)
    session.commit()
