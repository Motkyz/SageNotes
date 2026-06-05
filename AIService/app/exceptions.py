class SummaryServiceError(Exception):
    """Базовое исключение сервиса."""
    pass


class SummarizationFailedError(SummaryServiceError):
    """Ошибка при генерации суммаризации."""
    pass


class NoteTextEmptyError(SummaryServiceError):
    """Текст заметки пуст."""
    pass