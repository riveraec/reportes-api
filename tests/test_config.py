"""Smoke / checks de settings (paso 2)."""

from pathlib import Path

from reportes_api.config import ROOT_DIR, get_settings


def test_root_dir_es_repo():
    assert (ROOT_DIR / "pyproject.toml").is_file()


def test_defaults_apuntan_a_etl_hermano():
    settings = get_settings()
    assert settings.db_path.name == "reportes.db"
    assert "etl-reportes" in settings.db_path.parts
    assert settings.raw_dir.name == "raw"
    assert isinstance(settings.db_path, Path)
