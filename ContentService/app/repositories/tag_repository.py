from app.models import Tag
from app.repositories.base_repository import BaseRepository
from app.schemas.tag_schemas import TagCreate, TagUpdate


class TagRepository(
    BaseRepository[Tag, TagCreate, TagUpdate]
):

    model_cls = Tag