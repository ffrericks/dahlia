from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from ..db import get_session
from ..models import StorageBox
from ..services.storage import serialize_box

router = APIRouter(prefix="/storage-boxes", tags=["storage"])


@router.get("")
def list_boxes(session: Session = Depends(get_session)) -> list[dict]:
    boxes = session.exec(
        select(StorageBox).order_by(StorageBox.year, StorageBox.number)
    ).all()
    return [serialize_box(session, box) for box in boxes]
