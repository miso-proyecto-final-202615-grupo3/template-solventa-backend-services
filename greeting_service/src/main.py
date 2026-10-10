from fastapi import FastAPI

from src.core.config import settings
from src.core.database import Base, engine
from src.core.telemetry import setup_telemetry
from src.infrastructure.persistence import models  # noqa: F401
from src.presentation.routers import greetings, health

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

setup_telemetry(app)

app.include_router(health.router)
app.include_router(greetings.router)


@app.on_event("startup")
async def create_database_schema() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Welcome to the Clean Architecture FastAPI Microservice"}
