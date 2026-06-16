from datetime import date

from pydantic import BaseModel, field_validator, model_validator


class LogEntryCreate(BaseModel):
    text: str | None = None
    height_cm: int | None = None
    bud_count: int | None = None
    flower_count: int | None = None
    harvested_count: int | None = None
    fertilized: bool = False
    entry_date: date | None = None

    @field_validator("text")
    @classmethod
    def clean_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None

    @field_validator("height_cm", "bud_count", "flower_count", "harvested_count")
    @classmethod
    def non_negative(cls, value: int | None) -> int | None:
        if value is not None and value < 0:
            raise ValueError("Waarde mag niet negatief zijn.")
        return value

    @model_validator(mode="after")
    def not_empty(self):
        has_metric = any(
            v is not None
            for v in (
                self.height_cm,
                self.bud_count,
                self.flower_count,
                self.harvested_count,
            )
        )
        if not self.text and not has_metric and not self.fertilized:
            raise ValueError(
                "Een logboek-item heeft tekst, een meting of 'bemest' nodig."
            )
        return self
