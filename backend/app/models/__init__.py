"""SQLModel entities. Importing them here registers their tables for create_all()."""

from .app_settings import AppSettings
from .disposal import Disposal
from .location import Location
from .log_entry import LogEntry
from .photo import Photo
from .plant import Plant
from .planting import Planting
from .storage_box import StorageBox
from .variety import Variety

__all__ = [
    "Variety",
    "Plant",
    "Photo",
    "Location",
    "Planting",
    "StorageBox",
    "LogEntry",
    "Disposal",
    "AppSettings",
]
