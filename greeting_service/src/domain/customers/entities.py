from dataclasses import dataclass, field
import uuid


@dataclass(frozen=True)
class CustomerId:
    value: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class Customer:
    id: CustomerId
    full_name: str
    email: str
