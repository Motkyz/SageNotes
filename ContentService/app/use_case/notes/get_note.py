from app.repositories.note_repository import NoteRepository
from app.services.S3_service import s3_service

class GetNoteUseCase:

    def __init__(self, repository: NoteRepository):
        self.repository = repository

    async def execute(self, note_id: str):
        note = await self.repository.get(note_id)

        if not note:
            return None

        for file in note.files:
            file.url = await s3_service.generate_presigned_url(file.key)

        return note