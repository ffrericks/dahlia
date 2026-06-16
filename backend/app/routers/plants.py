from collections import Counter, defaultdict

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import PlainTextResponse
from sqlmodel import Session, select

from datetime import date

from ..db import get_session
from ..models import (
    Disposal,
    Location,
    LogEntry,
    Photo,
    Plant,
    Planting,
    StorageBox,
    Variety,
)
from ..schemas.disposal import DisposalCreate
from ..schemas.log import LogEntryCreate
from ..schemas.plant import PlantCreate, PlantUpdate, VarietyAssign
from ..schemas.winter import EyeStatusUpdate, LiftRequest, StorageAssign
from ..services import disposal as disposal_service
from ..services import plantings as planting_service
from ..services import plants as plant_service
from ..services.fertilization import last_fertilized
from ..services.insights import plant_year_history
from ..services.lineage import descendant_tally
from ..services.locations import (
    current_planting,
    location_code,
    location_label,
    serialize_planting,
)
from ..services.numbering import format_number
from ..services.photos import (
    delete_files,
    effective_thumbnail,
    profile_photo_of,
    save_upload,
)
from ..services.storage import assign_to_box, box_code, release_box
from ..services.summary import build_plant_summary

# Plants in these states have left the collection: hidden from the active list.
_GONE_STATES = ["discarded", "given_away"]

router = APIRouter(prefix="/plants", tags=["plants"])


# --- serialization helpers -------------------------------------------------


def serialize_plant(session: Session, plant: Plant) -> dict:
    # A provisional (unknown) plant has no variety/number yet — use its nickname.
    variety = session.get(Variety, plant.variety_id) if plant.variety_id else None
    if variety and plant.ss is not None and plant.ddd is not None:
        number = format_number(plant.ss, plant.ddd)
        full_code = f"{variety.code}{number}"
    else:
        number = None
        full_code = None
    label = full_code or plant.nickname or "Onbekend"

    # Where the plant currently stands (if planted).
    location = None
    planting = current_planting(session, plant.id)
    if planting:
        loc = session.get(Location, planting.location_id)
        location = {
            "code": location_code(loc),
            "name": loc.name,
            "label": location_label(session, loc),
            "position": planting.position,
        }

    return {
        "id": plant.id,
        "variety_id": plant.variety_id,
        "variety_code": variety.code if variety else None,
        "variety_name": variety.name if variety else None,
        "ss": plant.ss,
        "ddd": plant.ddd,
        "number": number,
        "full_code": full_code,
        "nickname": plant.nickname,
        "label": label,
        "origin": plant.origin,
        "parent_plant_id": plant.parent_plant_id,
        "state": plant.state,
        "eye_status": plant.eye_status,
        "disease_warning": plant.disease_warning,
        "thumbnail": effective_thumbnail(session, plant),
        "location": location,
        "storage": _storage_info(session, plant, label),
        "last_fertilized": _iso(last_fertilized(session, plant.id)),
    }


def _iso(value) -> str | None:
    return value.isoformat() if value else None


def _storage_info(session: Session, plant: Plant, label: str) -> dict | None:
    if plant.storage_box_id is None:
        return None
    box = session.get(StorageBox, plant.storage_box_id)
    if box is None:
        return None
    code = box_code(box)
    return {"box_code": code, "composite": f"{label}{code}"}


def serialize_photo(photo: Photo) -> dict:
    return {
        "id": photo.id,
        "plant_id": photo.plant_id,
        "url": f"/media/{photo.filename}",
        "thumbnail_url": f"/media/{photo.thumbnail}",
        "is_profile": photo.is_profile,
    }


def serialize_log(log: LogEntry) -> dict:
    return {
        "id": log.id,
        "plant_id": log.plant_id,
        "entry_date": log.entry_date.isoformat(),
        "text": log.text,
        "height_cm": log.height_cm,
        "bud_count": log.bud_count,
        "flower_count": log.flower_count,
        "harvested_count": log.harvested_count,
        "fertilized": log.fertilized,
    }


def serialize_disposal(disposal: Disposal) -> dict:
    return {
        "kind": disposal.kind,
        "reason": disposal.reason,
        "recipient": disposal.recipient,
        "disease_warning": disposal.disease_warning,
        "disposed_on": disposal.disposed_on.isoformat(),
    }


# --- collection routes (declared before /{plant_id} to avoid clashes) ------


