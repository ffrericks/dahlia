from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class StorageBox(SQLModel, table=True):
    """A winter-storage box, coded D + number + 2-digit year (e.g. D0126).

    Boxes are registered fresh each winter (year-scoped). A box disappears once all
    its tubers have been planted out / left it.
    """

    __table_args__ = (UniqueConstraint("number", "year", name="uq_box_number_year"),)

    id: int | None = Field(default=None, primary_key=True)
    number: int
    year: int  # full year; the code shows the last 2 digits
