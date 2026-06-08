from abc import ABC, abstractmethod

from app.domain.entities import Note, Summary


class ISummarizer(ABC):
    """Порт для сервиса суммаризации."""

    @abstractmethod
    async def summarize(self, note: Note) -> Summary:
        """Создать суммаризацию по заметке."""
        ...