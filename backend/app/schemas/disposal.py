from datetime import date

from pydantic import BaseModel, field_validator


class DisposalCreate(BaseModel):
    kind: str  # discarded | given_away
    reason: str | None = None
    recipient: str | None = None  # who received it (give-away)
    disease_warning: bool = False
    disposed_on: date | None = None

    @field_validator("kind")
    @classmethod
    def check_kind(cls, value: str) -> str:
        if value not in ("discarded", "given_away"):
            raise ValueError("Soort afvoer moet 'discarded' of 'given_away' zijn.")
        return value

    @field_validator("reason", "recipient")
    @classmethod
    def clean(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None
