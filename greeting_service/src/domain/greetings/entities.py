from dataclasses import dataclass, field
import uuid


@dataclass(frozen=True)
class GreetingId:
    value: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class Greeting:
    id: GreetingId
    message: str
    language: str

    def update_message(self, new_message: str) -> None:
        if not new_message.strip():
            raise ValueError("El mensaje de saludo no puede estar vacío.")
        self.message = new_message
