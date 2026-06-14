from datetime import date

from sqlmodel import Session

from ..models import Location, Plant, Planting
from ..schemas.planting import PlantingCreate
from .locations import create_location, current_planting
from .storage import release_box

# Only plants that are in storage (or just survived winter) can be planted out.
_PLANTABLE_STATES = {"stored", "survived_winter"}


def plant_into(session: Session, data: PlantingCreate) -> Planting:
    plant = session.get(Plant, data.plant_id)
    if plant is None:
        raise ValueError("Plant niet gevonden.")
    if plant.state not in _PLANTABLE_STATES:
        raise ValueError("Deze plant kan niet geplant worden (alleen vanuit opslag).")
    if current_planting(session, plant.id):
        raise ValueError("Deze plant staat al ergens geplant.")

    if data.location_id is not None:
        location = session.get(Location, data.location_id)
        if location is None:
            raise ValueError("Locatie niet gevonden.")
    else:
        location = create_location(session, data.new_location_kind, data.new_location_name)

    planting = Planting(
        plant_id=plant.id,
        location_id=location.id,
        planted_on=data.planted_on or date.today(),
        position=(data.position.strip() if data.position else None) or None,
    )
    # Planting out takes the tuber out of its storage box (clump replanted as-is).
    release_box(session, plant)
    # Planting starts the plant's season.
    plant.state = "planted"
    session.add(planting)
    session.add(plant)
    session.commit()
    session.refresh(planting)
    return planting


def lift_plant(session: Session, plant_id: int, lifted_on: date | None = None) -> Plant:
    """Rooien: end the plant's season, close its planting, return it to storage."""
    plant = session.get(Plant, plant_id)
    if plant is None:
        raise ValueError("Plant niet gevonden.")
    if plant.state != "planted":
        raise ValueError("Alleen geplante planten kunnen gerooid worden.")

    planting = current_planting(session, plant_id)
    if planting:
        planting.lifted_on = lifted_on or date.today()
        session.add(planting)
    plant.state = "stored"
    session.add(plant)
    session.commit()
    session.refresh(plant)
    return plant


def mark_survived_winter(session: Session, plant_id: int) -> Plant:
    """Mark a still-planted plant as having survived the winter in the ground."""
    plant = session.get(Plant, plant_id)
    if plant is None:
        raise ValueError("Plant niet gevonden.")
    if plant.state != "planted":
        raise ValueError("Alleen geplante planten kunnen 'winter overleefd' krijgen.")
    plant.state = "survived_winter"
    session.add(plant)
    session.commit()
    session.refresh(plant)
    return plant
