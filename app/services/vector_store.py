from __future__ import annotations

import logging
import uuid

import chromadb
from chromadb.utils import embedding_functions

from app.config import settings

logger = logging.getLogger(__name__)

# Singleton ChromaDB client and collection
_client: chromadb.PersistentClient | None = None
_collection: chromadb.Collection | None = None


def _get_embedding_function():
    """Get the sentence-transformer embedding function."""
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )


def get_collection() -> chromadb.Collection:
    """Get or create the ChromaDB collection (singleton)."""
    global _client, _collection

    if _collection is None:
        _client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
        _collection = _client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            embedding_function=_get_embedding_function(),
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(
            f"ChromaDB collection '{settings.CHROMA_COLLECTION_NAME}' loaded "
            f"with {_collection.count()} documents"
        )

    return _collection


def add_documents(documents: list[dict]) -> int:
    """Add chunked documents to the vector store. Returns count of added docs."""
    collection = get_collection()

    ids = [str(uuid.uuid4()) for _ in documents]
    texts = [doc["text"] for doc in documents]
    metadatas = [doc["metadata"] for doc in documents]

    # ChromaDB has a batch size limit; process in batches of 500
    batch_size = 500
    added = 0
    for i in range(0, len(ids), batch_size):
        batch_end = i + batch_size
        collection.add(
            ids=ids[i:batch_end],
            documents=texts[i:batch_end],
            metadatas=metadatas[i:batch_end],
        )
        added += len(ids[i:batch_end])

    logger.info(f"Added {added} documents to vector store")
    return added


def query(query_text: str, n_results: int = 5) -> list[dict]:
    """Query the vector store and return relevant document chunks with metadata."""
    collection = get_collection()

    if collection.count() == 0:
        return []

    results = collection.query(query_texts=[query_text], n_results=n_results)

    documents = []
    for i in range(len(results["ids"][0])):
        documents.append(
            {
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
            }
        )

    return documents


def get_stats() -> dict:
    """Get collection statistics."""
    collection = get_collection()
    return {"total_documents": collection.count()}


def reset_collection() -> None:
    """Delete and recreate the collection."""
    global _client, _collection

    if _client is None:
        _client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)

    _client.delete_collection(name=settings.CHROMA_COLLECTION_NAME)
    _collection = None
    # Recreate empty collection
    get_collection()
    logger.info("Vector store collection reset")
