from app.models import File
from app.repositories.base_repository import BaseRepository
from app.schemas.file_schemas import FileCreate, FileUpdate


class FileRepository(
    BaseRepository[File, FileCreate, FileUpdate]
):

    model_cls = File