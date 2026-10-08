# Template Solventa Backend Service

Microservicio base en Python con FastAPI, Clean Architecture y DDD.

## Requisitos

- Python 3.11+
- Poetry

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --reload
```

## Endpoints principales

- `GET /health`
- `GET /greetings/`
- `POST /greetings/`

## Estructura

- `src/core`: configuración, base de datos y telemetry
- `src/domain`: entidades y reglas del negocio
- `src/application/use_cases`: casos de uso
- `src/infrastructure`: adaptadores externos
- `src/presentation`: routers y dependencias
