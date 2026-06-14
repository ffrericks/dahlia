from sqlmodel import Session, select

from ..models import Plant

# Single-user app: no concurrent writers, so a read-then-max is safe for numbering.


def next_stam(session: Session, variety_id: int) -> int:
    """Next stam index (SS) for a variety: highest existing + 1, or 1 if none."""
    rows = session.exec(select(Plant.ss).where(Plant.variety_id == variety_id)).all()
    return max(rows) + 1 if rows else 1


def next_ddd(session: Session, variety_id: int, ss: int) -> int:
    """Next descendant counter (DDD) within a stam: highest existing + 1.

    The stam plant is DDD=000, so the first split becomes 001.
    """
    rows = session.exec(
        select(Plant.ddd).where(Plant.variety_id == variety_id, Plant.ss == ss)
    ).all()
    return max(rows) + 1 if rows else 0


def format_number(ss: int, ddd: int) -> str:
    """Format a plant number as the 5-digit SSDDD string, e.g. (1, 0) -> '01000'."""
    return f"{ss:02d}{ddd:03d}"
