import pytest

from src.application.use_cases.greetings_use_case import (
    CreateGreetingCommand,
    GreetingUseCases,
)
from src.domain.greetings.entities import Greeting
from src.domain.greetings.repositories import GreetingRepository


class InMemoryGreetingRepository(GreetingRepository):
    def __init__(self):
        self.storage = {}

    async def save(self, greeting: Greeting) -> None:
        self.storage[greeting.id.value] = greeting

    async def get_by_id(self, greeting_id):
        return self.storage.get(greeting_id.value)

    async def list_all(self):
        return list(self.storage.values())


@pytest.mark.asyncio
async def test_create_greeting():
    repo = InMemoryGreetingRepository()
    use_cases = GreetingUseCases(repo)

    command = CreateGreetingCommand(message="Hola Mundo", language="es")
    response = await use_cases.create_greeting(command)

    assert response.message == "Hola Mundo"
    assert response.language == "es"

    all_greetings = await use_cases.get_greetings()
    assert len(all_greetings) == 1
