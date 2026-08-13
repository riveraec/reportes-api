"""
config.py — configuración de la API: rutas a la BD y al raw del ETL.

Aquí solo hay settings (rutas), no lógica de negocio ni I/O de reportes.

Variables de entorno (opcionales), prefijo REPORTES_API_:
  REPORTES_API_DB_PATH=...\\etl-reportes\\data\\processed\\reportes.db
  REPORTES_API_RAW_DIR=...\\etl-reportes\\data\\raw
"""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Path(__file__) = este archivo (…/src/reportes_api/config.py)
# parents[0] = reportes_api/
# parents[1] = src/
# parents[2] = raíz del repo reportes-api/
ROOT_DIR = Path(__file__).resolve().parents[2]

# Carpeta hermana en el disco: …/python/etl-reportes/
_ETL_ROOT = ROOT_DIR.parent / "etl-reportes"
_DEFAULT_DB_PATH = _ETL_ROOT / "data" / "processed" / "reportes.db"
_DEFAULT_RAW_DIR = _ETL_ROOT / "data" / "raw"


class Settings(BaseSettings):
    """
    Settings = objeto de configuración tipado.

    BaseSettings (pydantic-settings) lee automáticamente:
    1) variables de entorno con prefijo REPORTES_API_
    2) archivo .env en la raíz del proyecto (si existe)
    Si no hay nada de eso, usa los defaults de abajo.
    """

    model_config = SettingsConfigDict(
        env_prefix="REPORTES_API_",  # db_path ← REPORTES_API_DB_PATH
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # ignora claves desconocidas en .env
    )

    # Ruta al SQLite que escribe el ETL (tabla resumen_diario, etc.)
    db_path: Path = Field(default=_DEFAULT_DB_PATH)
    # Carpeta de CSV crudos (la usaremos en POST /runs, paso 7)
    raw_dir: Path = Field(default=_DEFAULT_RAW_DIR)


@lru_cache
def get_settings() -> Settings:
    """
    Devuelve Settings una sola vez (cache).

    @lru_cache evita releer .env en cada request.
    Ojo: si cambias .env, hay que reiniciar Uvicorn.
    """
    return Settings()
