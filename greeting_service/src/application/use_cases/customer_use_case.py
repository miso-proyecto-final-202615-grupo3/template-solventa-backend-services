from pydantic import BaseModel

from src.domain.customers.entities import Customer, CustomerId
from src.domain.customers.repositories import CustomerRepository


class CreateCustomerCommand(BaseModel):
    full_name: str
    email: str


class CustomerResponseDTO(BaseModel):
    id: str
    full_name: str
    email: str


class CustomerUseCases:
    def __init__(self, repository: CustomerRepository):
        self.repository = repository

    async def create_customer(self, command: CreateCustomerCommand) -> CustomerResponseDTO:
        customer = Customer(
            id=CustomerId(),
            full_name=command.full_name.strip(),
            email=command.email.strip(),
        )
        if not customer.full_name:
            raise ValueError("El nombre completo no puede estar vacío.")
        if not customer.email:
            raise ValueError("El email no puede estar vacío.")

        await self.repository.save(customer)
        return CustomerResponseDTO(
            id=customer.id.value,
            full_name=customer.full_name,
            email=customer.email,
        )

    async def get_customers(self) -> list[CustomerResponseDTO]:
        customers = await self.repository.list_all()
        return [
            CustomerResponseDTO(
                id=customer.id.value,
                full_name=customer.full_name,
                email=customer.email,
            )
            for customer in customers
        ]
