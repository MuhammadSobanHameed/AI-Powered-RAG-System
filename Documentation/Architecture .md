# System Architecture - Detailed Documentation

## High-Level Flow Diagram

```
┌──────────────┐
│   Client     │
│  (curl/API)  │
└──────┬───────┘
       │ HTTP Request
       ▼
┌──────────────────────────────────────────────┐
│            FastAPI Application               │
│                 (main.py)                    │
│  ┌──────────────────────────────────────┐   │
│  │       CORS Middleware                │   │
│  │    Logging & Error Handling          │   │
│  └──────────────────────────────────────┘   │
└──────┬───────────────────────────────────────┘
       │
       ├─────► POST /documents/upload (upload.py)
       │       │
       │       ▼
       │    ┌──────────────────────────────────┐
       │    │    Orchestration Layer           │
       │    │  (Coordinates Agent Workflow)    │
       │    └────┬─────────────────────────────┘
       │         │
       │         ├──► 1️⃣  INGESTION AGENT
       │         │    ┌─────────────────────────┐
       │         │    │ • Validate file         │
       │         │    │ • Save to storage       │
       │         │    │ • Extract text          │
       │         │    │   - PDF → PyPDF2        │
       │         │    │   - Image → Tesseract   │
       │         │    │ • Clean & normalize     │
       │         │    └─────────┬───────────────┘
       │         │              │ Extracted Text
       │         │              ▼
       │         ├──► 2️⃣  INDEXING AGENT
       │         │    ┌─────────────────────────┐
       │         │    │ • Chunk text (500/50)   │
       │         │    │ • Generate embeddings   │
       │         │    │   (Sentence Transform)  │
       │         │    │ • Store in FAISS        │
       │         │    │ • Save metadata (SQLite)│
       │         │    └─────────────────────────┘
       │         │
       │         └──► ✅ Return Success Response
       │
       └─────► POST /documents/ask (ask.py)
               │
               ▼
            ┌──────────────────────────────────┐
            │         QA Agent                 │
            │  (Retrieval + Generation)        │
            └────┬─────────────────────────────┘
                 │
                 ├──► 1. Embed Question
                 │    (Sentence Transformers)
                 │
                 ├──► 2. FAISS Similarity Search
                 │    (Retrieve top-k chunks)
                 │
                 ├──► 3. Fetch Chunk Content
                 │    (SQLite Database)
                 │
                 ├──► 4. Construct Context
                 │    (Format retrieved chunks)
                 │
                 └──► 5. Generate Answer
                      (Groq LLaMA 3 API)
                      │
                      ▼
                   ✅ Return Answer + Sources
```

## Agent Interaction Sequence

### Document Upload Flow

```
Client                 API                 Ingestion Agent       Indexing Agent        Database/Storage
  │                     │                          │                     │                      │
  │   POST /upload      │                          │                     │                      │
  ├────────────────────►│                          │                     │                      │
  │                     │  validate & save file    │                     │                      │
  │                     ├─────────────────────────►│                     │                      │
  │                     │                          │   save file         │                      │
  │                     │                          ├────────────────────────────────────────────►│
  │                     │                          │                     │                      │
  │                     │                          │   extract text      │                      │
  │                     │                          │   (PDF/OCR)         │                      │
  │                     │   extracted text         │                     │                      │
  │                     │◄─────────────────────────┤                     │                      │
  │                     │                          │                     │                      │
  │                     │   chunk + embed          │                     │                      │
  │                     ├────────────────────────────────────────────────►│                      │
  │                     │                          │                     │  store vectors       │
  │                     │                          │                     ├─────────────────────►│
  │                     │                          │                     │  (FAISS)             │
  │                     │                          │                     │                      │
  │                     │                          │                     │  store metadata      │
  │                     │                          │                     ├─────────────────────►│
  │                     │                          │                     │  (SQLite)            │
  │                     │   success + doc_id       │                     │                      │
  │   Response (200)    │◄────────────────────────────────────────────────                      │
  │◄────────────────────┤                          │                     │                      │
  │                     │                          │                     │                      │
```

### Question Answering Flow

```
Client                 API                 QA Agent             FAISS/DB             LLM (Groq)
  │                     │                      │                     │                    │
  │   POST /ask         │                      │                     │                    │
  ├────────────────────►│                      │                     │                    │
  │                     │  question            │                     │                    │
  │                     ├─────────────────────►│                     │                    │
  │                     │                      │  embed question     │                    │
  │                     │                      │  (SentenceTransf)   │                    │
  │                     │                      │                     │                    │
  │                     │                      │  search vectors     │                    │
  │                     │                      ├────────────────────►│                    │
  │                     │                      │  top-k chunk IDs    │                    │
  │                     │                      │◄────────────────────┤                    │
  │                     │                      │                     │                    │
  │                     │                      │  fetch chunk content│                    │
  │                     │                      ├────────────────────►│                    │
  │                     │                      │  chunk texts        │                    │
  │                     │                      │◄────────────────────┤                    │
  │                     │                      │                     │                    │
  │                     │                      │  construct context  │                    │
  │                     │                      │                     │                    │
  │                     │                      │  generate answer    │                    │
  │                     │                      ├────────────────────────────────────────►│
  │                     │                      │  answer text        │                    │
  │                     │                      │◄────────────────────────────────────────┤
  │                     │  answer + sources    │                     │                    │
  │   Response (200)    │◄─────────────────────┤                     │                    │
  │◄────────────────────┤                      │                     │                    │
  │                     │                      │                     │                    │
```

