from __future__ import annotations
from typing import Generic, Type, TypeVar
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


ModelT = TypeVar("ModelT")
CreateSchemaT = TypeVar("CreateSchemaT", bound=BaseModel)
UpdateSchemaT = TypeVar("UpdateSchemaT", bound=BaseModel)


class BaseRepository(Generic[ModelT, CreateSchemaT, UpdateSchemaT]):

    model_cls: Type[ModelT]

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory

    def _session(self) -> AsyncSession:
        return self.session_factory()

    async def create(self, data: CreateSchemaT) -> ModelT:
        async with self._session() as session:
            try:
                obj = self.model_cls(**data.model_dump())
                session.add(obj)
                await session.commit()
                await session.refresh(obj)
                return obj
            except Exception:
                await session.rollback()
                raise

    async def get(self, item_id: str) -> ModelT | None:
        async with self._session() as session:
            return await session.get(self.model_cls, UUID(item_id))

    async def get_all(self) -> list[ModelT]:
        async with self._session() as session:
            result = await session.execute(
                select(self.model_cls)
            )
            return list(result.scalars().all())

    async def update(self, item_id: str, data: UpdateSchemaT) -> ModelT | None:
        async with self._session() as session:
            obj = await session.get(self.model_cls, UUID(item_id))
            if not obj:
                return None
            for field, value in data.model_dump(exclude_unset=True).items():
                setattr(obj, field, value)
            await session.commit()
            await session.refresh(obj)
            return obj

    async def delete(self, item_id: str) -> bool:
        async with self._session() as session:
            obj = await session.get(self.model_cls, UUID(item_id))
            if not obj:
                return False
            await session.delete(obj)
            await session.commit()
            return True