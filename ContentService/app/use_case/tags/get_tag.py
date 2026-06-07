from app.repositories.tag_repository import TagRepository


class GetTagUseCase:
    def __init__(self, repository: TagRepository):
        self.repository = repository

    async def execute(self, tag_id):
        return await self.repository.get(tag_id)