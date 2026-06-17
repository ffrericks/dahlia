from collections import defaultdict
from datetime import date, timedelta

from sqlmodel import Session, select

from ..models import Disposal, LogEntry, Plant, Variety

_GONE_STATES = {"discarded", "given_away"}


def _end_of_month(year: int, month: int) -> date:
    if month == 12:
        return date(year, 12, 31)
    return date(year, month + 1, 1) - timedelta(days=1)


def build_dashboard(session: Session) -> dict:
    plants = session.exec(select(Plant)).all()
    logs = session.exec(select(LogEntry)).all()

    # --- static cards ---
    varieties = len(session.exec(select(Variety.id)).all())
    active_plants = sum(1 for p in plants if p.state not in _GONE_STATES)
    harvested_total = sum(log.harvested_count or 0 for log in logs)
    cards = {
        "varieties": varieties,
        "plants": active_plants,
        "harvested_total": harvested_total,
    }

    # --- active plants over time, one line per year ---
    disposed_on = {
        d.plant_id: d.disposed_on for d in session.exec(select(Disposal)).all()
    }
    today = date.today()
    created_years = [p.created_on.year for p in plants if p.created_on]
    log_years = [log.entry_date.year for log in logs]
    start_year = min(created_years) if created_years else today.year
    end_year = max([today.year, *created_years, *log_years])

    plants_per_year = []
    for year in range(start_year, end_year + 1):
        points = []
        for month in range(1, 13):
            eom = _end_of_month(year, month)
            count = 0
            for plant in plants:
                if plant.created_on and plant.created_on <= eom:
                    left = disposed_on.get(plant.id)
                    if left is None or left > eom:
                        count += 1
            points.append({"month": month, "count": count})
        plants_per_year.append({"year": year, "points": points})

    # --- per-season metrics from the logbook ---
    by_month: dict[tuple[int, int], dict[str, list[int]]] = defaultdict(
        lambda: {"flowers": [], "buds": [], "heights": []}
    )
    for log in logs:
        key = (log.entry_date.year, log.entry_date.month)
        if log.flower_count is not None:
            by_month[key]["flowers"].append(log.flower_count)
        if log.bud_count is not None:
            by_month[key]["buds"].append(log.bud_count)
        if log.height_cm is not None:
            by_month[key]["heights"].append(log.height_cm)

    seasons = []
    for year in sorted({log.entry_date.year for log in logs}):
        points = []
        for month in range(1, 13):
            agg = by_month.get((year, month))
            points.append(
                {
                    "month": month,
                    # Peak values per month (a single highest log), not a sum.
                    "flowers": max(agg["flowers"]) if agg and agg["flowers"] else None,
                    "buds": max(agg["buds"]) if agg and agg["buds"] else None,
                    "height": max(agg["heights"]) if agg and agg["heights"] else None,
                }
            )
        seasons.append({"year": year, "points": points})

    return {"cards": cards, "plants_per_year": plants_per_year, "seasons": seasons}
