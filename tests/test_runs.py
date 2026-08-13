"""Tests POST /runs (paso 7)."""

from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from reportes_api.config import Settings
from reportes_api.deps import settings_dep
from reportes_api.main import app
from reportes_api.schemas import RunRequest
from reportes_api.services.run_service import RunServiceError, ejecutar_run


@pytest.fixture
def settings_tmp(tmp_path: Path) -> Settings:
    raw = tmp_path / "raw"
    raw.mkdir()
    csv = raw / "movimientos_2026-08.csv"
    csv.write_text(
        "fecha,sucursal,categoria,monto,moneda\n"
        "2026-08-01,CDMX-01,pagos,100.0,MXN\n",
        encoding="utf-8",
    )
    return Settings(db_path=tmp_path / "reportes.db", raw_dir=raw)


def test_ejecutar_run_mock(settings_tmp: Settings):
    fake = {
        "fuente": "movimientos_2026-08.csv",
        "leidas": 1,
        "aceptadas": 1,
        "rechazadas": 0,
        "escritas": 1,
        "resumen_filas": 1,
        "duracion_seg": 0.01,
    }
    with patch(
        "reportes_api.services.run_service.run_pipeline",
        return_value=fake,
    ) as mocked:
        resp = ejecutar_run(settings_tmp, RunRequest())
        assert resp.ok is True
        assert resp.escritas == 1
        mocked.assert_called_once()
        args, kwargs = mocked.call_args
        assert kwargs["db_path"] == settings_tmp.db_path
        assert kwargs["export_resumen"] is True


def test_ejecutar_run_csv_ausente(tmp_path: Path):
    settings = Settings(db_path=tmp_path / "x.db", raw_dir=tmp_path / "raw")
    settings.raw_dir.mkdir()
    with pytest.raises(RunServiceError, match="No se encontró CSV"):
        ejecutar_run(settings, RunRequest())


def test_post_runs_http(settings_tmp: Settings):
    app.dependency_overrides[settings_dep] = lambda: settings_tmp
    fake = {
        "fuente": "movimientos_2026-08.csv",
        "leidas": 1,
        "aceptadas": 1,
        "rechazadas": 0,
        "escritas": 1,
        "resumen_filas": 1,
        "duracion_seg": 0.02,
    }
    try:
        with patch(
            "reportes_api.services.run_service.run_pipeline",
            return_value=fake,
        ):
            client = TestClient(app)
            r = client.post("/runs", json={})
            assert r.status_code == 200
            body = r.json()
            assert body["ok"] is True
            assert body["fuente"] == "movimientos_2026-08.csv"
            assert body["mensaje"] == "Pipeline OK"
    finally:
        app.dependency_overrides.clear()


def test_post_runs_real_pipeline(settings_tmp: Settings):
    """Integración ligera: pipeline real sobre CSV/DB temporales."""
    app.dependency_overrides[settings_dep] = lambda: settings_tmp
    try:
        client = TestClient(app)
        r = client.post("/runs")
        assert r.status_code == 200
        body = r.json()
        assert body["escritas"] >= 1
        assert settings_tmp.db_path.is_file()

        resumen = client.get("/resumen")
        assert resumen.status_code == 200
        assert resumen.json()["total"] >= 1
    finally:
        app.dependency_overrides.clear()
