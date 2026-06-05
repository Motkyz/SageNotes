from fastapi import APIRouter, Depends

from app.domain.use_cases import SummarizeNoteUseCase
from app.presentation.dependencies import get_summarize_use_case
from app.presentation.schemas import SummarizeRequest, SummarizeResponse

router = APIRouter(prefix="/summary", tags=["summary"])


@router.post("", response_model=SummarizeResponse)
async def summarize_note(
    request: SummarizeRequest,
    use_case: SummarizeNoteUseCase = Depends(get_summarize_use_case),
) -> SummarizeResponse:
    """Создать суммаризацию по тексту заметки."""
    result = await use_case.execute(note_id=request.note_id, text=request.text)
    return SummarizeResponse(note_id=result.note_id, summary=result.summary)