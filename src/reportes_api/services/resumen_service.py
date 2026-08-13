"""
services/resumen_service.py — consulta de resumen_diario.

Solo lectura (SELECT + filtros). No recalcula SUM/COUNT: el ETL ya
materializó la tabla resumen_diario.
"""

from __future__ import annotations

import logging
import sqlite3
from datetime import date
from pathlib import Path

from reportes_api.schemas import ResumenItem, ResumenResponse

logger = logging.getLogger(__name__)


class ResumenDbError(Exception):
    """Error de dominio: BD ausente o no legible (el router lo traduce a HTTP 404)."""


def listar_resumen(
    db_path: Path,
    *,
    fecha_desde: date | None = None,
    fecha_hasta: date | None = None,
    categoria: str | None = None,
) -> ResumenResponse:
    """Devuelve filas de resumen_diario filtradas (o todas si no hay filtros)."""
    db_path = Path(db_path)
    if not db_path.is_file():
        logger.warning("BD ausente: %s", db_path)
        raise ResumenDbError(f"No existe la base de datos: {db_path}")

    # Armamos WHERE dinámico con placeholders (?) para evitar SQL injection.
    clauses: list[str] = []
    params: list[object] = []

    if fecha_desde is not None:
        clauses.append("fecha >= ?")
        params.append(fecha_desde.isoformat())  # date → "YYYY-MM-DD" (así está en SQLite)
    if fecha_hasta is not None:
        clauses.append("fecha <= ?")
        params.append(fecha_hasta.isoformat())
    if categoria is not None and categoria.strip():
        clauses.append("categoria = ?")
        params.append(categoria.strip())

    sql = (
        "SELECT fecha, categoria, cantidad, monto_total "
        "FROM resumen_diario"
    )
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)
    sql += " ORDER BY fecha, categoria"

    try:
        # Solo lectura: la API de consulta no debe escribir en la BD del ETL.
        with sqlite3.connect(f"file:{db_path}?mode=ro", uri=True) as conn:
            conn.row_factory = sqlite3.Row  # filas como dict: row["fecha"]
            rows = conn.execute(sql, params).fetchall()
    except sqlite3.Error as exc:
        logger.warning("Error SQLite al leer resumen (%s): %s", db_path, exc)
        raise ResumenDbError(f"Error leyendo resumen: {exc}") from exc

    # Mapeo fila SQL → schema Pydantic (lo que verá el cliente JSON).
    items = [
        ResumenItem(
            fecha=date.fromisoformat(row["fecha"]),
            categoria=row["categoria"],
            cantidad=int(row["cantidad"]),
            monto_total=float(row["monto_total"]),
        )
        for row in rows
    ]
    return ResumenResponse(
        items=items,
        total=len(items),
        # Eco de filtros: el cliente ve qué criterios se aplicaron
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        categoria=categoria.strip() if categoria and categoria.strip() else None,
    )
