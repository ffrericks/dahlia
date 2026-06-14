from sqlmodel import Session, select

from ..models import Plant


def _by_state(session: Session, state: str) -> list[Plant]:
    return list(session.exec(select(Plant).where(Plant.state == state)).all())


def planted_plants(session: Session) -> list[Plant]:
    """Plants still in the ground — they block starting a new season."""
    return _by_state(session, "planted")


def survived_plants(session: Session) -> list[Plant]:
    return _by_state(session, "survived_winter")


def start_new_season(session: Session) -> int:
    """Begin a new season. Blocked while any plant is still planted.

    Plants marked 'survived_winter' resume as the first plants of the new season.
    Returns how many resumed.
    """
    if planted_plants(session):
        raise ValueError(
            "Er staan nog planten geplant. Rooi ze of markeer ze als 'winter overleefd'."
        )
    resumed = survived_plants(session)
    for plant in resumed:
        plant.state = "planted"
        session.add(plant)
    session.commit()
    return len(resumed)
