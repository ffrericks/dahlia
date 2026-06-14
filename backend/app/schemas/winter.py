from datetime import date

from pydantic import BaseModel, field_validator

EYE_STATUSES = {"awaiting_eye", "has_eye", "blind"}


class EyeStatusUpdate(BaseModel):
    eye_status: str

    @field_validator("eye_status")
    @classmethod
    def check(cls, value: str) -> str:
        if value not in EYE_STATUSES:
            raise ValueError("Onbekende oog-status.")
        return value


class LiftRequest(BaseModel):
    lifted_on: date | None = None  # defaults to today


class StorageAssign(BaseModel):
    number: int
    year: int | None = None  # defaults to the current year

    @field_validator("number")
    @classmethod
    def check_number(cls, value: int) -> int:
        if value < 1 or value > 99:
            raise ValueError("Doosnummer moet tussen 1 en 99 liggen.")
        return value
