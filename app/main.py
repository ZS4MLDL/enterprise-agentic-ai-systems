"""
FastAPI application entry point.
"""
from fastapi import FastAPI
from app.api.v1.chat import router as chat_router

app = FastAPI(title="Enterprise Research and Knowledge Assistant Platform")

app.include_router(chat_router)


@app.get("/health")
def health():
    return {"status": "ok"}
