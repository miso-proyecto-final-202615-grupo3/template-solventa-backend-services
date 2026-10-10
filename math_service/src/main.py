from fastapi import FastAPI

from src.core.config import settings
from src.core.telemetry import setup_telemetry
from src.presentation.routers import addition, health

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

setup_telemetry(app)
app.include_router(addition.router)
app.include_router(health.router)