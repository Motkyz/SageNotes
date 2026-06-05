from pydantic import BaseModel, Field


class SummarizeRequest(BaseModel):
    note_id: str = Field(..., description="Идентификатор заметки", examples=["abc-123"])
    text: str = Field(..., description="Полный текст заметки для суммаризации", min_length=1)


class SummarizeResponse(BaseModel):
    note_id: str = Field(..., description="Идентификатор заметки")
    summary: str = Field(..., description="Текст суммаризации")