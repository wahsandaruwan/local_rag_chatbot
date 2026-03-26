# 🤖 Local RAG Chatbot

A fully **local**, **privacy-first** AI chatbot that answers questions based on your PDF documents — powered by **Ollama**, **ChromaDB**, and **FastAPI**. Everything runs on your machine. No data leaves your computer.

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?logo=fastapi&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-Llama_3.1-orange?logo=meta&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-0.5.5-purple)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📖 What Is This?

This is a **Retrieval-Augmented Generation (RAG)** chatbot. In simple terms:

1. You **upload PDF documents** (notes, reports, books, manuals, etc.).
2. The app **reads, splits, and stores** them in a smart database.
3. You **ask questions** in plain English.
4. The chatbot **finds the most relevant parts** of your documents and uses a local AI model to **generate an accurate answer** — with source citations.

> **Think of it as ChatGPT, but it only knows what YOU feed it, and it runs 100% on your own computer.**

---

## ✨ Key Features

- **100% Local & Private** — No cloud APIs. Your data never leaves your machine.
- **PDF Upload & Processing** — Drag-and-drop PDF uploads with automatic text extraction and chunking.
- **Smart Document Search** — Semantic search finds the most relevant document sections for your questions.
- **Real-Time Streaming Responses** — Answers appear word-by-word in real-time, just like ChatGPT.
- **Source Citations** — Every answer includes references to the exact document and page number.
- **Beautiful Dark UI** — Modern glassmorphism design with smooth animations.
- **Health Monitoring** — Live status indicators for AI model and knowledge base.
- **Knowledge Base Management** — View stats and reset your document store anytime.

---

## 🛠️ Technology Stack

