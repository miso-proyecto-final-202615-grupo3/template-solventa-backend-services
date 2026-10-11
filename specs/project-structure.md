# Especificación Técnica del Microservicio: FastAPI Clean Architecture & DDD

## 1. Visión General del Proyecto y Stack Tecnológico

Este microservicio sigue los principios de Clean Architecture y Domain-Driven Design (DDD) con una organización basada en Domain Slices. Utiliza las últimas versiones estables del ecosistema Python.

Stack Tecnológico (Últimas versiones)

* Framework Web: FastAPI (>= 0.115+)
* Validación y Configuración: Pydantic v2 & Pydantic-Settings
* Base de Datos / ORM: SQLAlchemy 2.0+ (con soporte asíncrono asyncpg)
* Pruebas Unitarias e Integración: Pytest, Pytest-Asyncio, Httpx
* Telemetría y Observabilidad: OpenTelemetry SDK, Prometheus (vía prometheus-fastapi-instrumentator)

## 2. Estructura de Directorios del Proyecto

La estructura del proyecto desacopla estrictamente los componentes externos de las reglas de negocio puras.

```txt
microservice/
├── greeting_service/
│   ├── requirements.txt
│   ├── src/
│   │   ├── presentation/
│   │   ├── application/
│   │   ├── domain/
│   │   ├── infrastructure/
│   │   ├── core/
│   │   └── main.py
│   └── tests/
│       ├── unit/
│       ├── integration/
│       └── conftest.py
├── math_service/
│   ├── requirements.txt
│   ├── src/
│   │   ├── presentation/
│   │   ├── application/
│   │   ├── domain/
│   │   ├── infrastructure/
│   │   ├── core/
│   │   └── main.py
│   └── tests/
│       ├── unit/
│       └── integration/
├── docker/
│   ├── services/
│   │   ├── Dockerfile.greeting_service  # Imagen de Greeting Service
│   │   └── Dockerfile.math_service      # Imagen de Math Service
├── docker-compose.yml                   # Docker Compose para ejecución en local
└── README.md
```

## 3. Implementación de Componentes Clave

### 3.1. Core (greeting_service/src/core/)

Configuración (config.py)

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
  PROJECT_NAME: str = "FastAPI Clean DDD Service"
  VERSION: str = "1.0.0"
  ENVIRONMENT: str = "dev"
  DATABASE_URL: str = (
      "postgresql+asyncpg://postgres:postgres@localhost:5432/db"
  )
  OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://localhost:4317"

  model_config = SettingsConfigDict(
      env_file=".env", env_file_encoding="utf-8", extra="ignore"
  )


settings = Settings()
```

Telemetría OpenTelemetry y Prometheus (telemetry.py)

```python
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from prometheus_fastapi_instrumentator import Instrumentator
from src.core.config import settings


def setup_telemetry(app: FastAPI) -> None:
  # Configuración de OpenTelemetry Tracing
  resource = Resource.create(attributes={"service.name": settings.PROJECT_NAME})
  provider = TracerProvider(resource=resource)

  otlp_exporter = OTLPSpanExporter(
      endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT, insecure=True
  )
  provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
  trace.set_tracer_provider(provider)

  # Instrumentar FastAPI para trazas
  FastAPIInstrumentor.instrument_app(app)

  # Configurar métricas de Prometheus
  Instrumentator().instrument(app).expose(app, endpoint="/metrics")
```

### 3.2. Domain Layer (greeting_service/src/domain/greetings/)

Entidad y Objeto de Valor (entities.py y value_objects.py)

```python
from dataclasses import dataclass, field
import uuid


@dataclass(frozen=True)
class GreetingId:
  value: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class Greeting:
  id: GreetingId
  message: str
  language: str

  def update_message(self, new_message: str) -> None:
    if not new_message.strip():
      raise ValueError("El mensaje de saludo no puede estar vacío.")
    self.message = new_message
```

Interfaz del Repositorio (repositories.py)

```python
from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.greetings.entities import Greeting, GreetingId


class GreetingRepository(ABC):

  @abstractmethod
  async def save(self, greeting: Greeting) -> None:
    pass

  @abstractmethod
  async def get_by_id(self, greeting_id: GreetingId) -> Optional[Greeting]:
    pass

  @abstractmethod
  async def list_all(self) -> List[Greeting]:
    pass
```

### 3.3. Infrastructure Layer (greeting_service/src/infrastructure/persistence/)

Modelo SQLAlchemy y Repositorio Concreto (greeting_repository_impl.py)

```python
from sqlalchemy import Column, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.core.database import Base
from src.domain.greetings.entities import Greeting, GreetingId
from src.domain.greetings.repositories import GreetingRepository


