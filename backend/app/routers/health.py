from fastapi import APIRouter

from .. import __version__

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    """Liveness check used by the frontend and any container health probe."""
    return {"status": "ok", "version": __version__}
