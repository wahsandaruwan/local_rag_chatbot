import logging
from collections.abc import AsyncGenerator

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


async def check_health() -> dict:
    """Check if Ollama is running and the model is available."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [m["name"] for m in models]
                model_available = any(
                    settings.LLM_MODEL in name for name in model_names
                )
                return {
                    "ollama_running": True,
                    "model_available": model_available,
                    "model_name": settings.LLM_MODEL,
                    "available_models": model_names,
                }
    except (httpx.ConnectError, httpx.TimeoutException):
        pass

    return {
        "ollama_running": False,
        "model_available": False,
        "model_name": settings.LLM_MODEL,
        "available_models": [],
    }


async def generate_stream(prompt: str, system: str = "") -> AsyncGenerator[str, None]:
    """Stream tokens from Ollama's generate API."""
    payload = {
        "model": settings.LLM_MODEL,
        "prompt": prompt,
        "stream": True,
    }
    if system:
        payload["system"] = system

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{settings.OLLAMA_BASE_URL}/api/generate",
                json=payload,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        import json

                        data = json.loads(line)
                        token = data.get("response", "")
                        if token:
                            yield token
                        if data.get("done", False):
                            break
    except httpx.ConnectError:
        yield "\n\n⚠️ Error: Cannot connect to Ollama. Please ensure it is running."
    except Exception as e:
        logger.error(f"LLM generation error: {e}")
        yield f"\n\n⚠️ Error: {e}"
