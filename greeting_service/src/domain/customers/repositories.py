from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.customers.entities import Customer, CustomerId


class CustomerRepository(ABC):
    @abstractmethod
    async def save(self, customer: Customer) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, customer_id: CustomerId) -> Optional[Customer]:
        raise NotImplementedError

    @abstractmethod
    async def list_all(self) -> List[Customer]:
        raise NotImplementedError
