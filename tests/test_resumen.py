"""Tests GET /resumen (paso 5)."""

import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from reportes_api.config import Settings
from reportes_api.deps import settings_dep
from reportes_api.main import app
from reportes_api.services.resumen_service import listar_resumen


@pytest.fixture
def db_seed(tmp_path: Path) -> Path:
    db = tmp_path / "reportes.db"
    with sqlite3.connect(db) as conn:
        conn.execute(
            """
            CREATE TABLE resumen_diario (
                fecha TEXT NOT NULL,
                categoria TEXT NOT NULL,
                cantidad INTEGER NOT NULL,
                monto_total REAL NOT NULL,
                PRIMARY KEY (fecha, categoria)
            )
            """
        )
        conn.executemany(
            "INSERT INTO resumen_diario VALUES (?, ?, ?, ?)",
            [
                ("2026-08-01", "pagos", 2, 100.0),
                ("2026-08-01", "retiros", 1, 50.0),
                ("2026-08-02", "pagos", 3, 200.5),
            ],
        )
        conn.commit()
    return db


def test_listar_resumen_filtro_categoria(db_seed: Path):
    resp = listar_resumen(db_seed, categoria="pagos")
    assert resp.total == 2
    assert all(i.categoria == "pagos" for i in resp.items)


def test_listar_resumen_rango_fechas(db_seed: Path):
    from datetime import date

    resp = listar_resumen(
        db_seed,
        fecha_desde=date(2026, 8, 2),
        fecha_hasta=date(2026, 8, 2),
    )
    assert resp.total == 1
    assert resp.items[0].monto_total == 200.5


def test_get_resumen_http(db_seed: Path):
    app.dependency_overrides[settings_dep] = lambda: Settings(
        db_path=db_seed,
        raw_dir=db_seed.parent,
    )
    try:
        client = TestClient(app)
        r = client.get("/resumen", params={"categoria": "retiros"})
        assert r.status_code == 200
        body = r.json()
        assert body["total"] == 1
        assert body["items"][0]["categoria"] == "retiros"
        assert body["categoria"] == "retiros"
    finally:
        app.dependency_overrides.clear()


def test_get_resumen_db_ausente(tmp_path: Path):
    missing = tmp_path / "no-existe.db"
    app.dependency_overrides[settings_dep] = lambda: Settings(
        db_path=missing,
        raw_dir=tmp_path,
    )
    try:
        client = TestClient(app)
        r = client.get("/resumen")
        assert r.status_code == 404
    finally:
        app.dependency_overrides.clear()
