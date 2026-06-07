from app.repositories.tag_repository import TagRepository


class DeleteTagUseCase:
    def __init__(self, repository: TagRepository):
        self.repository = repository

    async def execute(self, tag_id):
        return await self.repository.delete(tag_id)