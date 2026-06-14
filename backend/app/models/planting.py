from datetime import date

from sqlmodel import Field, SQLModel


class Planting(SQLModel, table=True):
    """A plant standing in a location for one season (planting date -> lifting date).

    Plantings are never deleted, so a plant keeps a full multi-year history. The
    current planting is the one with lifted_on still None (lifting arrives in Phase 5).
    """

    id: int | None = Field(default=None, primary_key=True)
    plant_id: int = Field(foreign_key="plant.id", index=True)
    location_id: int = Field(foreign_key="location.id", index=True)
    planted_on: date
    lifted_on: date | None = Field(default=None)
    # Where in a bak the plant sits (e.g. "voor", "achter", a slot label).
    position: str | None = Field(default=None)
