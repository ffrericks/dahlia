from datetime import date

from pydantic import BaseModel, field_validator, model_validator


class PlantingCreate(BaseModel):
    plant_id: int

    # Plant into an existing location...
    location_id: int | None = None
    # ...or create a new one (garden spot or pot/bak) on the spot.
    new_location_kind: str | None = None
    new_location_name: str | None = None

    position: str | None = None  # where in a bak the plant sits
    planted_on: date | None = None  # defaults to today on the server

    @field_validator("new_location_kind")
    @classmethod
    def check_kind(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if value not in ("garden", "container"):
            raise ValueError("Soort locatie moet 'garden' of 'container' zijn.")
        return value

    @model_validator(mode="after")
    def check_location(self):
        if self.location_id is None and self.new_location_kind is None:
            raise ValueError("Kies een bestaande locatie of maak een nieuwe.")
        return self
