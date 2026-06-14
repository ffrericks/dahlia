from sqlmodel import Field, SQLModel


class Variety(SQLModel, table=True):
    """A dahlia variety (soort), identified by a unique 3-letter code."""

    id: int | None = Field(default=None, primary_key=True)
    # 3-letter code, stored uppercase and unique. Used as the prefix of every plant code.
    code: str = Field(index=True, unique=True)
    # Optional: a seedling's variety may stay unnamed until it proves itself.
    name: str | None = Field(default=None)
    description: str | None = Field(default=None)
    # Optional Wikipedia article; its first paragraph can be imported as the description.
    wikipedia_url: str | None = Field(default=None)
