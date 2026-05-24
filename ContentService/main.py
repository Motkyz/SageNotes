from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api.router import main_router
from app.db import engine, Base, init_database


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await init_database()
    yield

app = FastAPI(title="ContentService", lifespan=lifespan)
app.include_router(main_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)