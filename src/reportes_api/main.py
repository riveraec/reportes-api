"""
main.py — punto de entrada de la aplicación FastAPI.

Uvicorn carga este módulo y busca el objeto `app`:
  uvicorn reportes_api.main:app --reload
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from reportes_api.logging_config import configure_logging
from reportes_api.routers import health, resumen, runs

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Arranque: configura logging. Apagado: nada especial en v1."""
    configure_logging()
    logger.info("reportes-api arrancada")
    yield
    logger.info("reportes-api detenida")


app = FastAPI(
    title="reportes-api",
    version="0.1.0",
    description="API fina sobre etl-reportes: disparar corridas y consultar resumen diario.",
    lifespan=lifespan,
)

app.include_router(health.router)
app.include_router(resumen.router)
app.include_router(runs.router)
