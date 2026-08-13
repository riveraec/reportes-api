"""
routers/resumen.py — endpoint GET /resumen.

Recibe query params y delega la consulta a services/resumen_service.py.
"""

from __future__ import annotations

import logging
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query

from reportes_api.config import Settings
from reportes_api.deps import settings_dep
from reportes_api.schemas import ResumenResponse
from reportes_api.services.resumen_service import ResumenDbError, listar_resumen

logger = logging.getLogger(__name__)

router = APIRouter(tags=["resumen"])


@router.get("/resumen", response_model=ResumenResponse)
def get_resumen(
    fecha_desde: date | None = Query(default=None),
    fecha_hasta: date | None = Query(default=None),
    categoria: str | None = Query(default=None),
    settings: Settings = Depends(settings_dep),
) -> ResumenResponse:
    """
    GET /resumen

    Lee la tabla resumen_diario que YA calculó el ETL.
    Si falta la BD → 404.
    """
    try:
        resp = listar_resumen(
            settings.db_path,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            categoria=categoria,
        )
        logger.info(
            "GET /resumen OK: total=%s filtros fecha_desde=%s fecha_hasta=%s categoria=%s",
            resp.total,
            fecha_desde,
            fecha_hasta,
            categoria,
        )
        return resp
    except ResumenDbError as exc:
        logger.warning("GET /resumen → 404 (BD): %s", exc)
        raise HTTPException(status_code=404, detail=str(exc)) from exc
