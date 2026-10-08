from typing import List

from fastapi import APIRouter, Depends, status

from src.application.use_cases.customer_use_case import (
    CreateCustomerCommand,
    CustomerResponseDTO,
    CustomerUseCases,
)

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.post(
    "/",
    response_model=CustomerResponseDTO,
    status_code=status.HTTP_201_CREATED,
)
async def create_customer(
    command: CreateCustomerCommand,
    use_cases: CustomerUseCases = Depends(lambda: None),
) -> CustomerResponseDTO:
    raise NotImplementedError("Customer repository dependency has not been wired yet.")


@router.get("/", response_model=List[CustomerResponseDTO])
async def list_customers() -> List[CustomerResponseDTO]:
    raise NotImplementedError("Customer repository dependency has not been wired yet.")