@router.get("")
def list_plants(
    variety_id: int | None = None,
    include_gone: bool = False,
    session: Session = Depends(get_session),
) -> list[dict]:
    query = select(Plant)
    if variety_id is not None:
        query = query.where(Plant.variety_id == variety_id)
    # By default hide discarded/given-away plants — they stay only in the family tree.
    if not include_gone:
        query = query.where(Plant.state.not_in(_GONE_STATES))
    plants = session.exec(query.order_by(Plant.variety_id, Plant.ss, Plant.ddd)).all()
    return [serialize_plant(session, p) for p in plants]


@router.get("/tree")
def plant_tree(session: Session = Depends(get_session)) -> list[dict]:
    """Full family tree across all varieties (parent -> children via lineage)."""
    plants = session.exec(select(Plant)).all()
    children: dict[int, list[Plant]] = defaultdict(list)
    roots: list[Plant] = []
    for plant in plants:
        if plant.parent_plant_id is None:
            roots.append(plant)
        else:
            children[plant.parent_plant_id].append(plant)

    # Coalesce None (provisional plants) so sorting never compares None with int.
    order = lambda p: (p.variety_id or 0, p.ss or 0, p.ddd or 0)  # noqa: E731

    def build(plant: Plant) -> dict:
        node = serialize_plant(session, plant)
        node["children"] = [build(c) for c in sorted(children[plant.id], key=order)]
        return node

    return [build(r) for r in sorted(roots, key=order)]


@router.get("/summary")
def inventory_summary(session: Session = Depends(get_session)) -> dict:
    plants = session.exec(select(Plant)).all()
    by_state = Counter(p.state for p in plants)
    return {"total": len(plants), "by_state": dict(by_state)}


@router.get("/search")
def search_plants(q: str, session: Session = Depends(get_session)) -> list[dict]:
    """Find plants by code (BUM01000), storage code (BUM01000D0126) or nickname.

    Matches across all plants (incl. discarded/given-away), so an old label scans fine.
    """
    needle = q.strip().upper().replace(" ", "")
    if not needle:
        return []

    results = []
    for plant in session.exec(select(Plant)).all():
        data = serialize_plant(session, plant)
        full = data["full_code"] or ""
        composite = data["storage"]["composite"].upper() if data["storage"] else ""
        nickname = (plant.nickname or "").upper()

        # A scanned/typed value may be the bare code, or carry a storage/location suffix.
        code_match = full and (needle in full or full in needle)
        storage_match = composite and needle in composite
        nickname_match = nickname and needle in nickname
        if code_match or storage_match or nickname_match:
            results.append(data)

    results.sort(key=lambda d: d["full_code"] or d["label"])
    return results


