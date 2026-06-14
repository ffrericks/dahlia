from datetime import date

from sqlmodel import Field, SQLModel


class LogEntry(SQLModel, table=True):
    """A logbook entry for a plant: free text plus optional measurements."""

    id: int | None = Field(default=None, primary_key=True)
    plant_id: int = Field(foreign_key="plant.id", index=True)
    entry_date: date
    text: str | None = Field(default=None)
    height_cm: int | None = Field(default=None)
    bud_count: int | None = Field(default=None)
    flower_count: int | None = Field(default=None)
    harvested_count: int | None = Field(default=None)