class GreetingModel(Base):
  __tablename__ = "greetings"

  id = Column(String, primary_key=True, index=True)
  message = Column(String, nullable=False)
  language = Column(String, nullable=False)


class SqlAlchemyGreetingRepository(GreetingRepository):

  def __init__(self, session: AsyncSession):
    self.session = session

  async def save(self, greeting: Greeting) -> None:
    db_obj = await self.session.get(GreetingModel, greeting.id.value)
    if db_obj:
      db_obj.message = greeting.message
      db_obj.language = greeting.language
    else:
      db_obj = GreetingModel(
          id=greeting.id.value,
          message=greeting.message,
          language=greeting.language,
      )
      self.session.add(db_obj)
    await self.session.commit()

  async def get_by_id(self, greeting_id: GreetingId) -> Optional[Greeting]:
    result = await self.session.execute(
        select(GreetingModel).where(GreetingModel.id == greeting_id.value)
    )
    db_obj = result.scalars().first()
    if not db_obj:
      return None
    return Greeting(
        id=GreetingId(value=db_obj.id),
        message=db_obj.message,
        language=db_obj.language,
    )

  async def list_all(self) -> List[Greeting]:
    result = await self.session.execute(select(GreetingModel))
    db_objs = result.scalars().all()
    return [
        Greeting(
            id=GreetingId(value=obj.id),
            message=obj.message,
            language=obj.language,
        )
        for obj in db_objs
    ]
```

### 3.4. Use Cases Layer (greeting_service/src/application/use_cases/greetings_use_case.py)

```python
from pydantic import BaseModel
from src.domain.greetings.entities import Greeting, GreetingId
from src.domain.greetings.repositories import GreetingRepository


class CreateGreetingCommand(BaseModel):
  message: str
  language: str


class GreetingResponseDTO(BaseModel):
  id: str
  message: str
  language: str


class GreetingUseCases:

  def __init__(self, repository: GreetingRepository):
    self.repository = repository

  async def create_greeting(
      self, command: CreateGreetingCommand
  ) -> GreetingResponseDTO:
    greeting = Greeting(
        id=GreetingId(), message=command.message, language=command.language
    )
    await self.repository.save(greeting)
    return GreetingResponseDTO(
        id=greeting.id.value,
        message=greeting.message,
        language=greeting.language,
    )

  async def get_greetings(self) -> list[GreetingResponseDTO]:
    greetings = await self.repository.list_all()
    return [
        GreetingResponseDTO(
            id=g.id.value, message=g.message, language=g.language
        )
        for g in greetings
    ]
```

### 3.5. Presentation Layer (greeting_service/src/presentation/routers/)

Health Check (health.py)

```python
from fastapi import APIRouter, status
from pydantic import BaseModel


class HealthResponse(BaseModel):
  status: str
  version: str


router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
)
async def health_check():
  return HealthResponse(status="healthy", version="1.0.0")
```

Greetings Router (greetings.py)

```python
from fastapi import APIRouter, Depends, status
from typing import List
from src.presentation.dependencies import get_greeting_use_cases
from src.application.use_cases.greetings_usecases import (
    CreateGreetingCommand,
    GreetingResponseDTO,
    GreetingUseCases,
)

router = APIRouter(prefix="/greetings", tags=["Greetings"])


@router.post(
    "/", response_model=GreetingResponseDTO, status_code=status.HTTP_201_CREATED
)
async def create_greeting(
    command: CreateGreetingCommand,
    use_cases: GreetingUseCases = Depends(get_greeting_use_cases),
):
  return await use_cases.create_greeting(command)


@router.get("/", response_model=List[GreetingResponseDTO])
async def list_greetings(
    use_cases: GreetingUseCases = Depends(get_greeting_use_cases),
):
  return await use_cases.get_greetings()
```

### 3.6. Main Application (greeting_service/src/main.py)

```python
from fastapi import FastAPI
from src.core.config import settings
from src.core.telemetry import setup_telemetry
from src.presentation.routers import greetings, health

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configurar Telemetría y Métricas
setup_telemetry(app)

# Incluir Rutas
app.include_router(health.router)
app.include_router(greetings.router)


@app.get("/")
async def root():
  return {"message": "Welcome to the Clean Architecture FastAPI Microservice"}
```

## 4. Estrategia de Pruebas Unitarias (tests/)

Las pruebas se ejecutan utilizando Pytest y Pytest-Asyncio, aislando los casos de uso utilizando mocks o repositorios en memoria para garantizar velocidad y fiabilidad.

Ejemplo de Prueba Unitaria para Casos de Uso (greeting_service/tests/unit/test_greetings.py)

```python
import pytest
from src.domain.greetings.entities import Greeting
from src.domain.greetings.repositories import GreetingRepository
from src.application.use_cases.greetings_usecases import CreateGreetingCommand, GreetingUseCases


