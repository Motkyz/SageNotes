from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

class FileCreate(BaseModel):
    note_id: UUID
    name: str
    key: str
    extension: str
    mime_type: str
    size: int


class FileUpdate(BaseModel):
    pass


class FileResponse(BaseModel):
    id: UUID

    name: str
    url: str | None = None

    extension: str
    mime_type: str
    size: int

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
