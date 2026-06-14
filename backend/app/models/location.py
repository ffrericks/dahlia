from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class Location(SQLModel, table=True):
    """A place a plant can stand: a garden spot (T##) or a pot/bak (B##).

    A container holding more than one plant is a "bak"; with one it's a "pot" —
    that distinction is derived from the number of active plantings, not stored.
    Locations persist as empty places when their plants leave.
    """

    __table_args__ = (UniqueConstraint("kind", "number", name="uq_location_number"),)

    id: int | None = Field(default=None, primary_key=True)
    kind: str  # "garden" (T##) | "container" (B##)
    number: int  # the ## part, sequential per kind
    name: str | None = Field(default=None)
