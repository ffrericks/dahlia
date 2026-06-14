from collections import defaultdict
from datetime import date

from sqlmodel import Session, select

from ..models import Location, LogEntry, Planting
from .locations import location_code, location_label


def _avg(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _logs_in_planting(session: Session, planting: Planting) -> list[LogEntry]:
    """Log entries written while the plant stood in this location (this season)."""
    logs = session.exec(select(LogEntry).where(LogEntry.plant_id == planting.plant_id)).all()
    end = planting.lifted_on or date.max
    return [log for log in logs if planting.planted_on <= log.entry_date <= end]


def planting_metrics(session: Session, planting: Planting) -> dict:
    logs = _logs_in_planting(session, planting)
    heights = [log.height_cm for log in logs if log.height_cm is not None]
    flowers = [log.flower_count for log in logs if log.flower_count is not None]
    harvested = [log.harvested_count for log in logs if log.harvested_count is not None]
    return {
        # Peak height and peak simultaneous bloom; total flowers harvested.
        "height_max": max(heights) if heights else None,
        "flowers_max": max(flowers) if flowers else None,
        "harvested_total": sum(harvested),
    }


def plant_year_history(session: Session, plant_id: int) -> list[dict]:
    """Per-season summary for one plant: where it stood and how it did each year."""
    plantings = session.exec(
        select(Planting).where(Planting.plant_id == plant_id).order_by(Planting.planted_on)
    ).all()
    history = []
    for planting in plantings:
        location = session.get(Location, planting.location_id)
        history.append(
            {
                "year": planting.planted_on.year,
                "location_code": location_code(location),
                "location_label": location_label(session, location),
                "planted_on": planting.planted_on.isoformat(),
                "lifted_on": planting.lifted_on.isoformat() if planting.lifted_on else None,
                **planting_metrics(session, planting),
            }
        )
    return history


def location_ranking(session: Session, weights: dict[str, float]) -> list[dict]:
    """Rank locations by a weighted, normalized score of height/flowers/harvest.

    Metrics are averaged per planting (so a busy bak isn't unfairly boosted), then
    each metric is normalized to 0-100 against the best location before weighting.
    """
    plantings = session.exec(select(Planting)).all()
    by_location: dict[int, list[dict]] = defaultdict(list)
    for planting in plantings:
        by_location[planting.location_id].append(planting_metrics(session, planting))

    rows = []
    for location_id, metrics_list in by_location.items():
        location = session.get(Location, location_id)
        rows.append(
            {
                "location_id": location_id,
                "code": location_code(location),
                "label": location_label(session, location),
                "name": location.name,
                "plantings": len(metrics_list),
                "avg_height": round(_avg([m["height_max"] for m in metrics_list if m["height_max"] is not None]), 1),
                "avg_flowers": round(_avg([m["flowers_max"] for m in metrics_list if m["flowers_max"] is not None]), 1),
                "avg_harvested": round(_avg([m["harvested_total"] for m in metrics_list]), 1),
            }
        )

    max_height = max((r["avg_height"] for r in rows), default=0)
    max_flowers = max((r["avg_flowers"] for r in rows), default=0)
    max_harvested = max((r["avg_harvested"] for r in rows), default=0)
    weight_sum = sum(weights.values())

    def normalized(value: float, peak: float) -> float:
        return value / peak * 100 if peak else 0.0

    for row in rows:
        if weight_sum <= 0:
            row["score"] = 0.0
            continue
        score = (
            weights["height"] * normalized(row["avg_height"], max_height)
            + weights["flowers"] * normalized(row["avg_flowers"], max_flowers)
            + weights["harvested"] * normalized(row["avg_harvested"], max_harvested)
        )
        row["score"] = round(score / weight_sum, 1)

    rows.sort(key=lambda r: r["score"], reverse=True)
    return rows
