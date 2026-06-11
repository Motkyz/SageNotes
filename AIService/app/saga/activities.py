from temporalio import activity

from app.domain.entities import Note
from app.infrastructure.llm_client import YandexCloudSummarizer
from app.infrastructure.rabbitmq_publisher import RabbitMQPublisher
from app.presentation.dependencies import _summarizer, _rabbitmq


@activity.defn
async def summarize_activity(note_id: str, text: str) -> dict:
    """Activity: суммаризация текста."""
    note = Note(note_id=note_id, text=text)
    result = await _summarizer.summarize(note, user_id="temporal")
    return {"note_id": result.note_id, "summary": result.summary}


@activity.defn
async def publish_to_rabbitmq_activity(note_id: str, summary: str, user_id: str) -> dict:
    """Activity: отправка результата в RabbitMQ."""
    await _rabbitmq.publish_summary_completed(
        note_id=note_id,
        summary=summary,
        user_id=user_id,
    )
    return {"status": "sent"}


@activity.defn
async def compensate_publish_activity(note_id: str, user_id: str, error: str) -> dict:
    """Activity: компенсация — отправка события об ошибке."""
    try:
        await _rabbitmq.publish_summary_failed(
            note_id=note_id,
            user_id=user_id,
            error=error,
        )
    except Exception:
        pass
    return {"status": "compensated"}