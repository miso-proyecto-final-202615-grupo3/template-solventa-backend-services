from dataclasses import dataclass


@dataclass(frozen=True)
class GreetingMessage:
    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("El mensaje no puede estar vacío.")


@dataclass(frozen=True)
class GreetingLanguage:
    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("El idioma no puede estar vacío.")
