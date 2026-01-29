# AI-Powered RAG System

A production-ready backend system that accepts documents (PDFs/Images), processes them using a **multi-agent architecture**, stores structured knowledge in a vector database, and answers user questions grounded strictly in uploaded content.

## 🎯 Project Overview

This system implements a **Retrieval-Augmented Generation (RAG)** pipeline with three specialized agents:

- **Ingestion Agent**: Validates, stores, and extracts text from documents
- **Indexing Agent**: Chunks text, generates embeddings, and stores vectors in FAISS
- **QA Agent**: Retrieves relevant context and generates accurate answers using Groq LLaMA

## 🏗️ Architecture

```
┌─────────────────┐
│   Client/API    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    FastAPI      │
│  (main.py)      │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│  Orchestration Layer        │
│  (API Routes)               │
└─────┬───────────────────────┘
      │
      ├──► Ingestion Agent
      │    ├─ PDF Service
      │    ├─ OCR Service
      │    └─ Text Cleaning
      │
      ├──► Indexing Agent
      │    ├─ Text Chunking
      │    ├─ Embedding Service (Sentence Transformers)
      │    ├─ FAISS Vector DB
      │    └─ SQLite Metadata
      │
      └──► QA Agent
           ├─ Query Embedding
           ├─ FAISS Retrieval
           └─ LLM Generation (Groq LLaMA)
```

## 📁 Project Structure

```
app/
├── main.py                      # FastAPI entry point
├── config.py                    # Configuration management
├── requirements.txt             # Python dependencies
│
├── api/                         # API endpoints
│   ├── upload.py                # POST /documents/upload
│   └── ask.py                   # POST /documents/ask
│
├── agents/                      # Core business logic agents
│   ├── ingestion_agent.py       # Document processing & text extraction
│   ├── indexing_agent.py        # Chunking, embedding, vector storage
│   └── qa_agent.py              # Question answering with RAG
│
├── services/                    # Low-level service implementations
│   ├── ocr_service.py           # Tesseract OCR for images
│   ├── pdf_service.py           # PyPDF2 text extraction
│   ├── embedding_service.py     # Sentence Transformer embeddings
│   ├── faiss_service.py         # FAISS vector database
│   └── llm_service.py           # Groq API wrapper
│
├── db/                          # Database layer
│   ├── models.py                # SQLAlchemy models
│   └── session.py               # Database session management
│
├── utils/                       # Utility functions
│   ├── chunking.py              # Text splitting logic
│   └── cleaning.py              # Text normalization
│
└── storage/                     # File storage
    ├── uploads/                 # Uploaded documents
    └── faiss/                   # Persisted FAISS index
```

## 🚀 Setup Instructions

### Prerequisites

- Python 3.9+
- Tesseract OCR (for image processing)
- Groq API key (get from [console.groq.com](https://console.groq.com))

### 1. Install Tesseract OCR

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

**Windows:**
Download from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki)

### 2. Clone and Setup

```bash
# Clone repository
git clone <repository-url>
cd app

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your Groq API key
nano .env
```

**Required in `.env`:**
```env
GROQ_API_KEY=your_groq_api_key_here
```

### 4. Run the Application

```bash
# Start the server
uvicorn app.main:app --reload

# Server will start at http://localhost:8000
# API documentation available at http://localhost:8000/docs
```

## 📡 API Endpoints

### 1. Upload Document

**Endpoint:** `POST /documents/upload`

**Description:** Upload a PDF or image, extract text, and index it for search.

**Request:**
```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/document.pdf"
```

**Response:**
```json
{
  "document_id": "doc_abc123def456",
  "filename": "document.pdf",
  "status": "indexed",
  "message": "Document processed and indexed successfully",
  "num_chunks": 15
}
```

### 2. Ask Question

**Endpoint:** `POST /documents/ask`

**Description:** Ask a question based on uploaded documents. Answers are grounded in document content.

**Request:**
```bash
curl -X POST "http://localhost:8000/documents/ask" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the refund policy?"
  }'
```

**Response:**
```json
{
  "answer": "According to the uploaded documents, the refund policy allows returns within 30 days of purchase with a valid receipt. Items must be in original condition.",
  "sources": ["doc_abc123def456"],
  "num_sources": 1,
  "confidence": "high"
}
```

### 3. Health Check

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "vector_db": {
    "status": "connected",
    "total_vectors": 156
  },
  "groq_api": "configured"
}
```

## 🧪 Testing with Sample Documents

### Using curl

```bash
# 1. Upload a document
curl -X POST "http://localhost:8000/documents/upload" \
  -F "file=@sample.pdf"

# 2. Ask a question
curl -X POST "http://localhost:8000/documents/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the main topic of the document?"}'
```

### Using Postman

1. **Upload Document:**
   - Method: `POST`
   - URL: `http://localhost:8000/documents/upload`
   - Body: `form-data` with key `file` (type: File)
   - Select your PDF or image file