class InMemoryGreetingRepository(GreetingRepository):

  def __init__(self):
    self.storage = {}

  async def save(self, greeting: Greeting) -> None:
    self.storage[greeting.id.value] = greeting

  async def get_by_id(self, greeting_id):
    return self.storage.get(greeting_id.value)

  async def list_all(self):
    return list(self.storage.values())


@pytest.mark.asyncio
async def test_create_greeting():
  repo = InMemoryGreetingRepository()
  use_cases = GreetingUseCases(repo)

  command = CreateGreetingCommand(message="Hola Mundo", language="es")
  response = await use_cases.create_greeting(command)

  assert response.message == "Hola Mundo"
  assert response.language == "es"

  all_greetings = await use_cases.get_greetings()
  assert len(all_greetings) == 1
```

## 5. Dependencias del Proyecto (pyproject.toml)

```toml
[tool.poetry]
name = "fastapi-clean-ddd-microservice"
version = "1.0.0"
description = "Microservice using FastAPI, Clean Architecture, DDD, OpenTelemetry and SQLAlchemy"
authors = ["Developer <dev@example.com>"]

[tool.poetry.dependencies]
python = "^3.11"
fastapi = ">=0.115.0"
uvicorn = {extras = ["standard"], version = ">=0.30.0"}
pydantic = ">=2.10.0"
pydantic-settings = ">=2.7.0"
sqlalchemy = ">=2.0.36"
asyncpg = ">=0.30.0"
opentelemetry-api = ">=1.28.0"
opentelemetry-sdk = ">=1.28.0"
opentelemetry-instrumentation-fastapi = ">=0.49b0"
opentelemetry-exporter-otlp = ">=1.28.0"
prometheus-fastapi-instrumentator = ">=7.0.0"

[tool.poetry.group.dev.dependencies]
pytest = ">=8.3.0"
pytest-asyncio = ">=0.24.0"
httpx = ">=0.27.0"
pytest-cov = ">=6.0.0"

[build-system]
requires = ["poetry-core>=2.0.0"]
build-backend = "poetry.core.masonry.api"
```

## 6. Pruebas de Integración y API (greeting_service/tests/integration/)

Las pruebas de integración validan el comportamiento completo del microservicio desde la capa de presentación (endpoints HTTP) hasta la infraestructura, utilizando un cliente HTTP asíncrono (httpx.AsyncClient) y una base de datos real o simulada mediante bases de datos de prueba transaccionales.

Configuración Compartida de Pruebas (tests/conftest.py)

Este archivo configura la aplicación con una base de datos de pruebas (por ejemplo, SQLite en memoria asíncrona o PostgreSQL efímero) y sobrescribe las dependencias de inyección (get_db o el repositorio) para los tests de integración.

```python
from collections.abc import AsyncGenerator
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from src.core.database import Base
from src.main import app
from src.presentation.dependencies import get_db

# Base de datos en memoria para pruebas de integración rápidas
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False, future=True)
TestSessionLocal = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
  async with TestSessionLocal() as session:
    yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
async def setup_database():
  """Crea las tablas antes de cada test y las limpia al terminar."""
  async with test_engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)
  yield
  async with test_engine.begin() as conn:
    await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
  """Cliente HTTP asíncrono para probar los endpoints de FastAPI."""
  async with AsyncClient(
      transport=ASGITransport(app=app), base_url="http://test"
  ) as ac:
    yield ac
```

Implementación de Pruebas de API (greeting_service/tests/integration/test_greetings_api.py)

Este archivo verifica que los endpoints HTTP funcionen de extremo a extremo, validando códigos de estado HTTP, serialización de Pydantic v2 y la persistencia real en la base de datos de prueba.

```python
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(async_client: AsyncClient):
  """Prueba el endpoint de health check."""
  response = await async_client.get("/health")
  assert response.status_code == 200
  data = response.json()
  assert data["status"] == "healthy"
  assert "version" in data


@pytest.mark.asyncio
async def test_create_and_list_greetings_api(async_client: AsyncClient):
  """Prueba el flujo completo de creación y listado de saludos a nivel API."""
  # 1. Crear un saludo vía POST
  payload = {"message": "¡Hola desde integración!", "language": "es"}
  response = await async_client.post("/greetings/", json=payload)

  assert response.status_code == 201
  data = response.json()
  assert data["message"] == payload["message"]
  assert data["language"] == payload["language"]
  assert "id" in data
  greeting_id = data["id"]

  # 2. Listar los saludos vía GET y verificar que aparezca
  response_list = await async_client.get("/greetings/")
  assert response_list.status_code == 200
  greetings = response_list.json()

  assert len(greetings) == 1
  assert greetings[0]["id"] == greeting_id
  assert greetings[0]["message"] == "¡Hola desde integración!"
```
