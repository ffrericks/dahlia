from sqlmodel import Field, SQLModel


class AppSettings(SQLModel, table=True):
    """App-wide settings. A single row (id=1) holds all of them."""

    id: int | None = Field(default=None, primary_key=True)
    # Base URL the tool is reachable at (used for QR links / the API view later).
    tool_url: str | None = Field(default=None)
    # Whether fertilizing one plant counts for every plant in the same bak.
    auto_fertilize_bak: bool = Field(default=True)
    # Default name for a new garden spot when none is given.
    default_garden_name: str | None = Field(default=None)
