import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api.router import main_router
from app.db import init_database
from app.grpc.server import start_grpc_server


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_database()
    grpc_task = asyncio.create_task(
        start_grpc_server()
    )

    yield

    grpc_task.cancel()

app = FastAPI(title="ContentService", lifespan=lifespan)
app.include_router(main_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)