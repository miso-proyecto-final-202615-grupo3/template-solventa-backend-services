from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import SessionLocal
from src.infrastructure.persistence.greeting_repository_impl import SqlAlchemyGreetingRepository
from src.application.use_cases.greetings_use_case import GreetingUseCases


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


async def get_greeting_use_cases(
    db: AsyncSession = Depends(get_db),
) -> GreetingUseCases:
    repository = SqlAlchemyGreetingRepository(db)
    return GreetingUseCases(repository)
