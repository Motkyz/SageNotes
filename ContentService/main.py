import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from temporalio.client import Client
from temporalio.worker import Worker

from app.api.router import main_router
from app.config import settingTemporal
from app.db import init_database
from app.utils.activities import process_ocr_activity, index_document_activity, index_document_grpc_activity, \
    process_ocr_grpc_activity

from app.utils.workflows import SaveNoteWorkflow
from app.grpc.server import start_grpc_server


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_database()

    client = await Client.connect(settingTemporal.TEMPORAL_HOST)
    setattr(app.state, "temporal_client", client)

    worker = Worker(
        client,
        task_queue=settingTemporal.TEMPORAL_TASK_QUEUE,
        workflows=[SaveNoteWorkflow],
        activities=[
            process_ocr_activity,
            index_document_activity,
            process_ocr_grpc_activity,
            index_document_grpc_activity
        ],
    )
    worker_task = asyncio.create_task(worker.run())

    grpc_task = asyncio.create_task(
        start_grpc_server(client)
    )

    yield

    grpc_task.cancel()

    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        print("Temporal Worker background task cancelled successfully.")


app = FastAPI(title="ContentService", lifespan=lifespan)
app.include_router(main_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)