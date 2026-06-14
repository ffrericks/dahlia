from sqlmodel import Field, SQLModel


class Photo(SQLModel, table=True):
    """A photo of a plant. Files live in the photos data folder (downscaled + thumbnail).

    One photo per plant may be the profile; that profile photo also represents the
    variety. A plant without its own photos falls back to the variety's image.
    """

    id: int | None = Field(default=None, primary_key=True)
    plant_id: int = Field(foreign_key="plant.id", index=True)
    filename: str  # downscaled full-size image
    thumbnail: str  # small thumbnail
    is_profile: bool = Field(default=False)
