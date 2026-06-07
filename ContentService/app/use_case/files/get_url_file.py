from app.repositories.file_repository import FileRepository
from app.services.S3_service import s3_service


class GetUrlFileUseCase:

    def __init__(self, repository: FileRepository):
        self.repository = repository

    async def execute(self, file_id: str):
        file = await self.repository.get(file_id)
        if not file:
            raise Exception("File not found")

        key = file.key
        url = await s3_service.generate_presigned_url(key)

        return url
