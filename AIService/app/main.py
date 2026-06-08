from fastapi import FastAPI

from app.presentation.router import router as summary_router

app = FastAPI(title="Summary Service", version="1.0.0")

app.include_router(summary_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}