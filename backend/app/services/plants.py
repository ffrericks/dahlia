import re
from datetime import date

from sqlmodel import Session, select

from ..models import Plant, Variety
from ..schemas.plant import PlantCreate
from .numbering import next_ddd, next_stam

_CODE_RE = re.compile(r"^[A-Z]{3}$")


def _create_variety_inline(
    session: Session, code: str | None, name: str | None
) -> Variety:
    """Create the new variety a seedling or new-variety purchase belongs to."""
    if not code:
        raise ValueError("Een nieuwe soort heeft een code nodig.")
    code = code.strip().upper()
    if not _CODE_RE.match(code):
        raise ValueError("Code moet uit precies 3 letters bestaan.")
    if session.exec(select(Variety).where(Variety.code == code)).first():
        raise ValueError(f"Soortcode '{code}' bestaat al.")

    cleaned_name = name.strip() if name else None
    variety = Variety(code=code, name=cleaned_name or None)
    session.add(variety)
    session.flush()  # assign an id without ending the transaction
    return variety


def create_plant(session: Session, data: PlantCreate) -> Plant:
    """Create a plant, assigning its number from its origin and lineage."""
    if data.origin == "unknown":
        # Provisional plant: no variety/number yet, just a nickname.
        variety_id = ss = ddd = parent_id = None

    elif data.origin == "split":
        parent = session.get(Plant, data.parent_plant_id)
        if parent is None:
            raise ValueError("Moederplant niet gevonden.")
        if parent.variety_id is None:
            raise ValueError("De moederplant heeft nog geen soort; wijs die eerst toe.")
        variety_id = parent.variety_id
        ss = parent.ss  # a split stays in the parent's stam
        ddd = next_ddd(session, variety_id, ss)
        parent_id = parent.id

    elif data.origin == "seedling":
        parent = session.get(Plant, data.parent_plant_id)
        if parent is None:
            raise ValueError("Moederplant niet gevonden.")
        # A seedling becomes a brand-new variety; it is plant 01000 there.
        variety = _create_variety_inline(
            session, data.new_variety_code, data.new_variety_name
        )
        variety_id = variety.id
        ss, ddd = 1, 0
        parent_id = parent.id

    else:  # purchased / gifted — no mother plant, starts a fresh stam
        if data.variety_id is not None:
            variety = session.get(Variety, data.variety_id)
            if variety is None:
                raise ValueError("Soort niet gevonden.")
            variety_id = variety.id
            ss = next_stam(session, variety_id)
        else:
            variety = _create_variety_inline(
                session, data.new_variety_code, data.new_variety_name
            )
            variety_id = variety.id
            ss = 1
        ddd = 0
        parent_id = None

    plant = Plant(
        variety_id=variety_id,
        ss=ss,
        ddd=ddd,
        nickname=data.nickname,
        parent_plant_id=parent_id,
        origin=data.origin,
        state=data.state,
        created_on=date.today(),
    )
    session.add(plant)
    session.commit()
    session.refresh(plant)
    return plant


def assign_variety(
    session: Session,
    plant_id: int,
    variety_id: int | None,
    new_variety_code: str | None,
    new_variety_name: str | None,
) -> Plant:
    """Give a provisional plant a variety once it's identified (e.g. at bloom)."""
    plant = session.get(Plant, plant_id)
    if plant is None:
        raise ValueError("Plant niet gevonden.")
    if plant.variety_id is not None:
        raise ValueError("Deze plant heeft al een soort.")

    if variety_id is not None:
        variety = session.get(Variety, variety_id)
        if variety is None:
            raise ValueError("Soort niet gevonden.")
    else:
        variety = _create_variety_inline(session, new_variety_code, new_variety_name)

    # Compute the stam index BEFORE assigning, so autoflush doesn't see ss=None.
    new_ss = next_stam(session, variety.id)
    plant.variety_id = variety.id
    plant.ss = new_ss
    plant.ddd = 0
    session.add(plant)
    session.commit()
    session.refresh(plant)
    return plant
