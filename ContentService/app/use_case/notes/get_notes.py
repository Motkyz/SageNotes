from app.repositories.note_repository import NoteRepository
from app.models import Note
from app.services.S3_service import s3_service


class GetNotesUseCase:

    def __init__(self, repository: NoteRepository):
        self.repository = repository

    async def execute(self) -> list[Note]:
        notes = await self.repository.get_all()
        for note in notes:
            for file in note.files:
                file.url = await s3_service.generate_presigned_url(file.key)
        return notes