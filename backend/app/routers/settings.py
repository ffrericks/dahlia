from fastapi import APIRouter, Depends
from sqlmodel import Session

from ..db import get_session
from ..schemas.settings import SettingsRead, SettingsUpdate
from ..services.settings import get_settings

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=SettingsRead)
def read_settings(session: Session = Depends(get_session)) -> SettingsRead:
    return get_settings(session)


@router.put("", response_model=SettingsRead)
def update_settings(
    data: SettingsUpdate, session: Session = Depends(get_session)
) -> SettingsRead:
    settings = get_settings(session)
    # Only change fields the client actually sent.
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(settings, field, value)
    session.add(settings)
    session.commit()
    session.refresh(settings)
    return settings
