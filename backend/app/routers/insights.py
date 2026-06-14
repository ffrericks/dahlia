from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from ..db import get_session
from ..services.insights import location_ranking

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("/locations")
def best_locations(
    w_height: float = Query(default=1.0, ge=0),
    w_flowers: float = Query(default=1.0, ge=0),
    w_harvested: float = Query(default=1.0, ge=0),
    session: Session = Depends(get_session),
) -> dict:
    """End-of-season ranking of which spot/bak grew best (adjustable weights)."""
    weights = {"height": w_height, "flowers": w_flowers, "harvested": w_harvested}
    return {"weights": weights, "locations": location_ranking(session, weights)}
