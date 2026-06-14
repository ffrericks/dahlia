import re

from pydantic import BaseModel, field_validator, model_validator

ORIGINS = {"split", "seedling", "purchased", "gifted", "unknown"}
STATES = {"stored", "planted", "discarded", "given_away", "survived_winter"}
_CODE_RE = re.compile(r"^[A-Za-z]{3}$")


class PlantCreate(BaseModel):
    origin: str

    # split / seedling: the mother plant.
    parent_plant_id: int | None = None

    # purchased / gifted into an EXISTING variety.
    variety_id: int | None = None

    # seedling, or purchased/gifted of a brand-new variety: create the variety inline.
    new_variety_code: str | None = None
    new_variety_name: str | None = None

    # Label for a provisional (unknown) plant, e.g. "Links".
    nickname: str | None = None

    state: str = "stored"

    @field_validator("origin")
    @classmethod
    def check_origin(cls, value: str) -> str:
        if value not in ORIGINS:
            raise ValueError(f"Onbekende herkomst: {value}")
        return value

    @field_validator("state")
    @classmethod
    def check_state(cls, value: str) -> str:
        if value not in STATES:
            raise ValueError(f"Onbekende status: {value}")
        return value

    @field_validator("new_variety_code")
    @classmethod
    def normalize_code(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not _CODE_RE.match(value):
            raise ValueError("Code voor de nieuwe soort moet uit precies 3 letters bestaan.")
        return value.upper()

    @field_validator("nickname")
    @classmethod
    def clean_nickname(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None

    @model_validator(mode="after")
    def check_combination(self):
        if self.origin in ("split", "seedling") and self.parent_plant_id is None:
            raise ValueError("Een afsplitsing of zaailing heeft een moederplant nodig.")
        if self.origin == "seedling" and self.new_variety_code is None:
            raise ValueError("Een zaailing wordt een nieuwe soort en heeft een code nodig.")
        if self.origin in ("purchased", "gifted"):
            if self.variety_id is None and self.new_variety_code is None:
                raise ValueError(
                    "Kies een bestaande soort of geef een code voor een nieuwe soort."
                )
        # 'unknown' needs nothing: no variety, no parent — just an optional nickname.
        return self


class VarietyAssign(BaseModel):
    """Assign a variety to a provisional (unknown) plant once you know what it is."""

    variety_id: int | None = None
    new_variety_code: str | None = None
    new_variety_name: str | None = None

    @field_validator("new_variety_code")
    @classmethod
    def normalize_code(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not _CODE_RE.match(value):
            raise ValueError("Code voor de nieuwe soort moet uit precies 3 letters bestaan.")
        return value.upper()

    @model_validator(mode="after")
    def check(self):
        if self.variety_id is None and self.new_variety_code is None:
            raise ValueError("Kies een bestaande soort of geef een code voor een nieuwe soort.")
        return self


class PlantUpdate(BaseModel):
    nickname: str | None = None

    @field_validator("nickname")
    @classmethod
    def clean_nickname(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None
