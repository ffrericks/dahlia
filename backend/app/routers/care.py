from datetime import date

from fastapi import APIRouter, Query

from ..services.care_tips import tips_for_month

router = APIRouter(tags=["care"])


@router.get("/care-tips")
def care_tips(month: int | None = Query(default=None, ge=1, le=12)) -> dict:
    """Care tips relevant to a month (defaults to the current month)."""
    active_month = month if month is not None else date.today().month
    return {"month": active_month, "tips": tips_for_month(active_month)}
