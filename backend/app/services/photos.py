import io
import uuid

from PIL import Image, ImageOps
from sqlmodel import Session, select

from ..config import settings
from ..models import Photo, Plant

# Downscale on upload to keep the data folder small (personal use, manual backup).
_MAX_IMAGE = 1600
_MAX_THUMB = 320


def save_upload(content: bytes) -> tuple[str, str]:
    """Store an uploaded image as a downscaled JPEG + thumbnail. Returns (filename, thumbname)."""
    settings.photos_dir.mkdir(parents=True, exist_ok=True)
    base = uuid.uuid4().hex
    filename = f"{base}.jpg"
    thumbname = f"{base}_thumb.jpg"

    try:
        with Image.open(io.BytesIO(content)) as img:
            # Honor camera EXIF rotation, then flatten to RGB so JPEG always works.
            img = ImageOps.exif_transpose(img)
            rgb = img.convert("RGB")

            full = rgb.copy()
            full.thumbnail((_MAX_IMAGE, _MAX_IMAGE))
            full.save(settings.photos_dir / filename, "JPEG", quality=85)

            thumb = rgb.copy()
            thumb.thumbnail((_MAX_THUMB, _MAX_THUMB))
            thumb.save(settings.photos_dir / thumbname, "JPEG", quality=80)
    except OSError as exc:  # Pillow raises OSError for non-images / corrupt files
        raise ValueError("Geen geldige afbeelding.") from exc

    return filename, thumbname


def delete_files(filename: str, thumbnail: str) -> None:
    for name in (filename, thumbnail):
        path = settings.photos_dir / name
        if path.exists():
            path.unlink()


def profile_photo_of(session: Session, plant_id: int) -> Photo | None:
    photos = session.exec(select(Photo).where(Photo.plant_id == plant_id)).all()
    for photo in photos:
        if photo.is_profile:
            return photo
    return None


def variety_image_thumb(session: Session, variety_id: int) -> str | None:
    """The variety's representative image: the profile photo of its lowest-numbered plant."""
    plants = session.exec(
        select(Plant)
        .where(Plant.variety_id == variety_id)
        .order_by(Plant.ss, Plant.ddd)
    ).all()
    for plant in plants:
        photo = profile_photo_of(session, plant.id)
        if photo:
            return f"/media/{photo.thumbnail}"
    return None


def effective_thumbnail(session: Session, plant: Plant) -> str | None:
    """A plant's own profile photo, or its variety's image (so splits share the parent's photo)."""
    photo = profile_photo_of(session, plant.id)
    if photo:
        return f"/media/{photo.thumbnail}"
    return variety_image_thumb(session, plant.variety_id)
