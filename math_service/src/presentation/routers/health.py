import logging

from fastapi import APIRouter, Response, status
from pydantic import BaseModel

from src.core.config import settings

logger = logging.getLogger(__name__)


class HealthResponse(BaseModel):
    status: str
    version: str


router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check(response: Response) -> HealthResponse:
    try:
        return HealthResponse(status="healthy", version=settings.VERSION)
    except Exception as exc:
        logger.exception("Math service health check failed: %s", exc)
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return HealthResponse(status="unhealthy", version="unknown")
