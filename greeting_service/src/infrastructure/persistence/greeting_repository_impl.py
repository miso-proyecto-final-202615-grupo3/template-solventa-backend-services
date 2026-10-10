from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.greetings.entities import Greeting, GreetingId
from src.domain.greetings.repositories import GreetingRepository
from src.infrastructure.persistence.models import GreetingModel


class SqlAlchemyGreetingRepository(GreetingRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, greeting: Greeting) -> None:
        existing = await self.session.get(GreetingModel, greeting.id.value)
        if existing:
            existing.message = greeting.message
            existing.language = greeting.language
        else:
            self.session.add(
                GreetingModel(
                    id=greeting.id.value,
                    message=greeting.message,
                    language=greeting.language,
                )
            )
        await self.session.commit()

    async def get_by_id(self, greeting_id: GreetingId) -> Optional[Greeting]:
        result = await self.session.execute(
            select(GreetingModel).where(GreetingModel.id == greeting_id.value)
        )
        db_obj = result.scalars().first()
        if not db_obj:
            return None
        return Greeting(
            id=GreetingId(value=db_obj.id),
            message=db_obj.message,
            language=db_obj.language,
        )

    async def list_all(self) -> List[Greeting]:
        result = await self.session.execute(select(GreetingModel))
        db_objs = result.scalars().all()
        return [
            Greeting(
                id=GreetingId(value=obj.id),
                message=obj.message,
                language=obj.language,
            )
            for obj in db_objs
        ]
