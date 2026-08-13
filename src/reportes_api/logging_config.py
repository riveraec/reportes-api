"""
logging_config.py — configuración de logging al arrancar la API.

Formato con hora, nivel y módulo. Se llama una vez en el lifespan de main.
"""

from __future__ import annotations

import logging


def configure_logging(verbose: bool = False) -> None:
    """Configura el logging raíz de la aplicación."""
    level = logging.DEBUG if verbose else logging.INFO
    root = logging.getLogger()
    if root.handlers:
        for handler in root.handlers[:]:
            root.removeHandler(handler)

    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        datefmt="%H:%M:%S",
    )
    logging.getLogger("reportes_api").setLevel(level)
