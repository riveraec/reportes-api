"""
routers/runs.py — endpoint POST /runs.

Recibe RunRequest (opcional), delega a run_service y traduce errores a HTTP.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException

from reportes_api.config import Settings
from reportes_api.deps import settings_dep
from reportes_api.schemas import RunRequest, RunResponse
from reportes_api.services.run_service import (
    RunServiceError,
    RunUnexpectedError,
    ejecutar_run,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["runs"])


@router.post("/runs", response_model=RunResponse)
def post_runs(
    body: RunRequest | None = None,
    settings: Settings = Depends(settings_dep),
) -> RunResponse:
    """
    POST /runs

    Dispara el pipeline ETL (CSV → SQLite + resumen_diario).
    Body opcional: {"fuente": "movimientos_2026-08.csv", "export_resumen": true}

    Errores:
    - 400: CSV ausente o PipelineError (datos inválidos)
    - 500: fallo inesperado del pipeline
    """
    try:
        return ejecutar_run(settings, body)
    except RunServiceError as exc:
        logger.warning("POST /runs → 400: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RunUnexpectedError as exc:
        logger.error("POST /runs → 500: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc
