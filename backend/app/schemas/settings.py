from pydantic import BaseModel, ConfigDict, field_validator


def _clean(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip().rstrip("/")  # drop a trailing slash so links build cleanly
    return value or None


class SettingsRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tool_url: str | None
    auto_fertilize_bak: bool
    default_garden_name: str | None


class SettingsUpdate(BaseModel):
    tool_url: str | None = None
    auto_fertilize_bak: bool | None = None
    default_garden_name: str | None = None

    @field_validator("tool_url")
    @classmethod
    def clean_url(cls, value: str | None) -> str | None:
        return _clean(value)

    @field_validator("default_garden_name")
    @classmethod
    def clean_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None