@router.post("", status_code=201)
def create_plant(data: PlantCreate, session: Session = Depends(get_session)) -> dict:
    try:
        plant = plant_service.create_plant(session, data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return serialize_plant(session, plant)


# --- single-plant routes ---------------------------------------------------


@router.get("/{plant_id}")
def get_plant(plant_id: int, session: Session = Depends(get_session)) -> dict:
    plant = session.get(Plant, plant_id)
    if plant is None:
        raise HTTPException(status_code=404, detail="Plant niet gevonden.")

    data = serialize_plant(session, plant)
    parent = (
        session.get(Plant, plant.parent_plant_id) if plant.parent_plant_id else None
    )
    data["parent"] = serialize_plant(session, parent) if parent else None

    child_plants = session.exec(
        select(Plant)
        .where(Plant.parent_plant_id == plant_id)
        .order_by(Plant.variety_id, Plant.ss, Plant.ddd)
    ).all()
    data["children"] = [serialize_plant(session, c) for c in child_plants]

    photos = session.exec(select(Photo).where(Photo.plant_id == plant_id)).all()
    data["photos"] = [serialize_photo(p) for p in photos]

    # Full location history across seasons (current + past plantings).
    plantings = session.exec(
        select(Planting)
        .where(Planting.plant_id == plant_id)
        .order_by(Planting.planted_on)
    ).all()
    data["plantings"] = [serialize_planting(session, pl) for pl in plantings]

    # Logbook (newest first).
    logs = session.exec(
        select(LogEntry)
        .where(LogEntry.plant_id == plant_id)
        .order_by(LogEntry.entry_date.desc(), LogEntry.id.desc())
    ).all()
    data["logs"] = [serialize_log(log) for log in logs]

    # Disposal record (if the plant has left the collection).
    disposal = session.exec(
        select(Disposal).where(Disposal.plant_id == plant_id)
    ).first()
    data["disposal"] = serialize_disposal(disposal) if disposal else None

    # How many descendants this plant has had, and how many are still owned.
    data["descendants"] = descendant_tally(session, plant_id)

    # Per-season performance history (multi-year).
    data["yearly"] = plant_year_history(session, plant_id)
    return data


@router.get("/{plant_id}/summary")
def plant_summary(
    plant_id: int, session: Session = Depends(get_session)
) -> PlainTextResponse:
    """A hand-over text file: lineage, line averages and upcoming care tips."""
    try:
        filename, text = build_plant_summary(session, plant_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return PlainTextResponse(
        text, headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.patch("/{plant_id}")
def update_plant(
    plant_id: int, data: PlantUpdate, session: Session = Depends(get_session)
) -> dict:
    """Rename a plant's nickname (e.g. rename 'Links' once you know more)."""
    plant = session.get(Plant, plant_id)
    if plant is None:
        raise HTTPException(status_code=404, detail="Plant niet gevonden.")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(plant, field, value)
    session.add(plant)
    session.commit()
    session.refresh(plant)
    return serialize_plant(session, plant)


@router.put("/{plant_id}/variety")
def assign_variety(
    plant_id: int, data: VarietyAssign, session: Session = Depends(get_session)
) -> dict:
    """Assign a variety to a provisional plant once it's identified."""
    try:
        plant = plant_service.assign_variety(
            session,
            plant_id,
            variety_id=data.variety_id,
            new_variety_code=data.new_variety_code,
            new_variety_name=data.new_variety_name,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return serialize_plant(session, plant)


@router.delete("/{plant_id}", status_code=204)
def delete_plant(plant_id: int, session: Session = Depends(get_session)) -> None:
    plant = session.get(Plant, plant_id)
    if plant is None:
        raise HTTPException(status_code=404, detail="Plant niet gevonden.")
    # Keep lineage intact: don't allow deleting a plant that has descendants.
    if session.exec(select(Plant).where(Plant.parent_plant_id == plant_id)).first():
        raise HTTPException(
            status_code=409,
            detail="Deze plant heeft afstammelingen en kan niet verwijderd worden.",
        )

    for photo in session.exec(select(Photo).where(Photo.plant_id == plant_id)).all():
        delete_files(photo.filename, photo.thumbnail)
        session.delete(photo)
    session.delete(plant)
    session.commit()


# --- photos ----------------------------------------------------------------


@router.post("/{plant_id}/photos", status_code=201)
async def upload_photo(
    plant_id: int,
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
) -> dict:
    plant = session.get(Plant, plant_id)
    if plant is None:
        raise HTTPException(status_code=404, detail="Plant niet gevonden.")

    content = await file.read()
    try:
        filename, thumbnail = save_upload(content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    # The first photo of a plant automatically becomes its profile photo.
    is_first = (
        profile_photo_of(session, plant_id) is None
        and not session.exec(select(Photo).where(Photo.plant_id == plant_id)).first()
    )
    photo = Photo(
        plant_id=plant_id, filename=filename, thumbnail=thumbnail, is_profile=is_first
    )
    session.add(photo)
    session.commit()
    session.refresh(photo)
    return serialize_photo(photo)


@router.put("/{plant_id}/photos/{photo_id}/profile")
def set_profile_photo(
    plant_id: int, photo_id: int, session: Session = Depends(get_session)
) -> dict:
    photos = session.exec(select(Photo).where(Photo.plant_id == plant_id)).all()
    target = next((p for p in photos if p.id == photo_id), None)
    if target is None:
        raise HTTPException(status_code=404, detail="Foto niet gevonden.")
    for photo in photos:  # exactly one profile photo per plant
        photo.is_profile = photo.id == photo_id
        session.add(photo)
    session.commit()
    session.refresh(target)
    return serialize_photo(target)


@router.delete("/{plant_id}/photos/{photo_id}", status_code=204)
def delete_photo(
    plant_id: int, photo_id: int, session: Session = Depends(get_session)
) -> None:
    photo = session.get(Photo, photo_id)
    if photo is None or photo.plant_id != plant_id:
        raise HTTPException(status_code=404, detail="Foto niet gevonden.")
    was_profile = photo.is_profile
    delete_files(photo.filename, photo.thumbnail)
    session.delete(photo)
    session.commit()

    # If we removed the profile photo, promote another so the plant keeps an image.
    if was_profile:
        remaining = session.exec(
            select(Photo).where(Photo.plant_id == plant_id)
        ).first()
        if remaining:
            remaining.is_profile = True
            session.add(remaining)
            session.commit()


# --- winter / storage actions ----------------------------------------------


@router.post("/{plant_id}/lift")
def lift(
    plant_id: int, data: LiftRequest, session: Session = Depends(get_session)
) -> dict:
    """Rooien: end the season and return the plant to storage."""
    try:
        plant = planting_service.lift_plant(session, plant_id, data.lifted_on)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return serialize_plant(session, plant)


@router.post("/{plant_id}/survive-winter")
def survive_winter(plant_id: int, session: Session = Depends(get_session)) -> dict:
    """Mark a still-planted plant as having survived the winter in the ground."""
    try:
        plant = planting_service.mark_survived_winter(session, plant_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return serialize_plant(session, plant)


@router.patch("/{plant_id}/eye-status")
def set_eye_status(
    plant_id: int, data: EyeStatusUpdate, session: Session = Depends(get_session)
) -> dict:
    plant = session.get(Plant, plant_id)
    if plant is None:
        raise HTTPException(status_code=404, detail="Plant niet gevonden.")
    plant.eye_status = data.eye_status
    session.add(plant)
    session.commit()
    session.refresh(plant)
    return serialize_plant(session, plant)


@router.put("/{plant_id}/storage")
def assign_storage(
    plant_id: int, data: StorageAssign, session: Session = Depends(get_session)
) -> dict:
    plant = session.get(Plant, plant_id)
    if plant is None:
        raise HTTPException(status_code=404, detail="Plant niet gevonden.")
    try:
        assign_to_box(session, plant, data.number, data.year or date.today().year)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    session.commit()
    session.refresh(plant)
    return serialize_plant(session, plant)


@router.delete("/{plant_id}/storage", status_code=204)
def remove_from_storage(plant_id: int, session: Session = Depends(get_session)) -> None:
    plant = session.get(Plant, plant_id)
    if plant is None:
        raise HTTPException(status_code=404, detail="Plant niet gevonden.")
    release_box(session, plant)
    session.commit()


# --- logbook ---------------------------------------------------------------


@router.post("/{plant_id}/logs", status_code=201)
def add_log(
    plant_id: int, data: LogEntryCreate, session: Session = Depends(get_session)
) -> dict:
    plant = session.get(Plant, plant_id)
    if plant is None:
        raise HTTPException(status_code=404, detail="Plant niet gevonden.")
    log = LogEntry(
        plant_id=plant_id,
        entry_date=data.entry_date or date.today(),
        text=data.text,
        height_cm=data.height_cm,
        bud_count=data.bud_count,
        flower_count=data.flower_count,
        harvested_count=data.harvested_count,
        fertilized=data.fertilized,
    )
    session.add(log)
    session.commit()
    session.refresh(log)
    return serialize_log(log)


@router.delete("/{plant_id}/logs/{log_id}", status_code=204)
def delete_log(
    plant_id: int, log_id: int, session: Session = Depends(get_session)
) -> None:
    log = session.get(LogEntry, log_id)
    if log is None or log.plant_id != plant_id:
        raise HTTPException(status_code=404, detail="Logboek-item niet gevonden.")
    session.delete(log)
    session.commit()


# --- disposal --------------------------------------------------------------


@router.post("/{plant_id}/dispose")
def dispose(
    plant_id: int, data: DisposalCreate, session: Session = Depends(get_session)
) -> dict:
    """Discard or give away a plant (kept in the family tree, hidden from the active list)."""
    try:
        plant = disposal_service.dispose_plant(
            session,
            plant_id,
            kind=data.kind,
            reason=data.reason,
            recipient=data.recipient,
            disease_warning=data.disease_warning,
            disposed_on=data.disposed_on,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return serialize_plant(session, plant)


@router.post("/{plant_id}/not-emerged")
def not_emerged(plant_id: int, session: Session = Depends(get_session)) -> dict:
    """ "Niet opgekomen" — counts as discarded, with a logbook note."""
    try:
        plant = disposal_service.mark_not_emerged(session, plant_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return serialize_plant(session, plant)
