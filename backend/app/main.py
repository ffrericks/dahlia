from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import settings
from .db import init_db
from .routers import (
    care,
    health,
    insights,
    locations,
    plantings,
    plants,
    season,
    settings as settings_router,
    storage,
    varieties,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Dahlia Tool", version="0.1.0", lifespan=lifespan)

app.include_router(health.router, prefix="/api")
app.include_router(varieties.router, prefix="/api")
app.include_router(plants.router, prefix="/api")
app.include_router(locations.router, prefix="/api")
app.include_router(plantings.router, prefix="/api")
app.include_router(care.router, prefix="/api")
app.include_router(storage.router, prefix="/api")
app.include_router(season.router, prefix="/api")
app.include_router(insights.router, prefix="/api")
app.include_router(settings_router.router, prefix="/api")

# Serve uploaded photos from the data volume. check_dir=False because the folder is
# created at startup (init_db), which runs after this module is imported.
app.mount("/media", StaticFiles(directory=settings.photos_dir, check_dir=False), name="media")


# Serve the built frontend when it is present (production image). During local dev the
# folder is absent, so only the API runs and Vite's dev server proxies /api to it.
if settings.static_dir.is_dir():
    assets_dir = settings.static_dir / "assets"
    if assets_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str) -> FileResponse:
        # Unknown /api/* paths are real 404s, not the SPA shell.
        if full_path.startswith("api"):
            raise HTTPException(status_code=404, detail="Not found")
        # Serve a real static file if it exists; otherwise return index.html so the
        # single-page app can handle client-side routing.
        candidate = settings.static_dir / full_path
        if full_path and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(settings.static_dir / "index.html")