| Layer | Technology | What It Does |
|---|---|---|
| **Backend Framework** | [FastAPI](https://fastapi.tiangolo.com/) | High-performance async Python web framework |
| **Web Server** | [Uvicorn](https://www.uvicorn.org/) | Lightning-fast ASGI server |
| **AI Model** | [Ollama](https://ollama.com/) + Llama 3.1 (8B) | Runs the language model locally on your machine |
| **Embeddings** | [Sentence-Transformers](https://www.sbert.net/) (all-MiniLM-L6-v2) | Converts text into numerical vectors for smart searching |
| **Vector Database** | [ChromaDB](https://www.trychroma.com/) | Stores and searches document embeddings efficiently |
| **PDF Processing** | [PyPDF2](https://pypdf2.readthedocs.io/) | Extracts text from PDF files page by page |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript | Clean UI with no heavy frameworks needed |
| **Templating** | [Jinja2](https://jinja.palletsprojects.com/) | Server-side HTML page rendering |
| **HTTP Client** | [httpx](https://www.python-httpx.org/) | Async communication with the Ollama API |
| **Configuration** | [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) | Type-safe configuration with `.env` file support |

---

## 🏗️ How It Works

### The Big Picture

```
┌──────────────────────────────────────────────────────────────┐
│                     YOUR BROWSER                             │
│                                                              │
│   📄 Upload Page                    💬 Chat Page             │
│   ├─ Drag & drop PDFs              ├─ Type your question    │
│   ├─ See upload progress            ├─ See real-time answer  │
│   └─ Manage knowledge base          └─ View source citations │
└──────────────────┬───────────────────────────┬───────────────┘
                   │                           │
                   ▼                           ▼
┌──────────────────────────────────────────────────────────────┐
│                    FASTAPI BACKEND                            │
│                                                              │
│   PDF Service ──▶ Vector Store (ChromaDB)                    │
│   (Extract & Chunk)    (Store & Search Embeddings)           │
│                              │                               │
│   RAG Service ◀──────────────┘                               │
│   (Retrieve relevant context)                                │
│           │                                                  │
│           ▼                                                  │
│   LLM Service ──▶ Ollama (Llama 3.1)                        │
│   (Stream AI response)                                       │
└──────────────────────────────────────────────────────────────┘
```

### Step-by-Step: Uploading a Document

```
PDF File ──▶ Upload API ──▶ Extract Text (page by page)
                                    │
                                    ▼
                           Split Into Chunks
                        (1000 chars, 200 overlap)
                                    │
                                    ▼
                        Generate Embeddings
                      (all-MiniLM-L6-v2 model)
                                    │
                                    ▼
                      Store in ChromaDB (persistent)
```

1. You drag and drop a PDF onto the upload page.
2. The backend extracts text from every page using PyPDF2.
3. The text is split into small overlapping chunks (1000 characters each, with 200 character overlap) — this ensures no context is lost at chunk boundaries.
4. Each chunk is converted into a numerical vector (embedding) using the `all-MiniLM-L6-v2` model.
5. The vectors are stored in ChromaDB on your disk, along with metadata (source file name, page number).

### Step-by-Step: Asking a Question

```
Your Question ──▶ Chat API ──▶ Semantic Search (ChromaDB)
                                       │
                                       ▼
                              Top 5 Relevant Chunks
                                       │
                                       ▼
                              Build Augmented Prompt
                          (Context + Your Question)
                                       │
                                       ▼
                              Send to Ollama (Llama 3.1)
                                       │
                                       ▼
                              Stream Answer Back
                          (word by word, with sources)
```

1. You type a question in the chat.
2. Your question is converted into an embedding vector.
3. ChromaDB finds the **top 5 most similar** document chunks using cosine similarity.
4. A prompt is built combining: the retrieved context + your question + instructions to only answer from the context.
5. The prompt is sent to the Llama 3.1 model running in Ollama.
6. The response streams back **token by token** in real-time via Server-Sent Events (SSE).
7. Source citations (document name + page number) are appended at the end.

---

## 📂 Project Structure

```
├── app/
│   ├── main.py              # FastAPI app entry point & page routes
│   ├── config.py            # All app settings (model, paths, limits)
│   ├── routes/
│   │   ├── chat.py          # Chat API endpoints (POST /api/chat)
│   │   └── documents.py     # Document API endpoints (upload, stats, reset)
│   └── services/
│       ├── pdf_service.py   # PDF text extraction & chunking
│       ├── vector_store.py  # ChromaDB operations (store, search, reset)
│       ├── rag_service.py   # RAG pipeline (retrieve → augment → generate)
│       └── llm_service.py   # Ollama communication (health check, streaming)
├── templates/
│   ├── base.html            # Base layout (navbar, styles, scripts)
│   ├── upload.html          # Document upload page
│   └── chat.html            # Chat interface page
├── static/
│   ├── css/styles.css       # Dark theme with glassmorphism effects
│   └── js/
│       ├── upload.js        # Upload page logic (drag-drop, progress)
│       └── chat.js          # Chat page logic (SSE streaming, formatting)
├── uploads/                 # Temporary storage for uploaded PDFs
├── chroma_data/             # Persistent ChromaDB vector database
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.12+** installed on your machine
- **Ollama** installed and running ([Download Ollama](https://ollama.com/download))

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd "local_rag_chatbot"
```

### 2. Set Up a Virtual Environment

```bash
python3 -m venv rag_env
source rag_env/bin/activate       # Linux / macOS
# rag_env\Scripts\activate        # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install and Start Ollama

Download Ollama from [ollama.com](https://ollama.com/download) and install it. Then pull the Llama 3.1 model:

```bash
ollama pull llama3.1:8b
```

Make sure Ollama is running:

```bash
ollama serve
```

> **Note:** Ollama typically runs automatically in the background after installation. You can verify by visiting `http://localhost:11434` in your browser — you should see "Ollama is running".

### 5. Start the Chatbot

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 6. Open in Your Browser

- **Upload Documents:** [http://localhost:8000](http://localhost:8000)
- **Chat Interface:** [http://localhost:8000/chat](http://localhost:8000/chat)

---

## 📘 How to Use

### Uploading Documents

1. Open [http://localhost:8000](http://localhost:8000) in your browser.
2. **Drag and drop** a PDF file onto the upload zone — or click the zone to browse files.
3. Wait for the upload and processing to complete (you'll see a progress bar).
4. A success notification will confirm how many text chunks were added to the knowledge base.
5. Upload as many PDFs as you need — they all go into the same knowledge base.

### Chatting with Your Documents

1. Navigate to [http://localhost:8000/chat](http://localhost:8000/chat).
2. Check the **status bar** at the top — it should show Ollama as online (green dot) and your document count.
3. Type your question in the text box and press **Enter** (or click the send button).
4. Watch the AI response stream in real-time.
5. At the end of each answer, you'll see **source citations** showing which document and page the information came from.

### Managing the Knowledge Base

- **View Stats:** The upload page shows how many document chunks are stored.
- **Reset:** Click the "Reset Knowledge Base" button on the upload page to clear all stored documents and start fresh.

---

## ⚙️ Configuration

All settings can be customized via environment variables or a `.env` file in the project root:

| Variable | Default | Description |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | URL where Ollama is running |
| `LLM_MODEL` | `llama3.1:8b` | Ollama model to use for answers |
| `CHROMA_PERSIST_DIR` | `./chroma_data` | Where ChromaDB stores its data |
| `CHROMA_COLLECTION_NAME` | `rag_documents` | Name of the ChromaDB collection |
| `CHUNK_SIZE` | `1000` | Characters per text chunk |
| `CHUNK_OVERLAP` | `200` | Overlapping characters between chunks |
| `UPLOAD_DIR` | `./uploads` | Temporary PDF upload directory |
| `MAX_FILE_SIZE_MB` | `50` | Maximum upload file size in MB |

**Example `.env` file:**

```env
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=llama3.1:8b
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_FILE_SIZE_MB=50
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Upload page (web UI) |
| `GET` | `/chat` | Chat page (web UI) |
| `POST` | `/api/documents/upload` | Upload and process a PDF file |
| `GET` | `/api/documents/stats` | Get knowledge base statistics |
| `DELETE` | `/api/documents/reset` | Clear all documents from the knowledge base |
| `POST` | `/api/chat` | Send a question and receive a streamed response (SSE) |
| `GET` | `/api/chat/health` | Check Ollama and vector store health |

### Chat Request Example

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the main topic of the document?", "n_results": 5}'
```

### Upload Example

```bash
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@your-document.pdf"
```

---

## 🧠 How RAG Works (Simple Explanation)

**RAG** stands for **Retrieval-Augmented Generation**. Here's the idea in plain English:

> Instead of asking an AI to answer from its general training data (which may be wrong or outdated), we **first search our own documents** for relevant information, then **give that information to the AI** along with the question. This way, the AI answers based on **your specific documents**.

**Without RAG:**
```
You: "What's the company refund policy?"
AI:  "I don't have specific information about your company policies..." ❌
```

**With RAG:**
```
You: "What's the company refund policy?"
System: *searches your uploaded policy PDF, finds relevant paragraphs*
AI:  "According to the Company Policy Handbook (p.12), refunds are available within 30 days..." ✅
```

---

## 🤔 Frequently Asked Questions

**Q: Do I need an internet connection?**
A: Only for the initial setup (downloading dependencies and the AI model). After that, everything runs offline.

**Q: What types of files can I upload?**
A: Currently, only **PDF** files are supported.

**Q: How much RAM/VRAM do I need?**
A: The Llama 3.1 8B model requires approximately **5GB of RAM** (or VRAM if using GPU). The embedding model needs about **500MB** additionally.

**Q: Can I use a different AI model?**
A: Yes! Pull any model with `ollama pull <model-name>` and update the `LLM_MODEL` setting in your `.env` file or `app/config.py`.

**Q: Where is my data stored?**
A: Document embeddings are stored in the `chroma_data/` folder. Uploaded PDFs are temporarily saved in `uploads/`. Everything stays on your machine.

**Q: Can I reset and start over?**
A: Yes — click the "Reset Knowledge Base" button on the upload page, or call `DELETE /api/documents/reset`.
