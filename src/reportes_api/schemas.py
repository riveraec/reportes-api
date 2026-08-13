"""
schemas.py — contratos JSON (request/response) con Pydantic.

Validan tipos, serializan respuestas y alimentan el esquema OpenAPI (/docs).
Sin SQL ni llamadas al ETL: solo la forma de los datos.
"""

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Respuesta de GET /health."""

    status: str = Field(examples=["ok"])  # "ok" o "degraded"
    db_ok: Optional[bool] = Field(
        default=None,
        description="True si reportes.db es accesible; None si no se comprobó",
    )
    db_path: Optional[str] = Field(
        default=None,
        description="Ruta configurada a la SQLite del ETL",
    )


class RunRequest(BaseModel):
    """
    Body opcional de POST /runs (paso 7).
    Si el cliente no manda fuente, el service usará el CSV default del raw.
    """

    fuente: Optional[str] = Field(
        default=None,
        description="Nombre o ruta del CSV (relativo a raw_dir o absoluto)",
        examples=["movimientos_2026-08.csv"],
    )
    export_resumen: bool = Field(
        default=True,
        description="Si True, el pipeline exporta resumen_diario.csv",
    )


class RunResponse(BaseModel):
    """
    Resultado de una corrida ETL.
    Los campos coinciden con el dict que devuelve etl_reportes.pipeline.run_pipeline.
    """

    ok: bool = True
    fuente: str
    leidas: int
    aceptadas: int
    rechazadas: int
    escritas: int
    resumen_filas: int
    duracion_seg: float
    mensaje: Optional[str] = None


class ResumenItem(BaseModel):
    """Una fila de la tabla resumen_diario (agregado por fecha + categoría)."""

    fecha: date
    categoria: str
    cantidad: int  # COUNT de movimientos
    monto_total: float  # SUM de montos


class ResumenResponse(BaseModel):
    """
    Envoltorio de GET /resumen.
    `items` = filas; `total` = cuántas; el resto eco de filtros usados.
    """

    items: list[ResumenItem]
    total: int = Field(description="Cantidad de items devueltos")
    fecha_desde: Optional[date] = None
    fecha_hasta: Optional[date] = None
    categoria: Optional[str] = Field(
        default=None,
        description="Filtro de categoría aplicado (si hubo)",
    )
