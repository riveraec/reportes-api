"""
services/run_service.py — dispara el pipeline etl-reportes.

Resuelve el CSV de entrada, llama a run_pipeline y mapea el dict
de resultado a RunResponse. Sin detalles HTTP (eso va en el router).
"""

from __future__ import annotations

import logging
from pathlib import Path

from etl_reportes.pipeline import PipelineError, run_pipeline

from reportes_api.config import Settings
from reportes_api.schemas import RunRequest, RunResponse

logger = logging.getLogger(__name__)


class RunServiceError(Exception):
    """Error controlado de corrida (CSV ausente, PipelineError) → HTTP 4xx."""


class RunUnexpectedError(Exception):
    """Fallo inesperado al ejecutar el pipeline → HTTP 500."""


def _resolve_input_csv(raw_dir: Path, fuente: str | None) -> Path:
    """
    Resuelve la ruta del CSV:
    - fuente absoluta → se usa tal cual
    - fuente relativa / nombre → raw_dir / fuente
    - sin fuente → movimientos_2026-08.csv o el primer *.csv en raw_dir
    """
    raw_dir = Path(raw_dir)

    if fuente:
        path = Path(fuente)
        if not path.is_absolute():
            path = raw_dir / fuente
        return path

    default = raw_dir / "movimientos_2026-08.csv"
    if default.is_file():
        return default

    candidatos = sorted(raw_dir.glob("*.csv"))
    if candidatos:
        return candidatos[0]

    raise RunServiceError(
        f"No se encontró CSV de entrada. Indica 'fuente' o coloca un .csv en {raw_dir}"
    )


def ejecutar_run(settings: Settings, request: RunRequest | None = None) -> RunResponse:
    """Ejecuta E→T→L vía etl_reportes y devuelve RunResponse."""
    request = request or RunRequest()
    input_path = _resolve_input_csv(settings.raw_dir, request.fuente)

    if not input_path.is_file():
        logger.warning("CSV no encontrado: %s", input_path)
        raise RunServiceError(f"No existe el archivo CSV: {input_path}")

    logger.info(
        "Corrida inicio: fuente=%s db=%s export_resumen=%s",
        input_path.name,
        settings.db_path,
        request.export_resumen,
    )

    try:
        summary = run_pipeline(
            input_path,
            db_path=settings.db_path,
            export_resumen=request.export_resumen,
        )
    except FileNotFoundError as exc:
        logger.warning("Pipeline FileNotFoundError: %s", exc)
        raise RunServiceError(str(exc)) from exc
    except PipelineError as exc:
        logger.warning("PipelineError: %s", exc)
        raise RunServiceError(str(exc)) from exc
    except Exception as exc:
        logger.exception("Fallo inesperado en run_pipeline: %s", exc)
        raise RunUnexpectedError(
            f"Error interno al ejecutar el pipeline: {exc}"
        ) from exc

    logger.info(
        "Corrida OK: fuente=%s leidas=%s escritas=%s resumen_filas=%s duracion=%ss",
        summary["fuente"],
        summary["leidas"],
        summary["escritas"],
        summary["resumen_filas"],
        summary["duracion_seg"],
    )

    return RunResponse(
        ok=True,
        fuente=summary["fuente"],
        leidas=summary["leidas"],
        aceptadas=summary["aceptadas"],
        rechazadas=summary["rechazadas"],
        escritas=summary["escritas"],
        resumen_filas=summary["resumen_filas"],
        duracion_seg=summary["duracion_seg"],
        mensaje="Pipeline OK",
    )
