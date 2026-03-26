import json
import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.services import rag_service, llm_service, vector_store

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chat", tags=["chat"])


class ChatRequest(BaseModel):
    """Chat request body."""
    query: str
    n_results: int = 5


@router.post("")
async def chat(request: ChatRequest):
    """Send a query and receive a streamed RAG response via SSE."""
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    async def event_stream():
        try:
            async for token in rag_service.query_and_respond(
                request.query, n_results=request.n_results
            ):
                # Format as SSE
                data = json.dumps({"token": token})
                yield f"data: {data}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            logger.error(f"Chat stream error: {e}")
            error_data = json.dumps({"error": str(e)})
            yield f"data: {error_data}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.get("/health")
async def health_check():
    """Check Ollama and vector store health."""
    ollama_health = await llm_service.check_health()
    db_stats = vector_store.get_stats()

    return {
        "ollama": ollama_health,
        "vector_store": {
            "status": "connected",
            "total_documents": db_stats["total_documents"],
        },
    }
