from src.domain.greetings.entities import Greeting, GreetingId


class GreetingService:
    @staticmethod
    def create(message: str, language: str) -> Greeting:
        if not message.strip():
            raise ValueError("El mensaje del saludo no puede estar vacío.")
        if not language.strip():
            raise ValueError("El idioma del saludo no puede estar vacío.")
        return Greeting(id=GreetingId(), message=message.strip(), language=language.strip())
