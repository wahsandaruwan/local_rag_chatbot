import os
import logging

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from app.config import settings
from app.services import pdf_service, vector_store

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/documents", tags=["documents"])


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a PDF document, extract text, chunk it, and store embeddings."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    # Check file size
    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > settings.MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"File too large ({size_mb:.1f}MB). Maximum is {settings.MAX_FILE_SIZE_MB}MB",
        )

    # Save file temporarily
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
    try:
        with open(file_path, "wb") as f:
            f.write(content)

        # Process PDF into chunks
        documents = pdf_service.process_pdf(file_path, file.filename)
        if not documents:
            raise HTTPException(
                status_code=400, detail="No text content found in the PDF"
            )

        # Store in vector database
        added_count = vector_store.add_documents(documents)

        return JSONResponse(
            content={
                "message": f"Successfully processed '{file.filename}'",
                "chunks_added": added_count,
                "total_documents": vector_store.get_stats()["total_documents"],
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during processing")
    finally:
        # Clean up uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)


@router.get("/stats")
async def get_document_stats():
    """Get the number of document chunks in the vector store."""
    try:
        stats = vector_store.get_stats()
        return JSONResponse(content=stats)
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve stats")


@router.delete("/reset")
async def reset_documents():
    """Clear all documents from the vector store."""
    try:
        vector_store.reset_collection()
        return JSONResponse(content={"message": "Knowledge base has been reset"})
    except Exception as e:
        logger.error(f"Reset error: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset knowledge base")
