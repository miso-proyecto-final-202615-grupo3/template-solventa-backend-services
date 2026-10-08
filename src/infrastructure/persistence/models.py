from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class GreetingModel(Base):
    __tablename__ = "greetings"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    message: Mapped[str] = mapped_column(String, nullable=False)
    language: Mapped[str] = mapped_column(String, nullable=False)


class CustomerModel(Base):
    __tablename__ = "customers"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
