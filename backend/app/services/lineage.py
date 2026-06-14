from collections import defaultdict

from sqlmodel import Session, select

from ..models import Plant

_GONE_STATES = {"discarded", "given_away"}


def descendant_tally(session: Session, plant_id: int) -> dict:
    """Count all transitive descendants of a plant, and how many are still owned.

    "Owned" = still in the collection (not discarded or given away).
    """
    plants = session.exec(select(Plant)).all()
    children: dict[int, list[Plant]] = defaultdict(list)
    for plant in plants:
        if plant.parent_plant_id is not None:
            children[plant.parent_plant_id].append(plant)

    total = 0
    owned = 0
    stack = list(children[plant_id])
    while stack:
        current = stack.pop()
        total += 1
        if current.state not in _GONE_STATES:
            owned += 1
        stack.extend(children[current.id])

    return {"total": total, "owned": owned}
