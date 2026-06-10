import asyncio
from temporalio.client import Client
from temporalio.worker import Worker

# Импортируем наш конфиг
from app.config import settingTemporal
from activities import process_ocr_activity, index_document_activity
from workflows import SaveNoteWorkflow

async def main():
    client = await Client.connect(settingTemporal.TEMPORAL_HOST)

    worker = Worker(
        client,
        task_queue=settingTemporal.TEMPORAL_TASK_QUEUE,
        workflows=[SaveNoteWorkflow],
        activities=[process_ocr_activity, index_document_activity],
    )

    print(f"Content Service Temporal Worker started on {settingTemporal.TEMPORAL_HOST}...")
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())