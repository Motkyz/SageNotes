from dataclasses import dataclass


@dataclass(frozen=True)
class Note:
    """Заметка, для которой нужна суммаризация."""
    note_id: str
    text: str


@dataclass(frozen=True)
class Summary:
    """Результат суммаризации."""
    note_id: str
    summary: str