## Data Flow

### 1. Document Processing Pipeline

```
Raw Document (PDF/Image)
         │
         ▼
    ┌────────┐
    │ Ingest │  → Validate format, size
    └───┬────┘
        │
        ├──► PDF Path
        │    └─► PyPDF2.extract_text()
        │        └─► Clean Text
        │
        └──► Image Path
             └─► Tesseract OCR
                 └─► Clean Text
                      │
                      ▼
                 ┌─────────┐
                 │  Index  │  → Chunk (500 chars, 50 overlap)
                 └────┬────┘
                      │
                      ├─► Chunk 1 ──► Embedding ──┐
                      ├─► Chunk 2 ──► Embedding ──┤
                      ├─► Chunk 3 ──► Embedding ──├─► FAISS Index
                      ├─► ...                     │   + SQLite
                      └─► Chunk N ──► Embedding ──┘
```

### 2. Question Answering Pipeline

```
User Question
     │
     ▼
 Embed Question
 (384-dim vector)
     │
     ▼
FAISS Similarity Search
     │
     ├─► Chunk 1 (distance: 0.23)
     ├─► Chunk 2 (distance: 0.31)
     ├─► Chunk 3 (distance: 0.45)
     └─► ...
         │
         ▼
    Retrieve Content
    (from SQLite)
         │
         ▼
    Construct Context
    (format chunks)
         │
         ▼
    LLM Prompt:
    ┌────────────────────────┐
    │ System: You are a QA   │
    │ assistant...           │
    │                        │
    │ Context: [chunks]      │
    │                        │
    │ Question: [question]   │
    └────────────────────────┘
         │
         ▼
    Groq LLaMA 3 API
         │
         ▼
    Generated Answer
    + Source Attribution
```

## Component Responsibilities Matrix

| Component | Read | Write | Depends On |
|-----------|------|-------|------------|
| **Ingestion Agent** | Uploaded files | Storage files | OCR, PDF services |
| **Indexing Agent** | Text | FAISS, SQLite | Embedding service |
| **QA Agent** | FAISS, SQLite | None | Embedding, LLM services |
| **FAISS Service** | Index file | Index file | None |
| **Embedding Service** | None | None | Sentence Transformers |
| **LLM Service** | None | None | Groq API |
| **Database** | Queries | Records | None |

## Technology Stack Justification

### Why FastAPI?
- ✅ Automatic OpenAPI documentation
- ✅ Async support for future scaling
- ✅ Type validation with Pydantic
- ✅ Easy to test and extend

### Why Sentence Transformers?
- ✅ Runs locally (no API costs)
- ✅ Fast inference (~50ms per text)
- ✅ High quality embeddings
- ✅ 384 dimensions (efficient storage)

### Why FAISS?
- ✅ Optimized for similarity search
- ✅ Runs locally
- ✅ Handles 100K+ vectors efficiently
- ✅ Simple persistence model

### Why Groq?
- ✅ Fast LLaMA 3 inference (<1s)
- ✅ High quality responses
- ✅ Generous free tier
- ✅ Simple API

### Why SQLite?
- ✅ Zero configuration
- ✅ File-based (easy backup)
- ✅ Sufficient for metadata
- ✅ Easy to upgrade to PostgreSQL

## Scalability Considerations

### Current Limitations
- **Synchronous processing**: Blocks during upload
- **Single FAISS index**: No sharding
- **SQLite**: Limited concurrent writes
- **Local storage**: Not distributed

### Scaling Path
```
Current (MVP)                  →  Production
─────────────────────────────────────────────────
FastAPI (single instance)      →  Load balanced
FAISS (in-memory)              →  Pinecone/Weaviate
SQLite                         →  PostgreSQL
Synchronous                    →  Celery + Redis
Local storage                  →  S3/MinIO
```

## Security Model

### Current Implementation
- ✅ File type validation
- ✅ File size limits
- ✅ Input sanitization
- ❌ No authentication
- ❌ No rate limiting

### Production Requirements
- 🔒 API key authentication
- 🔒 Rate limiting (per user)
- 🔒 Input validation (strict)
- 🔒 Output sanitization
- 🔒 Audit logging

---

**This architecture is designed for clarity and extensibility over premature optimization.**