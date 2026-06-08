import openai
from openai import OpenAI

from app.config import settings
from app.domain.entities import Note, Summary
from app.domain.interfaces import ISummarizer
from app.exceptions import NoteTextEmptyError, SummarizationFailedError


class YandexCloudSummarizer(ISummarizer):
    """Реализация суммаризации через YandexCloud."""

    def __init__(self) -> None:
        self._client = OpenAI(
            api_key=settings.yandex_cloud_api_key,
            base_url="https://ai.api.cloud.yandex.net/v1",
        )
        self._model = f"gpt://{settings.yandex_cloud_folder}/{settings.yandex_cloud_model}"

    async def summarize(self, note: Note) -> Summary:
        self._validate_note(note)

        try:
            response = self._client.chat.completions.create(
                model=self._model,
                temperature=settings.summarize_temperature,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Ты — ассистент, который делает краткую суммаризацию текста. "
                            "Выдели самую суть. Отвечай на русском языке. "
                            "Верни только текст суммаризации, без вводных фраз."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"Сделай краткую суммаризацию следующего текста:\n\n{note.text}",
                    },
                ],
                max_tokens=settings.summarize_max_tokens,
            )

            summary_text = response.choices[0].message.content
            if summary_text is None:
                raise SummarizationFailedError("Модель вернула пустой ответ")

            return Summary(note_id=note.note_id, summary=summary_text.strip())

        except openai.APIError as e:
            raise SummarizationFailedError(f"Ошибка API YandexCloud: {e}") from e

    @staticmethod
    def _validate_note(note: Note) -> None:
        if not note.text.strip():
            raise NoteTextEmptyError("Текст заметки не может быть пустым")