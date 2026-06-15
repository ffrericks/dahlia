from datetime import date

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from ..db import get_session
from ..models import Location, LogEntry, Plant, Variety
from ..services.fertilization import last_fertilized
from ..services.locations import current_planting, location_code, location_label
from ..services.numbering import format_number

router = APIRouter(prefix="/automation", tags=["automation"])

_GONE_STATES = ["discarded", "given_away"]


@router.get("/plants")
def automation_plants(
    include_gone: bool = False, session: Session = Depends(get_session)
) -> list[dict]:
    """Flat, read-only summary per plant for tools like n8n.

    Gives everything to drive notifications: when last fertilized (and how many
    days ago), flower/harvest totals, and the latest logbook entry.
    """
    query = select(Plant)
    if not include_gone:
        query = query.where(Plant.state.not_in(_GONE_STATES))
    plants = session.exec(query.order_by(Plant.variety_id, Plant.ss, Plant.ddd)).all()

    today = date.today()
    summaries = []
    for plant in plants:
        variety = session.get(Variety, plant.variety_id) if plant.variety_id else None
        number = (
            format_number(plant.ss, plant.ddd)
            if plant.ss is not None and plant.ddd is not None
            else None
        )
        full_code = f"{variety.code}{number}" if variety and number else None

        logs = session.exec(
            select(LogEntry)
            .where(LogEntry.plant_id == plant.id)
            .order_by(LogEntry.entry_date.desc(), LogEntry.id.desc())
        ).all()
        heights = [log.height_cm for log in logs if log.height_cm is not None]
        buds = [log.bud_count for log in logs if log.bud_count is not None]
        flowers = [log.flower_count for log in logs if log.flower_count is not None]
        harvested = [log.harvested_count for log in logs if log.harvested_count is not None]
        latest = logs[0] if logs else None

        fertilized = last_fertilized(session, plant.id)
        planting = current_planting(session, plant.id)
        location = session.get(Location, planting.location_id) if planting else None

        summaries.append(
            {
                "id": plant.id,
                "full_code": full_code,
                "label": full_code or plant.nickname or "Onbekend",
                "variety_name": variety.name if variety else None,
                "state": plant.state,
                "location": location_code(location) if location else None,
                "location_label": location_label(session, location) if location else None,
                "last_fertilized": fertilized.isoformat() if fertilized else None,
                "days_since_fertilized": (today - fertilized).days if fertilized else None,
                "height_max_cm": max(heights) if heights else None,
                "buds_peak": max(buds) if buds else None,
                "flowers_peak": max(flowers) if flowers else None,
                "harvested_total": sum(harvested),
                "last_log_date": latest.entry_date.isoformat() if latest else None,
                "last_log_text": latest.text if latest else None,
            }
        )
    return summaries
