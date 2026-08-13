"""
routers/health.py — endpoint GET /health.

Comprueba que el proceso responde y, si es posible, que la SQLite del ETL
es legible. La comprobación de BD es local (SELECT 1); no requiere un service.
"""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path

from fastapi import APIRouter, Depends

from reportes_api.config import Settings
from reportes_api.deps import settings_dep
from reportes_api.schemas import HealthResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


def _db_ok(db_path: Path) -> bool:
    """
    True si el archivo SQLite existe y se puede abrir en solo lectura.

    mode=ro (read-only): la API de health NO escribe en la BD del ETL.
    """
    if not db_path.is_file():
        return False
    try:
        with sqlite3.connect(f"file:{db_path}?mode=ro", uri=True) as conn:
            conn.execute("SELECT 1")
        return True
    except sqlite3.Error as exc:
        logger.warning("Health: no se pudo leer BD %s: %s", db_path, exc)
        return False


@router.get("/health", response_model=HealthResponse)
def health(settings: Settings = Depends(settings_dep)) -> HealthResponse:
    """
    GET /health

    - status "ok"       → proceso vivo y BD legible
    - status "degraded" → proceso vivo pero BD no accesible (ruta mal / ETL no corrido)
    """
    ok = _db_ok(settings.db_path)
    if not ok:
        logger.warning("Health degraded: db_path=%s", settings.db_path)
    return HealthResponse(
        status="ok" if ok else "degraded",
        db_ok=ok,
        db_path=str(settings.db_path),
    )
