from sqlmodel import Session, select

from ..models import Plant, StorageBox, Variety
from .numbering import format_number


def box_code(box: StorageBox) -> str:
    return f"D{box.number:02d}{box.year % 100:02d}"


def plants_in_box(session: Session, box_id: int) -> list[Plant]:
    return list(session.exec(select(Plant).where(Plant.storage_box_id == box_id)).all())


def _delete_box_if_empty(session: Session, box_id: int | None) -> None:
    """A box disappears once it holds no more tubers."""
    if box_id is None:
        return
    if not plants_in_box(session, box_id):
        box = session.get(StorageBox, box_id)
        if box:
            session.delete(box)


def get_or_create_box(session: Session, number: int, year: int) -> StorageBox:
    box = session.exec(
        select(StorageBox).where(StorageBox.number == number, StorageBox.year == year)
    ).first()
    if box is None:
        box = StorageBox(number=number, year=year)
        session.add(box)
        session.flush()
    return box


def assign_to_box(session: Session, plant: Plant, number: int, year: int) -> StorageBox:
    if plant.state != "stored":
        raise ValueError("Alleen knollen in opslag kunnen in een doos.")
    old_box_id = plant.storage_box_id
    box = get_or_create_box(session, number, year)
    plant.storage_box_id = box.id
    session.add(plant)
    session.flush()  # so the empty-check below sees the change
    if old_box_id and old_box_id != box.id:
        _delete_box_if_empty(session, old_box_id)
    return box


def release_box(session: Session, plant: Plant) -> None:
    """Take a plant out of its box (e.g. when planted out); drop the box if now empty."""
    old_box_id = plant.storage_box_id
    if old_box_id is None:
        return
    plant.storage_box_id = None
    session.add(plant)
    session.flush()
    _delete_box_if_empty(session, old_box_id)


def serialize_box(session: Session, box: StorageBox) -> dict:
    plants = []
    for plant in plants_in_box(session, box.id):
        variety = session.get(Variety, plant.variety_id)
        plants.append(
            {
                "plant_id": plant.id,
                "full_code": f"{variety.code}{format_number(plant.ss, plant.ddd)}",
                "variety_name": variety.name,
                "eye_status": plant.eye_status,
            }
        )
    return {
        "id": box.id,
        "number": box.number,
        "year": box.year,
        "code": box_code(box),
        "plants": plants,
    }
