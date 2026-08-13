"""Tests GET /health (paso 4)."""

from fastapi.testclient import TestClient

from reportes_api.main import app

client = TestClient(app)


def test_health_ok():
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] in ("ok", "degraded")
    assert "db_ok" in body
    assert "db_path" in body
    # Con ETL ya corrido en esta máquina suele ser True
    assert isinstance(body["db_ok"], bool)
