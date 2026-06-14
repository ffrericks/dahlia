from sqlmodel import Session, select

from ..models import Location, Planting


def location_code(location: Location) -> str:
    prefix = "T" if location.kind == "garden" else "B"
    return f"{prefix}{location.number:02d}"


def active_plantings(session: Session, location_id: int) -> list[Planting]:
    """Plantings currently in a location (not yet lifted)."""
    return list(
        session.exec(
            select(Planting).where(
                Planting.location_id == location_id, Planting.lifted_on.is_(None)
            )
        ).all()
    )


def location_label(session: Session, location: Location) -> str:
    if location.kind == "garden":
        return "tuin"
    # A container with more than one plant is a bak; otherwise a pot.
    return "bak" if len(active_plantings(session, location.id)) > 1 else "pot"


def next_number(session: Session, kind: str) -> int:
    rows = session.exec(select(Location.number).where(Location.kind == kind)).all()
    return max(rows) + 1 if rows else 1


def create_location(session: Session, kind: str, name: str | None) -> Location:
    if kind not in ("garden", "container"):
        raise ValueError("Soort locatie moet 'garden' of 'container' zijn.")
    location = Location(
        kind=kind,
        number=next_number(session, kind),
        name=(name.strip() if name else None) or None,
    )
    session.add(location)
    session.flush()  # assign an id without committing yet
    return location


def current_planting(session: Session, plant_id: int) -> Planting | None:
    return session.exec(
        select(Planting).where(
            Planting.plant_id == plant_id, Planting.lifted_on.is_(None)
        )
    ).first()


def serialize_location(session: Session, location: Location) -> dict:
    return {
        "id": location.id,
        "kind": location.kind,
        "code": location_code(location),
        "name": location.name,
        "label": location_label(session, location),
        "active_count": len(active_plantings(session, location.id)),
    }


def serialize_planting(session: Session, planting: Planting) -> dict:
    location = session.get(Location, planting.location_id)
    return {
        "id": planting.id,
        "location_id": planting.location_id,
        "location_code": location_code(location),
        "location_name": location.name,
        "location_label": location_label(session, location),
        "position": planting.position,
        "planted_on": planting.planted_on.isoformat(),
        "lifted_on": planting.lifted_on.isoformat() if planting.lifted_on else None,
    }
