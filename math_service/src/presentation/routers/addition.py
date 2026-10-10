from fastapi import APIRouter, Depends

from src.application.use_cases.add_numbers_use_case import (
    AddNumbersCommand,
    AddNumbersResponse,
    AddNumbersUseCase,
)
from src.presentation.dependencies import get_add_numbers_use_case

router = APIRouter(tags=["Math"])


@router.post("/add", response_model=AddNumbersResponse)
async def add(
    command: AddNumbersCommand,
    use_case: AddNumbersUseCase = Depends(get_add_numbers_use_case),
) -> AddNumbersResponse:
    return use_case.execute(command)