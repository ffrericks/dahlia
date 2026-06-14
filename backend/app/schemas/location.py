from pydantic import BaseModel, field_validator

LOCATION_KINDS = {"garden", "container"}


def _clean(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value or None


class LocationCreate(BaseModel):
    kind: str
    name: str | None = None

    @field_validator("kind")
    @classmethod
    def check_kind(cls, value: str) -> str:
        if value not in LOCATION_KINDS:
            raise ValueError("Soort locatie moet 'garden' of 'container' zijn.")
        return value

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str | None) -> str | None:
        return _clean(value)


class LocationUpdate(BaseModel):
    name: str | None = None

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str | None) -> str | None:
        return _clean(value)
