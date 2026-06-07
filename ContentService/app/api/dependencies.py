from fastapi import Depends

from app.db import async_session
from app.repositories.note_repository import NoteRepository
from app.repositories.tag_repository import TagRepository
from app.repositories.file_repository import FileRepository
from app.use_case.files.delete_file import DeleteFileUseCase
from app.use_case.files.get_url_file import GetUrlFileUseCase
from app.use_case.files.upload_file import UploadFileUseCase
from app.use_case.notes.create_note import CreateNoteUseCase
from app.use_case.notes.delete_note import DeleteNoteUseCase
from app.use_case.notes.get_note import GetNoteUseCase
from app.use_case.notes.get_notes import GetNotesUseCase
from app.use_case.notes.update_note import UpdateNoteUseCase
from app.use_case.tags.create_tag import CreateTagUseCase
from app.use_case.tags.delete_tag import DeleteTagUseCase
from app.use_case.tags.get_tag import GetTagUseCase
from app.use_case.tags.get_tags import GetTagsUseCase
from app.use_case.tags.update_tag import UpdateTagUseCase

# Репозитории
def get_note_repository() -> NoteRepository:
    return NoteRepository(session_factory=async_session)

def get_tag_repository() -> TagRepository:
    return TagRepository(session_factory=async_session)

def get_file_repository() -> FileRepository:
    return FileRepository(session_factory=async_session)


# Заметки
def get_note_use_case(
    repository: NoteRepository = Depends(get_note_repository),
) -> GetNoteUseCase:
    return GetNoteUseCase(repository)


def get_notes_use_case(
    repository: NoteRepository = Depends(get_note_repository),
) -> GetNotesUseCase:
    return GetNotesUseCase(repository)


def get_create_note_use_case(
    repository: NoteRepository = Depends(get_note_repository),
) -> CreateNoteUseCase:
    return CreateNoteUseCase(repository)

def get_update_note_use_case(
        repository: NoteRepository = Depends(get_note_repository)
) -> UpdateNoteUseCase:
    return UpdateNoteUseCase(repository)

def get_delete_note_use_case(
        repository: NoteRepository = Depends(get_note_repository)
) -> DeleteNoteUseCase:
    return DeleteNoteUseCase(repository)


# Теги
def get_tag_use_case(
        repository: TagRepository = Depends(get_tag_repository)
) -> GetTagUseCase:
    return GetTagUseCase(repository)

def get_tags_use_case(
        repository: TagRepository = Depends(get_tag_repository)
) -> GetTagsUseCase:
    return GetTagsUseCase(repository)

def get_create_tag_use_case(
        repository: TagRepository = Depends(get_tag_repository)
) -> CreateTagUseCase:
    return CreateTagUseCase(repository)

def get_update_tag_use_case(
        repository: TagRepository = Depends(get_tag_repository)
) -> UpdateTagUseCase:
    return UpdateTagUseCase(repository)

def get_delete_tag_use_case(
        repository: TagRepository = Depends(get_tag_repository)
) -> DeleteTagUseCase:
    return DeleteTagUseCase(repository)


# Файлы
def get_upload_file_use_case(
        repository: FileRepository = Depends(get_file_repository)
) -> UploadFileUseCase:
    return UploadFileUseCase(repository=repository)

def get_delete_file_use_case(
        repository: FileRepository = Depends(get_file_repository)
) -> DeleteFileUseCase:
    return DeleteFileUseCase(repository=repository)

def get_url_file_use_case(
        repository: FileRepository = Depends(get_file_repository)
) -> GetUrlFileUseCase:
    return GetUrlFileUseCase(repository=repository)