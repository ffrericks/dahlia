from datetime import date

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class Disposal(SQLModel, table=True):
    """Record of a plant leaving the collection: discarded or given away.

    The plant itself is never deleted (lineage stays intact) — its state changes and
    this record holds the why/to-whom. One disposal per plant.
    """

    __table_args__ = (UniqueConstraint("plant_id", name="uq_disposal_plant"),)

    id: int | None = Field(default=None, primary_key=True)
    plant_id: int = Field(foreign_key="plant.id", index=True)
    kind: str  # discarded | given_away
    reason: str | None = Field(default=None)
    recipient: str | None = Field(default=None)  # who received it (give-away)
    disease_warning: bool = Field(default=False)
    disposed_on: date
