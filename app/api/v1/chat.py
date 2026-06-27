"""
/api/v1/chat — thin FastAPI router (Module 03, matures through the course).
"""
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1", tags=["chat"])


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    session_id: str
    reply: str


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    # Placeholder — wired to a real agent in Module 03
    return ChatResponse(session_id=req.session_id, reply="[agent not yet wired]")
