from fastapi import FastAPI

app = FastAPI(
    title="Private RAG Platform",
    version="0.1.0",
)


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "private-rag-platform",
        "version": "0.1.0",
    }
