from src.application.use_cases.add_numbers_use_case import AddNumbersUseCase


def get_add_numbers_use_case() -> AddNumbersUseCase:
    return AddNumbersUseCase()