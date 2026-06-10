from pydantic import BaseModel


class IndexRequest(BaseModel):
    note_id: str
    text: str