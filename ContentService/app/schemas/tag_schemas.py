from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TagBase(BaseModel):
    title: str
    color: str


class TagCreate(TagBase):
    pass


class TagUpdate(TagBase):
    title: Optional[str] = None
    color: Optional[str] = None


class TagResponse(TagBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)
