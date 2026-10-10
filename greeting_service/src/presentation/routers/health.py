from fastapi import APIRouter, status
from pydantic import BaseModel
from sqlalchemy import text

from src.core.config import settings
from src.core.database import engine


class HealthResponse(BaseModel):
    status: str
    version: str
    database_status: str


router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
)
async def health_check() -> HealthResponse:
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        database_status = "OK"
        status_value = "healthy"
    except Exception:
        database_status = "Failed"
        status_value = "unhealthy"

    return HealthResponse(
        status=status_value,
        version=settings.VERSION,
        database_status=database_status,
    )
