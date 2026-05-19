from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import database
from app.documents.routes import router as documents_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.close()


app = FastAPI(
    title="Private RAG Platform",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(documents_router)


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "private-rag-platform",
        "version": "0.1.0",
    }


@app.get("/health/db")
async def database_health_check():
    result = await database.fetchval("SELECT 1;")

    return {
        "status": "ok",
        "database": "connected",
        "result": result,
    }