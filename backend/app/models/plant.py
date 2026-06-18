from datetime import date

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class Plant(SQLModel, table=True):
    """A concrete plant/tuber instance. Its number is `SSDDD` within its variety.

    SS = stam (founder) index 01-99; DDD = descendant counter 000-999 (000 = the
    stam plant itself). The full code is variety.code + this number, e.g. WIT01000.
    """

    __table_args__ = (
        UniqueConstraint("variety_id", "ss", "ddd", name="uq_plant_number"),
    )

    id: int | None = Field(default=None, primary_key=True)
    # Variety/number are None for a provisional plant (unknown origin) until assigned.
    variety_id: int | None = Field(default=None, foreign_key="variety.id", index=True)
    ss: int | None = Field(default=None)  # stam index
    ddd: int | None = Field(default=None)  # descendant counter within the stam

    # Free-text label for a plant whose variety isn't known yet (e.g. "Links").
    nickname: str | None = Field(default=None)

    # Lineage: the mother plant this came from (None for purchased/gifted/unknown stock).
    parent_plant_id: int | None = Field(
        default=None, foreign_key="plant.id", index=True
    )

    # split | seedling | purchased | gifted | unknown
    origin: str
    # stored | planted | discarded | given_away | survived_winter
    state: str = Field(default="stored")

    # Set during winter storage / early spring: awaiting_eye | has_eye | blind
    eye_status: str | None = Field(default=None)
    # The winter-storage box this stored tuber sits in (None if not boxed).
    storage_box_id: int | None = Field(
        default=None, foreign_key="storagebox.id", index=True
    )
    # Set when discarded for disease (Phase 6); flags siblings in the family tree.
    disease_warning: bool = Field(default=False)
    # When the plant was registered (for the active-plants-over-time chart).
    created_on: date | None = Field(default=None)
    # True while a cutting is rooting in its own pot (before it's planted out).
    rooting: bool = Field(default=False)
