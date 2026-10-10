from fastapi import APIRouter
from pydantic import BaseModel

from src.core.config import settings


class HealthResponse(BaseModel):
    status: str
    version: str


router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return HealthResponse(status="healthy", version=settings.VERSION)
