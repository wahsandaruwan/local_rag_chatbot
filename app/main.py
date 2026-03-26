import logging
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.routes import documents, chat
from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(
    title="RAG Chatbot",
    description="Local AI-powered RAG chatbot using Ollama and ChromaDB",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files and templates
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Register API routers
app.include_router(documents.router)
app.include_router(chat.router)


@app.get("/")
async def upload_page(request: Request):
    """Serve the document upload page."""
    return templates.TemplateResponse("upload.html", {"request": request})


@app.get("/chat")
async def chat_page(request: Request):
    """Serve the chat interface page."""
    return templates.TemplateResponse("chat.html", {"request": request})


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    # Ensure upload directory exists
    os.makedirs(settings.upload_path, exist_ok=True)
    logger.info("RAG Chatbot started successfully")
