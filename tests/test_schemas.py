"""Smoke de schemas (paso 3)."""

from datetime import date

from reportes_api.schemas import (
    HealthResponse,
    ResumenItem,
    ResumenResponse,
    RunRequest,
    RunResponse,
)


def test_health_response():
    h = HealthResponse(status="ok", db_ok=True, db_path="/tmp/reportes.db")
    assert h.status == "ok"
    assert h.db_ok is True


def test_run_request_defaults():
    r = RunRequest()
    assert r.fuente is None
    assert r.export_resumen is True


def test_run_response_desde_pipeline_shape():
    resp = RunResponse(
        fuente="movimientos_2026-08.csv",
        leidas=25,
        aceptadas=20,
        rechazadas=5,
        escritas=20,
        resumen_filas=17,
        duracion_seg=0.037,
    )
    assert resp.ok is True
    assert resp.escritas == 20


def test_resumen_response():
    item = ResumenItem(
        fecha=date(2026, 8, 1),
        categoria="pagos",
        cantidad=3,
        monto_total=1500.5,
    )
    body = ResumenResponse(items=[item], total=1)
    assert body.total == 1
    assert body.items[0].categoria == "pagos"
