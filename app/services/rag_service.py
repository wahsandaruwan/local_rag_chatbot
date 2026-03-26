import logging
from collections.abc import AsyncGenerator

from app.services import vector_store, llm_service

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a helpful AI assistant that answers questions based on the provided context documents.

Rules:
- Answer ONLY based on the provided context. If the context doesn't contain enough information, say so clearly.
- Cite the source document and page number when possible.
- Be concise and accurate.
- If no context is provided, inform the user to upload relevant documents first."""


def _build_context_prompt(query: str, context_docs: list[dict]) -> str:
    """Build the prompt with retrieved context."""
    if not context_docs:
        return (
            f"User Question: {query}\n\n"
            "Note: No documents have been uploaded to the knowledge base yet. "
            "Please inform the user to upload relevant PDF documents first."
        )

    context_parts = []
    for i, doc in enumerate(context_docs, 1):
        source = doc["metadata"].get("source", "Unknown")
        page = doc["metadata"].get("page", "?")
        context_parts.append(
            f"[Source {i}: {source}, Page {page}]\n{doc['text']}"
        )

    context_text = "\n\n---\n\n".join(context_parts)
    return (
        f"Context Documents:\n\n{context_text}\n\n"
        f"---\n\n"
        f"User Question: {query}\n\n"
        f"Please answer based on the context above."
    )


async def query_and_respond(
    query: str, n_results: int = 5
) -> AsyncGenerator[str, None]:
    """Retrieve relevant docs, build prompt, and stream the LLM response."""
    # Retrieve relevant context
    context_docs = vector_store.query(query, n_results=n_results)
    logger.info(f"Retrieved {len(context_docs)} context documents for query")

    # Build augmented prompt
    prompt = _build_context_prompt(query, context_docs)

    # Stream LLM response
    async for token in llm_service.generate_stream(prompt, system=SYSTEM_PROMPT):
        yield token

    # Yield source references at the end
    if context_docs:
        sources = set()
        for doc in context_docs:
            source = doc["metadata"].get("source", "Unknown")
            page = doc["metadata"].get("page", "?")
            sources.add(f"{source} (p.{page})")

        yield "\n\n---\n📚 **Sources:** " + ", ".join(sorted(sources))
