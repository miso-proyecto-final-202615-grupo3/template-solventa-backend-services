from pydantic import BaseModel

from src.domain.greetings.entities import Greeting, GreetingId
from src.domain.greetings.repositories import GreetingRepository


class CreateGreetingCommand(BaseModel):
    message: str
    language: str


class GreetingResponseDTO(BaseModel):
    id: str
    message: str
    language: str


class GreetingUseCases:
    def __init__(self, repository: GreetingRepository):
        self.repository = repository

    async def create_greeting(self, command: CreateGreetingCommand) -> GreetingResponseDTO:
        greeting = Greeting(
            id=GreetingId(),
            message=command.message.strip(),
            language=command.language.strip(),
        )
        if not greeting.message:
            raise ValueError("El mensaje del saludo no puede estar vacío.")
        if not greeting.language:
            raise ValueError("El idioma del saludo no puede estar vacío.")

        await self.repository.save(greeting)
        return GreetingResponseDTO(
            id=greeting.id.value,
            message=greeting.message,
            language=greeting.language,
        )

    async def get_greetings(self) -> list[GreetingResponseDTO]:
        greetings = await self.repository.list_all()
        return [
            GreetingResponseDTO(
                id=greeting.id.value,
                message=greeting.message,
                language=greeting.language,
            )
            for greeting in greetings
        ]
