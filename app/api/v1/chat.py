"""
/api/v1/chat — FastAPI router (Module 03).
Wired to the stateful ResearchAgent.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.agents import research_agent

router = APIRouter(prefix="/api/v1", tags=["chat"])


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    session_id: str
    reply: str


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    try:
        reply = research_agent.run(req.session_id, req.message)
        return ChatResponse(session_id=req.session_id, reply=reply)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/chat/stream")
async def chat_stream(req: ChatRequest) -> StreamingResponse:
    def generate():
        try:
            for chunk in research_agent.stream(req.session_id, req.message):
                yield chunk
        except ValueError as e:
            yield f"[error: {e}]"
        except RuntimeError as e:
            yield f"[error: {e}]"

    return StreamingResponse(generate(), media_type="text/plain")
