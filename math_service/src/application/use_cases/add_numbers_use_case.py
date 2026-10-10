from pydantic import BaseModel

from src.domain.addition.services import add_numbers


class AddNumbersCommand(BaseModel):
    first_number: float
    second_number: float


class AddNumbersResponse(BaseModel):
    result: float


class AddNumbersUseCase:
    def execute(self, command: AddNumbersCommand) -> AddNumbersResponse:
        return AddNumbersResponse(
            result=add_numbers(command.first_number, command.second_number)
        )