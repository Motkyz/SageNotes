from app.domain.interfaces import ISummarizer
from app.domain.use_cases import SummarizeNoteUseCase
from app.infrastructure.llm_client import YandexCloudSummarizer

_summarizer: ISummarizer = YandexCloudSummarizer()
_summarize_use_case = SummarizeNoteUseCase(summarizer=_summarizer)


def get_summarize_use_case() -> SummarizeNoteUseCase:
    """Внедрение зависимости — сценарий суммаризации."""
    return _summarize_use_case