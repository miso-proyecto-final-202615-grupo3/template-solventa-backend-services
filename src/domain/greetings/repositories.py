from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.greetings.entities import Greeting, GreetingId


class GreetingRepository(ABC):
    @abstractmethod
    async def save(self, greeting: Greeting) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, greeting_id: GreetingId) -> Optional[Greeting]:
        raise NotImplementedError

    @abstractmethod
    async def list_all(self) -> List[Greeting]:
        raise NotImplementedError
