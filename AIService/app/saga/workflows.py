from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from app.saga.activities import summarize_activity, publish_to_rabbitmq_activity, compensate_publish_activity


@workflow.defn
class SummarizationWorkflow:
    """Saga: суммаризация + отправка в RabbitMQ."""

    @workflow.run
    async def run(self, note_id: str, text: str, user_id: str) -> dict:
        retry_policy = RetryPolicy(
            maximum_attempts=3,
            maximum_interval=timedelta(seconds=10),
        )

        try:
            result = await workflow.execute_activity(
                summarize_activity,
                args=[note_id, text],
                start_to_close_timeout=timedelta(seconds=60),
                retry_policy=retry_policy,
            )
        except Exception as e:
            raise workflow.ApplicationError(f"Summarization failed: {e}")

        summary = result["summary"]

        try:
            await workflow.execute_activity(
                publish_to_rabbitmq_activity,
                args=[note_id, summary, user_id],
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=retry_policy,
            )
        except Exception as e:
            await workflow.execute_activity(
                compensate_publish_activity,
                args=[note_id, user_id, str(e)],
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=RetryPolicy(maximum_attempts=1),
            )
            raise workflow.ApplicationError(f"RabbitMQ publish failed: {e}")

        return {"note_id": note_id, "summary": summary, "status": "completed"}