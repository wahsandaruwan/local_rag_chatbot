import logging
from PyPDF2 import PdfReader

from app.config import settings

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_path: str) -> list[dict]:
    """Extract text from a PDF and return a list of page-level text blocks."""
    pages = []
    try:
        reader = PdfReader(file_path)
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text and text.strip():
                pages.append({"text": text.strip(), "page": i + 1})
    except Exception as e:
        logger.error(f"Failed to read PDF {file_path}: {e}")
        raise ValueError(f"Could not process PDF: {e}")
    return pages


def chunk_text(
    text: str,
    chunk_size: int = settings.CHUNK_SIZE,
    chunk_overlap: int = settings.CHUNK_OVERLAP,
) -> list[str]:
    """Split text into overlapping chunks for embedding."""
    if not text:
        return []

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - chunk_overlap

    return chunks


def process_pdf(file_path: str, filename: str) -> list[dict]:
    """Extract text from PDF, chunk it, and return documents with metadata."""
    pages = extract_text_from_pdf(file_path)
    documents = []

    for page_data in pages:
        chunks = chunk_text(page_data["text"])
        for i, chunk in enumerate(chunks):
            documents.append(
                {
                    "text": chunk,
                    "metadata": {
                        "source": filename,
                        "page": page_data["page"],
                        "chunk_index": i,
                    },
                }
            )

    logger.info(f"Processed {filename}: {len(documents)} chunks from {len(pages)} pages")
    return documents
