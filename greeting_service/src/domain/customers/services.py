from src.domain.customers.entities import Customer, CustomerId


class CustomerService:
    @staticmethod
    def create(full_name: str, email: str) -> Customer:
        if not full_name.strip():
            raise ValueError("El nombre completo no puede estar vacío.")
        if not email.strip():
            raise ValueError("El email no puede estar vacío.")
        return Customer(id=CustomerId(), full_name=full_name.strip(), email=email.strip())
