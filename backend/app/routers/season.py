from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from ..db import get_session
from ..services.numbering import format_number
from ..services.season import planted_plants, start_new_season, survived_plants
from ..models import Variety

router = APIRouter(prefix="/season", tags=["season"])


def _brief(session: Session, plant) -> dict:
    variety = session.get(Variety, plant.variety_id)
    return {
        "id": plant.id,
        "full_code": f"{variety.code}{format_number(plant.ss, plant.ddd)}",
    }


@router.get("/status")
def season_status(session: Session = Depends(get_session)) -> dict:
    blocking = planted_plants(session)
    survived = survived_plants(session)
    return {
        "can_start_new": len(blocking) == 0,
        "blocking": [_brief(session, p) for p in blocking],
        "survived_count": len(survived),
    }


@router.post("/new")
def new_season(session: Session = Depends(get_session)) -> dict:
    try:
        resumed = start_new_season(session)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"resumed": resumed}
