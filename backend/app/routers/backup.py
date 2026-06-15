import io
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, Response, UploadFile

from ..config import settings
from ..db import engine, init_db

router = APIRouter(prefix="/backup", tags=["backup"])

# Typed confirmation required before an import overwrites everything.
_CONFIRM_PHRASE = "dahlia tool"


@router.get("/export")
def export_backup() -> Response:
    """Download a zip with the database + photos (a full backup)."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        db_path = settings.data_dir / "dahlia.db"
        if db_path.exists():
            archive.write(db_path, "dahlia.db")
        if settings.photos_dir.exists():
            for photo in settings.photos_dir.iterdir():
                if photo.is_file():
                    archive.write(photo, f"photos/{photo.name}")

    filename = f"dahlia-backup-{datetime.now().strftime('%Y%m%d-%H%M')}.zip"
    return Response(
        content=buffer.getvalue(),
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/import")
async def import_backup(
    confirm: str = Form(...),
    file: UploadFile = File(...),
) -> dict:
    """Restore from a backup zip. Overwrites the current data — gated by a typed phrase."""
    if confirm.strip().lower() != _CONFIRM_PHRASE:
        raise HTTPException(status_code=400, detail="Typ 'dahlia tool' om te bevestigen.")

    raw = await file.read()
    try:
        archive = zipfile.ZipFile(io.BytesIO(raw))
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Geen geldig back-upbestand (zip).")

    names = archive.namelist()
    if "dahlia.db" not in names:
        raise HTTPException(status_code=400, detail="Back-up bevat geen database (dahlia.db).")
    # Reject anything outside the expected, safe entries (no path traversal).
    for name in names:
        if name != "dahlia.db" and not name.startswith("photos/"):
            continue
        if ".." in name or name.startswith("/"):
            raise HTTPException(status_code=400, detail="Ongeldig pad in back-up.")

    # Close DB connections so the file can be replaced.
    engine.dispose()

    # Safety net: keep the current data before overwriting it.
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_dir = settings.data_dir / "_backups" / f"pre-import-{stamp}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    db_path = settings.data_dir / "dahlia.db"
    if db_path.exists():
        shutil.copy2(db_path, backup_dir / "dahlia.db")
    if settings.photos_dir.exists():
        shutil.copytree(settings.photos_dir, backup_dir / "photos", dirs_exist_ok=True)

    # Replace the database.
    with archive.open("dahlia.db") as src, open(db_path, "wb") as dst:
        shutil.copyfileobj(src, dst)

    # Replace photos with those from the backup.
    if settings.photos_dir.exists():
        shutil.rmtree(settings.photos_dir)
    settings.photos_dir.mkdir(parents=True, exist_ok=True)
    for name in names:
        if name.startswith("photos/") and not name.endswith("/"):
            target = settings.photos_dir / Path(name).name
            with archive.open(name) as src, open(target, "wb") as dst:
                shutil.copyfileobj(src, dst)

    # Ensure schema/migrations on the imported database.
    init_db()
    return {"ok": True, "backup_of_previous": str(backup_dir)}
