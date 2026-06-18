from datetime import date

from sqlmodel import Session

from ..models import Plant
from ..schemas.plant import TransplantCreate
from ..schemas.planting import PlantingCreate
from .numbering import next_ddd
from .plantings import lift_plant, plant_into


def create_cutting(
    session: Session, parent_id: int, new_location_name: str | None = None
) -> Plant:
    """Take a cutting: a descendant in the parent's stam that goes straight into its own pot."""
    parent = session.get(Plant, parent_id)
    if parent is None:
        raise ValueError("Moederplant niet gevonden.")
    if parent.variety_id is None:
        raise ValueError("De moederplant heeft nog geen soort; wijs die eerst toe.")
    if parent.rooting:
        raise ValueError("Een stek die nog wortelt kan niet gestekt worden.")

    cutting = Plant(
        variety_id=parent.variety_id,
        ss=parent.ss,  # same stam as the parent
        ddd=next_ddd(session, parent.variety_id, parent.ss),
        parent_plant_id=parent.id,
        origin="cutting",
        state="stored",  # momentarily, until planted into its pot below
        rooting=True,
        created_on=date.today(),
    )
    session.add(cutting)
    session.commit()
    session.refresh(cutting)

    # A cutting never sits in storage — give it its own pot right away.
    plant_into(
        session,
        PlantingCreate(
            plant_id=cutting.id,
            new_location_kind="container",
            new_location_name=new_location_name,
        ),
    )
    session.refresh(cutting)
    return cutting


def transplant_cutting(session: Session, plant_id: int, data: TransplantCreate) -> Plant:
    """Plant a rooting cutting out into a real location; the pot code lapses."""
    plant = session.get(Plant, plant_id)
    if plant is None:
        raise ValueError("Plant niet gevonden.")
    if plant.origin != "cutting" or not plant.rooting:
        raise ValueError("Alleen een stek die nog in z'n pot wortelt kan uitgeplant worden.")

    # Take it out of its pot, drop the rooting phase, then plant it normally.
    lift_plant(session, plant_id, data.planted_on)
    plant = session.get(Plant, plant_id)
    plant.rooting = False
    session.add(plant)
    session.commit()

    plant_into(
        session,
        PlantingCreate(
            plant_id=plant_id,
            location_id=data.location_id,
            new_location_kind=data.new_location_kind,
            new_location_name=data.new_location_name,
            position=data.position,
            planted_on=data.planted_on,
        ),
    )
    session.refresh(plant)
    return plant
