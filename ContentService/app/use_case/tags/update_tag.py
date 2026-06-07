from app.repositories.tag_repository import TagRepository
from app.schemas.tag_schemas import TagUpdate


class UpdateTagUseCase:
    def __init__(self, repository: TagRepository):
        self.repository = repository

    async def execute(self, tag_id: str, data: TagUpdate):
        return await self.repository.update(tag_id, data)