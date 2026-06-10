from typing import List

from pydantic import BaseModel


class OcrFileItem(BaseModel):
    fid: str
    file_url: str

class OcrRequest(BaseModel):
    note_id: str
    files: List[OcrFileItem]

class OcrResponseItem(BaseModel):
    fid: str
    text: str

class OcrResponseListDTO(BaseModel):
    note_id: str
    files: List[OcrResponseItem]