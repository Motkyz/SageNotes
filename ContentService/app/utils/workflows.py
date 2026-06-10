from datetime import timedelta
import asyncio
from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from app.schemas.ocr_schemas import OcrRequest
    from app.schemas.index_schemas import IndexRequest


@workflow.defn(name="SaveNoteWorkflow")
class SaveNoteWorkflow:
    @workflow.run
    async def run(self, note_id: str, base_text: str, files_data: list[dict], token: str) -> dict:

        ocr_retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=5),
            backoff_coefficient=2.0,
            maximum_interval=timedelta(seconds=60),
            maximum_attempts=5
        )

        index_retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=2),
            backoff_coefficient=2.0,
            maximum_attempts=3
        )

        initial_index_payload = {
            "note_id": note_id,
            "text": base_text
        }

        index_task = workflow.execute_activity(
            "index_document_activity",
            args=[initial_index_payload, token],
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=index_retry_policy
        )

        ocr_payload = {
            "note_id": note_id,
            "files": files_data
        }

        ocr_task = workflow.execute_activity(
            "process_ocr_activity",
            args=[ocr_payload, token],
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=ocr_retry_policy
        )

        _, ocr_result_text = await asyncio.gather(index_task, ocr_task)

        if ocr_result_text:
            final_text = f"{base_text}\n{ocr_result_text}".strip()

            final_index_payload = {
                "note_id": note_id,
                "text": final_text
            }

            await workflow.execute_activity(
                "index_document_activity",
                args=[final_index_payload, token],
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=index_retry_policy
            )
            return {"status": "SUCCESS", "indexed_with_ocr": True}

        return {"status": "SUCCESS", "indexed_with_ocr": False}