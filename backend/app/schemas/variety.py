import re

from pydantic import BaseModel, ConfigDict, field_validator

# A variety code is exactly three letters (case-insensitive on input, stored uppercase).
_CODE_RE = re.compile(r"^[A-Za-z]{3}$")


def _clean_name(value: str | None) -> str | None:
    """Empty/blank names are stored as None (a variety may stay unnamed)."""
    if value is None:
        return None
    value = value.strip()
    return value or None


class VarietyCreate(BaseModel):
    code: str
    name: str | None = None
    description: str | None = None
    wikipedia_url: str | None = None

    @field_validator("code")
    @classmethod
    def normalize_code(cls, value: str) -> str:
        value = value.strip()
        if not _CODE_RE.match(value):
            raise ValueError("Code moet uit precies 3 letters bestaan.")
        return value.upper()

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str | None) -> str | None:
        return _clean_name(value)


class VarietyUpdate(BaseModel):
    # Code is intentionally absent: it is fixed at registration because plant codes depend on it.
    name: str | None = None
    description: str | None = None
    wikipedia_url: str | None = None

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str | None) -> str | None:
        return _clean_name(value)


class VarietyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str | None
    description: str | None
    wikipedia_url: str | None
    plant_count: int = 0
    image_thumbnail: str | None = None


class DescriptionRequest(BaseModel):
    url: str
