# reportes-api

API **FastAPI** que **dispara** el pipeline [`etl-reportes`](https://github.com/riveraec/etl-reportes) y **consulta** el resumen diario en SQLite (`resumen_diario`).

Demo de portafolio: capa HTTP sobre un ETL real (no un CRUD suelto). Misma idea de “tablero / cierre” que [`indicadores-api`](https://github.com/riveraec/indicadores-api) en .NET, aquí en Python + batch.

**Autor:** [Efrain Rivera](https://www.linkedin.com/in/riveraec/) · [Portafolio](https://riveraec.github.io/portafolio/)

---

## Stack

| Pieza | Uso |
|-------|-----|
| Python 3.11+ | Runtime (probado con 3.14) |
| FastAPI + Uvicorn | API HTTP y servidor ASGI |
| Pydantic / pydantic-settings | Contratos y configuración |
| sqlite3 | Lectura de `reportes.db` del ETL |
| etl-reportes | Pipeline E→T→L (dependencia editable) |
| pytest + TestClient | Suite de pruebas |

---

## Endpoints

| Método | Ruta | Qué hace |
|--------|------|----------|
| `GET` | `/health` | Servicio vivo + check de SQLite |
| `GET` | `/resumen` | Lee `resumen_diario` (filtros opcionales) |
| `POST` | `/runs` | Dispara `etl_reportes.pipeline.run_pipeline` |
| — | `/docs` | OpenAPI / Swagger (automático) |

Filtros de resumen (query):

```text
GET /resumen?categoria=pagos
GET /resumen?fecha_desde=2026-08-01&fecha_hasta=2026-08-02
```

Body opcional de corrida:

```json
{ "fuente": "movimientos_2026-08.csv", "export_resumen": true }
```

---

## Arquitectura (vista rápida)

```text
Cliente HTTP
    │
    ▼
reportes-api (FastAPI)
    ├── GET  /health   → ping + SQLite read-only
    ├── GET  /resumen  → SELECT resumen_diario
    └── POST /runs     → run_pipeline(...)  ──►  etl-reportes
                                                      │
                                                      ▼
                                            data/processed/reportes.db
```

- **`/runs`** escribe (orquesta el ETL).  
- **`/resumen`** solo lee la misma BD.  
- La API **no** reimplementa Extract/Transform.

---

## Requisitos

- Python 3.11+  
- Repo hermano **etl-reportes** (clonado al lado o con path configurable)  
- PowerShell (Windows) u otra terminal  

Estructura esperada en desarrollo local:

```text
python/
├── etl-reportes/     ← pipeline + data/raw + reportes.db
└── reportes-api/     ← esta API
```

---

## Instalación (primera vez)

```powershell
cd reportes-api
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
pip install -e "..\etl-reportes"
```

Si PowerShell bloquea `Activate.ps1`:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Comprobar:

```powershell
python -c "from reportes_api.main import app; print(app.title)"
python -c "import etl_reportes; print(etl_reportes.__file__)"
python -c "from reportes_api.config import get_settings; s=get_settings(); print(s.db_path, s.db_path.exists())"
```

`db_path.exists()` debería ser `True` si ya corriste el ETL al menos una vez:

```powershell
cd ..\etl-reportes
.\.venv\Scripts\Activate.ps1
python -m etl_reportes run
```

---

## Configuración (opcional)

Por defecto la API apunta al hermano:

- DB: `../etl-reportes/data/processed/reportes.db`  
- Raw: `../etl-reportes/data/raw`  

Para sobrescribir, copia `.env.example` → `.env`:

```text
REPORTES_API_DB_PATH=C:\ruta\a\reportes.db
REPORTES_API_RAW_DIR=C:\ruta\a\data\raw
```

---

## Arrancar la API

Con el venv de **reportes-api** activo:

```powershell
uvicorn reportes_api.main:app --reload
```

| Recurso | URL |
|---------|-----|
| Docs (Swagger) | http://127.0.0.1:8000/docs |
| Health | http://127.0.0.1:8000/health |
| Resumen | http://127.0.0.1:8000/resumen |
| Corrida | `POST` http://127.0.0.1:8000/runs |

### Ejemplos con curl

```powershell
curl.exe http://127.0.0.1:8000/health
curl.exe http://127.0.0.1:8000/resumen
curl.exe "http://127.0.0.1:8000/resumen?categoria=pagos"
curl.exe -X POST http://127.0.0.1:8000/runs
curl.exe -X POST http://127.0.0.1:8000/runs `
  -H "Content-Type: application/json" `
  -d "{\"fuente\":\"movimientos_2026-08.csv\"}"
```

En `/docs` puedes probar los tres endpoints desde el navegador (Try it out).

---

## Tests

```powershell
pytest
```

Cobertura: smoke, config, schemas, health, resumen, runs (mock + integración) y errores HTTP (400 / 404 / 500).

---

## Errores HTTP (resumen)

| Código | Cuándo |
|--------|--------|
| 400 | CSV ausente o `PipelineError` (datos inválidos) |
| 404 | No existe / no se puede leer `reportes.db` en `/resumen` |
| 500 | Fallo inesperado del pipeline |

---

## Estructura del repo

```text
reportes-api/
├── pyproject.toml
├── .env.example
├── src/reportes_api/
│   ├── main.py
│   ├── config.py
│   ├── logging_config.py
│   ├── schemas.py
│   ├── deps.py
│   ├── routers/          # health, resumen, runs
│   └── services/         # resumen_service, run_service
└── tests/
```

---

## Proyectos relacionados

| Repo | Rol |
|------|-----|
| [etl-reportes](https://github.com/riveraec/etl-reportes) | Pipeline CSV → SQLite (esta API lo orquesta) |
| [indicadores-api](https://github.com/riveraec/indicadores-api) | API de métricas / resumen en .NET |
| [Portafolio](https://riveraec.github.io/portafolio/) | Demos publicados |

---

## Licencia

MIT (al publicar el repo en GitHub).
