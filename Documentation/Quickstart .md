# Quick Start Guide

Get the AI-Powered RAG System running in 5 minutes.

## Prerequisites

- Python 3.9+
- Tesseract OCR
- Groq API key (free from [console.groq.com](https://console.groq.com))

## Fast Setup

### Option 1: Automated Setup (Recommended)

```bash
# Clone repository
git clone <repository-url>
cd app

# Run setup script
chmod +x setup.sh
./setup.sh

# Add your API key to .env
echo "GROQ_API_KEY=your_key_here" >> .env

# Start server
source venv/bin/activate
uvicorn app.main:app --reload
```

### Option 2: Manual Setup

```bash
# 1. Install Tesseract
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# 2. Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# 4. Run server
uvicorn app.main:app --reload
```

### Option 3: Docker (Optional)

```bash
# Create .env file
echo "GROQ_API_KEY=your_key_here" > .env

# Run with Docker Compose
docker-compose up --build
```

## Verify Installation

```bash
# Check health
curl http://localhost:8000/health

# Should return:
# {"status": "healthy", ...}
```

## First Test

### 1. Upload a Document

```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -F "file=@your_document.pdf"
```

**Response:**
```json
{
  "document_id": "doc_abc123",
  "status": "indexed",
  "num_chunks": 12
}
```

### 2. Ask a Question

```bash
curl -X POST "http://localhost:8000/documents/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this document about?"}'
```

**Response:**
```json
{
  "answer": "This document discusses...",
  "sources": ["doc_abc123"],
  "confidence": "high"
}
```

## Next Steps

- 📖 Read [README.md](README.md) for full documentation
- 🏗️ See [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- 📋 Check [SAMPLE_API_CALLS.md](SAMPLE_API_CALLS.md) for more examples
- 🎯 Review [DESIGN_DECISIONS.md](DESIGN_DECISIONS.md) for trade-offs

## Common Issues

### "GROQ_API_KEY not set"
**Fix:** Add your key to `.env`:
```bash
echo "GROQ_API_KEY=your_actual_key" >> .env
```

### "Tesseract not found"
**Fix:** Install Tesseract OCR (see Prerequisites)

### "Port 8000 already in use"
**Fix:** Change port:
```bash
uvicorn app.main:app --port 8001
```

### Import errors
**Fix:** Activate virtual environment:
```bash
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

## Interactive API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Quick Architecture Overview

```
Upload → Ingestion Agent → Indexing Agent → FAISS + SQLite
                                                    │
Ask → QA Agent → Retrieve from FAISS → LLM ← ──────┘
```

## Development Mode

```bash
# Enable debug logging
export DEBUG=True

# Run with auto-reload
uvicorn app.main:app --reload --log-level debug
```

## Production Checklist

Before deploying to production:

- [ ] Set `DEBUG=False` in .env
- [ ] Use PostgreSQL instead of SQLite
- [ ] Add authentication
- [ ] Configure CORS properly
- [ ] Set up monitoring
- [ ] Enable HTTPS
- [ ] Implement rate limiting

## Need Help?

1. Check the logs in the console
2. Test `/health` endpoint
3. Review [README.md](README.md) for detailed docs
4. Verify all dependencies are installed

---

**You're ready to go! 🚀**