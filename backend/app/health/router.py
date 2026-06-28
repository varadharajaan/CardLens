"""Health probe endpoints used by local scripts and the cloud platform."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app import __version__
from app.config import settings
from app.shared.constants.api_paths import ApiPaths
from app.shared.database.session import get_db
from app.shared.errors.exceptions import DependencyUnavailableError

router = APIRouter(tags=["health"])


@router.get(ApiPaths.HEALTHZ, summary="Liveness probe")
def healthz() -> dict[str, Any]:
    """Return a static liveness signal; does not touch dependencies."""
    return {"status": "ok", "service": settings.app_name, "version": __version__}


@router.get(ApiPaths.READYZ, summary="Readiness probe")
def readyz(db: Session = Depends(get_db)) -> dict[str, Any]:
    """Return readiness after verifying the database is reachable."""
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        raise DependencyUnavailableError("Database is not reachable.") from exc
    return {"status": "ready", "database": "up"}
