from fastapi import APIRouter, Depends
from sqlmodel import Session

from ..db import get_session
from ..services.dashboard import build_dashboard

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("")
def dashboard(session: Session = Depends(get_session)) -> dict:
    """Metrics for the dashboard: cards, active plants per year, per-season graphs."""
    return build_dashboard(session)
