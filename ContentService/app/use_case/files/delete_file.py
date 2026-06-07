from app.repositories.file_repository import FileRepository
from app.services.S3_service import s3_service


class DeleteFileUseCase:

    def __init__(self, repository: FileRepository):
        self.repository = repository

    async def execute(self, file_id: str):
        file = await self.repository.get(file_id)
        if not file:
            raise Exception("File not found")

        key = file.key
        delete_from_s3 = await s3_service.delete_file(key)

        if delete_from_s3:
            return await self.repository.delete(file_id)
        raise Exception("File not delete in S3")
