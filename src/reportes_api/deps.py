"""
deps.py — dependencias inyectables (FastAPI Depends).

En un endpoint:

  settings: Settings = Depends(settings_dep)

FastAPI llama a settings_dep() al atender el request.

En tests se puede sustituir con:
  app.dependency_overrides[settings_dep] = lambda: Settings(db_path=...)
"""

from reportes_api.config import Settings, get_settings


def settings_dep() -> Settings:
    """Proveedor de Settings para los endpoints."""
    return get_settings()
