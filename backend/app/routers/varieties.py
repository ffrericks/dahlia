import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from ..db import get_session
from ..models import Plant, Variety
from ..schemas.variety import (
    VarietyCreate,
    VarietyRead,
    VarietyUpdate,
    WikipediaRequest,
)
from ..services.photos import variety_image_thumb
from ..services.wikipedia import fetch_first_paragraph

router = APIRouter(prefix="/varieties", tags=["varieties"])


def serialize_variety(session: Session, variety: Variety) -> dict:
    plant_count = len(
        session.exec(select(Plant.id).where(Plant.variety_id == variety.id)).all()
    )
    return {
        "id": variety.id,
        "code": variety.code,
        "name": variety.name,
        "description": variety.description,
        "wikipedia_url": variety.wikipedia_url,
        "plant_count": plant_count,
        "image_thumbnail": variety_image_thumb(session, variety.id),
    }


@router.get("", response_model=list[VarietyRead])
def list_varieties(session: Session = Depends(get_session)) -> list[dict]:
    varieties = session.exec(select(Variety).order_by(Variety.code)).all()
    return [serialize_variety(session, v) for v in varieties]


@router.post("/wikipedia-extract")
def wikipedia_extract(payload: WikipediaRequest) -> dict[str, str]:
    """Fetch a Wikipedia article's first paragraph so the UI can prefill the description."""
    try:
        return {"extract": fetch_first_paragraph(payload.url)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Kon Wikipedia niet bereiken: {exc}")


@router.post("", response_model=VarietyRead, status_code=201)
def create_variety(data: VarietyCreate, session: Session = Depends(get_session)) -> dict:
    variety = Variety(**data.model_dump())
    session.add(variety)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail=f"Soortcode '{data.code}' bestaat al.")
    session.refresh(variety)
    return serialize_variety(session, variety)


@router.get("/{variety_id}", response_model=VarietyRead)
def get_variety(variety_id: int, session: Session = Depends(get_session)) -> dict:
    variety = session.get(Variety, variety_id)
    if variety is None:
        raise HTTPException(status_code=404, detail="Soort niet gevonden.")
    return serialize_variety(session, variety)


@router.patch("/{variety_id}", response_model=VarietyRead)
def update_variety(
    variety_id: int, data: VarietyUpdate, session: Session = Depends(get_session)
) -> dict:
    variety = session.get(Variety, variety_id)
    if variety is None:
        raise HTTPException(status_code=404, detail="Soort niet gevonden.")
    # Only overwrite fields the client actually sent.
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(variety, field, value)
    session.add(variety)
    session.commit()
    session.refresh(variety)
    return serialize_variety(session, variety)


@router.delete("/{variety_id}", status_code=204)
def delete_variety(variety_id: int, session: Session = Depends(get_session)) -> None:
    variety = session.get(Variety, variety_id)
    if variety is None:
        raise HTTPException(status_code=404, detail="Soort niet gevonden.")
    # A variety with plants can't be removed — that would orphan their numbers.
    if session.exec(select(Plant.id).where(Plant.variety_id == variety_id)).first():
        raise HTTPException(
            status_code=409,
            detail="Deze soort heeft nog planten en kan niet verwijderd worden.",
        )
    session.delete(variety)
    session.commit()
