"""Tests de errores HTTP y logging (paso 8)."""

from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from reportes_api.config import Settings
from reportes_api.deps import settings_dep
from reportes_api.main import app


def test_resumen_404_bd_ausente(tmp_path: Path):
    missing = tmp_path / "no.db"
    app.dependency_overrides[settings_dep] = lambda: Settings(
        db_path=missing,
        raw_dir=tmp_path,
    )
    try:
        client = TestClient(app)
        r = client.get("/resumen")
        assert r.status_code == 404
        assert "No existe" in r.json()["detail"]
    finally:
        app.dependency_overrides.clear()


def test_runs_400_sin_csv(tmp_path: Path):
    raw = tmp_path / "raw"
    raw.mkdir()
    app.dependency_overrides[settings_dep] = lambda: Settings(
        db_path=tmp_path / "x.db",
        raw_dir=raw,
    )
    try:
        client = TestClient(app)
        r = client.post("/runs")
        assert r.status_code == 400
        assert "CSV" in r.json()["detail"] or "csv" in r.json()["detail"].lower()
    finally:
        app.dependency_overrides.clear()


def test_runs_500_fallo_inesperado(tmp_path: Path):
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "movimientos_2026-08.csv").write_text(
        "fecha,sucursal,categoria,monto,moneda\n2026-08-01,CDMX-01,pagos,1,MXN\n",
        encoding="utf-8",
    )
    app.dependency_overrides[settings_dep] = lambda: Settings(
        db_path=tmp_path / "reportes.db",
        raw_dir=raw,
    )
    try:
        with patch(
            "reportes_api.services.run_service.run_pipeline",
            side_effect=RuntimeError("boom"),
        ):
            client = TestClient(app)
            r = client.post("/runs")
            assert r.status_code == 500
            assert "interno" in r.json()["detail"].lower()
    finally:
        app.dependency_overrides.clear()