2. **Ask Question:**
   - Method: `POST`
   - URL: `http://localhost:8000/documents/ask`
   - Body: `raw` (JSON)
   ```json
   {
     "question": "Your question here"
   }
   ```

### Using Python

```python
import requests

# Upload document
with open("document.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/documents/upload",
        files={"file": f}
    )
    print(response.json())

# Ask question
response = requests.post(
    "http://localhost:8000/documents/ask",
    json={"question": "What is the main topic?"}
)
print(response.json())
```

## 🔍 Agent Responsibilities

### Ingestion Agent (`ingestion_agent.py`)

**Purpose:** Convert raw documents into clean, structured text

**Workflow:**
1. Validate file type and size
2. Save uploaded file to storage
3. Extract text:
   - PDFs → PyPDF2
   - Images → Tesseract OCR
4. Clean and normalize text
5. Return extracted text

**Error Handling:**
- Unsupported file types
- Corrupted documents
- Failed OCR extraction

### Indexing Agent (`indexing_agent.py`)

**Purpose:** Transform text into searchable vector representations

**Workflow:**
1. Split text into overlapping chunks (500 chars, 50 overlap)
2. Generate embeddings using Sentence Transformers
3. Store vectors in FAISS for similarity search
4. Store chunk metadata in SQLite
5. Persist FAISS index to disk

**Design Choice:** Overlapping chunks ensure context isn't lost at boundaries

### QA Agent (`qa_agent.py`)

**Purpose:** Answer questions using retrieved context

**Workflow:**
1. Embed user question
2. Retrieve top-k similar chunks from FAISS (k=5)
3. Fetch chunk contents from database
4. Construct context string
5. Generate answer using Groq LLaMA with context
6. Return answer with source attribution

**Safety:** Answers are strictly grounded in retrieved context to prevent hallucinations

## 🛠️ Technology Stack

| Component | Technology | Justification |
|-----------|-----------|---------------|
| **API Framework** | FastAPI | Async, automatic docs, type safety |
| **Text Extraction** | PyPDF2, Tesseract | Reliable, widely used |
| **Embeddings** | Sentence Transformers | Local, fast, cost-free |
| **Vector DB** | FAISS | Efficient local similarity search |
| **LLM** | Groq (LLaMA 3) | Fast inference, high quality |
| **Metadata DB** | SQLite | Simple, sufficient for scope |
| **Storage** | Local filesystem | Task-aligned, easy to manage |

## ⚙️ Configuration Options

Edit `config.py` or set environment variables:

```python
# Model Configuration
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL = "llama-3.3-70b-versatile"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K_RESULTS = 5

# File Limits
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}
```

## 🎯 Design Trade-offs

### ✅ Strengths

1. **Clear Agent Separation**: Each agent has a single, well-defined responsibility
2. **Local-First**: No external dependencies for embeddings (cost-efficient)
3. **Synchronous Processing**: Simpler debugging and flow control
4. **Type Safety**: Pydantic models for all API contracts
5. **Extensible**: Easy to add new document types or models

### ⚠️ Limitations

1. **FAISS Persistence**: Manual save/load required
2. **SQLite Concurrency**: Limited for high-traffic scenarios
3. **OCR Quality**: Depends on image quality
4. **Synchronous Upload**: Large documents block API response

## 🔮 Future Improvements

### Phase 1: Production Readiness
- [ ] Async processing with Celery/Redis
- [ ] PostgreSQL for production database
- [ ] Request authentication & rate limiting
- [ ] Structured logging with correlation IDs
- [ ] Comprehensive error handling

### Phase 2: Enhanced Features
- [ ] Multi-document question answering
- [ ] Document similarity search
- [ ] Caching frequent queries
- [ ] Support for DOCX, TXT files
- [ ] Batch document upload

### Phase 3: Scalability
- [ ] Swap FAISS with Pinecone/Weaviate
- [ ] Distributed task queue
- [ ] Horizontal scaling
- [ ] Advanced chunking strategies (semantic, recursive)
- [ ] Fine-tuned embedding models

## 🐛 Troubleshooting

### Issue: "GROQ_API_KEY not set"
**Solution:** Add your API key to `.env` file:
```bash
GROQ_API_KEY=your_key_here
```

### Issue: "Tesseract not found"
**Solution:** Install Tesseract OCR system package (see Setup Instructions)

### Issue: "No text extracted from PDF"
**Solution:** PDF might be image-based. Try converting to images first or use OCR-enabled PDF processing.

### Issue: Import errors
**Solution:** Ensure virtual environment is activated:
```bash
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

## 📝 License

This project is for educational and evaluation purposes.

## 🤝 Contributing

This is a technical assessment project. For questions or clarifications, contact the project maintainer.

## 📧 Support

For technical issues:
1. Check logs: Application logs show detailed error traces
2. Verify configuration: Ensure `.env` is properly configured
3. Test health endpoint: `GET /health` shows system status

---

**Built with focus on clarity, correctness, and real-world system design principles.**
