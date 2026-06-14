from datetime import date

from sqlmodel import Session, select

from ..models import Disposal, LogEntry, Plant
from .locations import current_planting
from .storage import release_box

_GONE_STATES = {"discarded", "given_away"}


def dispose_plant(
    session: Session,
    plant_id: int,
    kind: str,
    reason: str | None = None,
    recipient: str | None = None,
    disease_warning: bool = False,
    disposed_on: date | None = None,
) -> Plant:
    """Discard or give away a plant: change state and record why, without deleting it."""
    plant = session.get(Plant, plant_id)
    if plant is None:
        raise ValueError("Plant niet gevonden.")
    if plant.state in _GONE_STATES:
        raise ValueError("Deze plant is al afgevoerd.")

    when = disposed_on or date.today()

    # If it was in the ground, free the spot; if boxed, take it out.
    planting = current_planting(session, plant_id)
    if planting:
        planting.lifted_on = when
        session.add(planting)
    release_box(session, plant)

    plant.state = kind
    if disease_warning:
        plant.disease_warning = True
    session.add(plant)

    session.add(
        Disposal(
            plant_id=plant_id,
            kind=kind,
            reason=reason,
            recipient=recipient,
            disease_warning=disease_warning,
            disposed_on=when,
        )
    )
    session.commit()
    session.refresh(plant)
    return plant


def mark_not_emerged(session: Session, plant_id: int) -> Plant:
    """"Did not come up" — counts as discarded, with a logbook note."""
    plant = session.get(Plant, plant_id)
    if plant is None:
        raise ValueError("Plant niet gevonden.")
    session.add(LogEntry(plant_id=plant_id, entry_date=date.today(), text="Niet opgekomen."))
    return dispose_plant(session, plant_id, kind="discarded", reason="Niet opgekomen")
