from sqlmodel import Session

from ..models import AppSettings


def get_settings(session: Session) -> AppSettings:
    """Return the single settings row, creating it with defaults on first use."""
    settings = session.get(AppSettings, 1)
    if settings is None:
        settings = AppSettings(id=1)
        session.add(settings)
        session.commit()
        session.refresh(settings)
    return settings
