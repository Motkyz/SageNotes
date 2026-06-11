import asyncio
from temporalio.client import Client
from temporalio.worker import Worker

from app.saga.activities import summarize_activity, publish_to_rabbitmq_activity, compensate_publish_activity
from app.saga.workflows import SummarizationWorkflow


async def start_temporal_worker():
    """Запуск Temporal Worker."""
    client = await Client.connect("temporal:7233", namespace="default")
    
    worker = Worker(
        client,
        task_queue="summarization-task-queue",
        workflows=[SummarizationWorkflow],
        activities=[
            summarize_activity,
            publish_to_rabbitmq_activity,
            compensate_publish_activity,
        ],
    )
    
    print("✅ Temporal Worker запущен")
    await worker.run()