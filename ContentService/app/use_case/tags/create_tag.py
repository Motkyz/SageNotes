from app.repositories.tag_repository import TagRepository
from app.schemas.tag_schemas import TagCreate


class CreateTagUseCase:
    def __init__(self, repository: TagRepository):
        self.repository = repository

    async def execute(self, data: TagCreate):
        return await self.repository.create(data)