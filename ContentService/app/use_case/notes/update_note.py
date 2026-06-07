from app.repositories.note_repository import NoteRepository
from app.schemas.note_schemas import NoteUpdate


class UpdateNoteUseCase:
    def __init__(self, repository: NoteRepository):
        self.repository = repository

    async def execute(self, note_id: str, data: NoteUpdate):
        return await self.repository.update(note_id, data)