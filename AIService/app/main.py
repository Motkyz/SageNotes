import asyncio
from contextlib import asynccontextmanager

import grpc
from fastapi import FastAPI
from fastapi.security import HTTPBearer

from app.presentation.router import router as summary_router
from app.presentation.dependencies import _rabbitmq, get_summarize_use_case
from app.infrastructure.grpc_servicer import SummaryGrpcServicer
from app.proto import summary_pb2_grpc
from app.saga.worker import start_temporal_worker


@asynccontextmanager
async def lifespan(application: FastAPI):
    try:
        await _rabbitmq.connect()
        print("✅ RabbitMQ подключён")
    except Exception as e:
        print(f"⚠️ RabbitMQ недоступен ({e}) — работаем без очереди")

    grpc_server = grpc.aio.server()
    use_case = get_summarize_use_case()
    summary_pb2_grpc.add_SummaryServiceServicer_to_server(
        SummaryGrpcServicer(use_case), grpc_server
    )
    grpc_server.add_insecure_port("[::]:9090")
    await grpc_server.start()
    print("✅ gRPC сервер запущен на порту 9090")

    temporal_task = asyncio.create_task(start_temporal_worker())

    yield

    temporal_task.cancel()
    await grpc_server.stop(0)
    try:
        await _rabbitmq.close()
    except Exception:
        pass


app = FastAPI(
    title="Summary Service",
    version="1.0.0",
    lifespan=lifespan,
    swagger_ui_parameters={"persistAuthorization": True},
)

security = HTTPBearer(auto_error=False)
app.include_router(summary_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}