from app.repositories.note_repository import NoteRepository
from app.schemas.note_schemas import NoteCreate


class CreateNoteUseCase:

    def __init__(self, repository: NoteRepository):
        self.repository = repository

    async def execute(self, data: NoteCreate):
        return await self.repository.create(data)