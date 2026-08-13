"""Smoke: el paquete se importa tras pip install -e ."""

import reportes_api
from reportes_api.main import app


def test_import_paquete():
    assert reportes_api.__file__ is not None


def test_app_title():
    assert app.title == "reportes-api"
