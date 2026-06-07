from app.repositories.tag_repository import TagRepository


class GetTagsUseCase:
    def __init__(self, repository: TagRepository):
        self.repository = repository

    async def execute(self):
        return await self.repository.get_all()