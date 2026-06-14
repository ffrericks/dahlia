from collections import defaultdict
from datetime import date

from sqlmodel import Session, select

from ..models import LogEntry, Planting


def _location_on(plantings_by_plant: dict[int, list[Planting]], plant_id: int, when: date):
    """Which location a plant stood in on a given date (None if not planted then)."""
    for planting in plantings_by_plant.get(plant_id, []):
        end = planting.lifted_on or date.max
        if planting.planted_on <= when <= end:
            return planting.location_id
    return None


def last_fertilized(session: Session, plant_id: int) -> date | None:
    """The most recent date this plant was fertilized.

    Plants in the same spot are fed together, so a "fertilized" log on any plant
    that shared this plant's location on that date also counts for this plant.
    Multiple plants logging it on the same place + date is one feeding, so taking
    the latest applicable date never double-counts.
    """
    fertilized_logs = session.exec(
        select(LogEntry).where(LogEntry.fertilized == True)  # noqa: E712
    ).all()
    if not fertilized_logs:
        return None

    plantings_by_plant: dict[int, list[Planting]] = defaultdict(list)
    for planting in session.exec(select(Planting)).all():
        plantings_by_plant[planting.plant_id].append(planting)

    best: date | None = None
    for log in fertilized_logs:
        if log.plant_id == plant_id:
            applies = True
        else:
            log_location = _location_on(plantings_by_plant, log.plant_id, log.entry_date)
            applies = (
                log_location is not None
                and _location_on(plantings_by_plant, plant_id, log.entry_date) == log_location
            )
        if applies and (best is None or log.entry_date > best):
            best = log.entry_date
    return best
