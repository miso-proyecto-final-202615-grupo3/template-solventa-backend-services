from typing import List

from fastapi import APIRouter, Depends, status

from src.application.use_cases.greetings_use_case import (
    CreateGreetingCommand,
    GreetingResponseDTO,
    GreetingUseCases,
)
from src.core.config import settings
from src.presentation.dependencies import get_greeting_use_cases

router = APIRouter(prefix=f"{settings.API_PREFIX}/greetings", tags=["Greetings"])


@router.post(
    "/",
    response_model=GreetingResponseDTO,
    status_code=status.HTTP_201_CREATED,
)
async def create_greeting(
    command: CreateGreetingCommand,
    use_cases: GreetingUseCases = Depends(get_greeting_use_cases),
) -> GreetingResponseDTO:
    return await use_cases.create_greeting(command)


@router.get("/", response_model=List[GreetingResponseDTO])
async def list_greetings(
    use_cases: GreetingUseCases = Depends(get_greeting_use_cases),
) -> List[GreetingResponseDTO]:
    return await use_cases.get_greetings()
