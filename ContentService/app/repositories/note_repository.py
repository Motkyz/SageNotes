from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models import Note, Tag
from app.repositories.base_repository import BaseRepository
from app.schemas.note_schemas import NoteCreate, NoteUpdate


class NoteRepository(BaseRepository[Note, NoteCreate, NoteUpdate]):
    model_cls = Note

    async def create(self, data: NoteCreate) -> str:
        async with self._session() as session:
            note = self.model_cls(title=data.title, content=data.content)

            session.add(note)

            if data.tags:
                tags = await session.execute(select(Tag).where(Tag.id.in_(data.tags)))
                tags_list = list(tags.scalars().all())
                note.tags = tags_list

            # TODO нужно еще файлы сохранять

            await session.commit()
            return str(note.id)

    async def update(self, item_id: str, data: NoteUpdate) -> str | None:
        async with self._session() as session:
            note = await session.get(self.model_cls, UUID(item_id))
            if not note:
                return None

            if data.title is not None:
                note.title = data.title
            if data.content is not None:
                note.content = data.content
            if data.tags is not None:
                tags = await session.execute(select(Tag).where(Tag.id.in_(data.tags)))
                note.tags = list(tags.scalars().all())

            # TODO файлы

            await session.commit()

            return str(note.id)

    async def get(self, item_id: str) -> Note | None:
        async with self._session() as session:
            result = await session.execute(
                select(self.model_cls)
                .where(self.model_cls.id == UUID(item_id))
                .options(selectinload(self.model_cls.tags))
            )

            return result.scalar_one_or_none()

    async def get_all(self) -> list[Note]:
        async with self._session() as session:
            result = await session.execute(
                select(self.model_cls)
                .options(selectinload(self.model_cls.tags))
                .order_by(self.model_cls.created_at.desc())
            )

            return list(result.scalars().all())