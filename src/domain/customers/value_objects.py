from dataclasses import dataclass


@dataclass(frozen=True)
class CustomerName:
    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("El nombre del cliente no puede estar vacío.")


@dataclass(frozen=True)
class CustomerEmail:
    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("El email del cliente no puede estar vacío.")
