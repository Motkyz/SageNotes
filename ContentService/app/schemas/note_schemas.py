from typing import Optional
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.file_schemas import FileResponse
from app.schemas.tag_schemas import TagResponse


class NoteBase(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None


class NoteCreate(NoteBase):
    tags: list[str] = Field(default_factory=list)


class NoteUpdate(NoteBase):
    tags: Optional[list[str]] = None


class NoteResponse(NoteBase):
    id: UUID

    files: list[FileResponse] = Field(default_factory=list)
    tags: list[TagResponse] = Field(default_factory=list)

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)