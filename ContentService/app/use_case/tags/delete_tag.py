from app.repositories.tag_repository import TagRepository


class DeleteTagUseCase:
    def __init__(self, repository: TagRepository):
        self.repository = repository

    async def execute(self, user_id: str, tag_id):
        tag = await self.repository.get(tag_id)
        if not tag:
            return False

        if str(tag.user_id) != user_id:
            raise Exception("User not owner of the tag")

        return await self.repository.delete(tag_id)