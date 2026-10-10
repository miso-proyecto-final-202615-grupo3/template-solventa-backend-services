from src.application.use_cases.add_numbers_use_case import (
    AddNumbersCommand,
    AddNumbersUseCase,
)


def test_add_numbers():
    use_case = AddNumbersUseCase()
    command = AddNumbersCommand(first_number=2, second_number=3)

    response = use_case.execute(command)

    assert response.result == 5