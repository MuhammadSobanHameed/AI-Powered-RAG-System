# Design Decisions & Trade-offs

This document explains the key architectural decisions, their rationale, and associated trade-offs.

## 1. Agent Architecture

### Decision: Three Separate Agents
**Chosen:** Ingestion Agent, Indexing Agent, QA Agent

**Rationale:**
- **Clear separation of concerns**: Each agent has a single, well-defined responsibility
- **Independent testing**: Agents can be tested in isolation
- **Easier debugging**: Failures can be traced to specific agents
- **Future extensibility**: New agents (e.g., Summarization Agent) can be added without modifying existing ones

**Trade-offs:**
- ✅ **Pro**: Clean, maintainable architecture
- ✅ **Pro**: Easy to understand and explain
- ❌ **Con**: Slight overhead in function calls
- ❌ **Con**: More files to maintain

**Alternative Considered:** Single monolithic service
- Rejected because it would create tight coupling and make testing harder

---

## 2. Synchronous vs Async Processing

### Decision: Synchronous Processing
**Chosen:** Upload endpoint waits for complete processing before returning

**Rationale:**
- **Simplicity**: Easier to implement and debug
- **User feedback**: User gets immediate confirmation of success/failure
- **Scope alignment**: Task focuses on architecture, not production optimizations
- **Time constraint**: 30-hour deadline favors working solution over perfect solution

**Trade-offs:**
- ✅ **Pro**: Simpler error handling
- ✅ **Pro**: No need for job queue infrastructure
- ✅ **Pro**: User knows document is ready immediately
- ❌ **Con**: Large documents block API response
- ❌ **Con**: Not scalable for high throughput
- ❌ **Con**: Poor UX for slow processing

**Future Enhancement:** 
```python
# Async with Celery
@app.post("/documents/upload")
async def upload(file):
    task = process_document.delay(file)
    return {"task_id": task.id, "status": "processing"}

@app.get("/documents/status/{task_id}")
async def status(task_id):
    result = AsyncResult(task_id)
    return {"status": result.state}
```

---

## 3. Vector Database: FAISS

### Decision: Local FAISS Index
**Chosen:** FAISS IndexFlatL2 with file persistence

**Rationale:**
- **Zero external dependencies**: Runs locally without cloud services
- **Fast**: ~1ms for similarity search on 10K vectors
- **Cost-free**: No API charges
- **Sufficient for scope**: Handles expected document volume
- **Easy to upgrade**: Can swap with Pinecone later

**Trade-offs:**
- ✅ **Pro**: No API keys needed
- ✅ **Pro**: Fast local search
- ✅ **Pro**: Complete control over data
- ❌ **Con**: Manual persistence required
- ❌ **Con**: No distributed indexing
- ❌ **Con**: Limited to single machine RAM

**Alternatives Considered:**
- **Pinecone**: More scalable but requires API key and costs money
- **Weaviate**: More features but adds complexity
- **Chroma**: Good option but FAISS is more battle-tested

**Upgrade Path:**
```python
# Later: Swap FAISS with Pinecone
from pinecone import Pinecone
pc = Pinecone(api_key=settings.PINECONE_API_KEY)
index = pc.Index("documents")
index.upsert(vectors=embeddings, ids=chunk_ids)
```

---

## 4. Embedding Model: Sentence Transformers

### Decision: `all-MiniLM-L6-v2`
**Chosen:** Local Sentence Transformer model

**Rationale:**
- **Local execution**: No API calls, zero latency
- **Cost-free**: No per-request charges
- **Fast**: ~50ms per embedding
- **Good quality**: 384 dimensions, trained on 1B+ pairs
- **Privacy**: Data never leaves server

**Trade-offs:**
- ✅ **Pro**: No API costs
- ✅ **Pro**: Predictable performance
- ✅ **Pro**: Works offline
- ❌ **Con**: Requires local GPU/CPU compute
- ❌ **Con**: Slightly lower quality than OpenAI embeddings

**Alternatives Considered:**
- **OpenAI embeddings**: Better quality but costs $0.0001/1K tokens
- **Cohere embeddings**: Good but requires API key
- **BERT base**: Slower and larger

**Why This Model:**
- Small (80MB)
- Fast (50ms/text)
- Good quality (cosine similarity: 0.85+ for relevant pairs)
- Well-tested (10M+ downloads)

---

## 5. LLM: Groq LLaMA

### Decision: Groq Cloud with LLaMA 3
**Chosen:** Groq's hosted LLaMA 3 (8B parameters)

**Rationale:**
- **Speed**: <1 second inference time
- **Quality**: LLaMA 3 is highly capable
- **Free tier**: Generous limits for development
- **Simple API**: Similar to OpenAI
- **No local GPU needed**: Cloud-hosted

**Trade-offs:**
- ✅ **Pro**: Fast responses
- ✅ **Pro**: High quality answers
- ✅ **Pro**: Easy to integrate
- ❌ **Con**: External dependency
- ❌ **Con**: Rate limits on free tier
- ❌ **Con**: Data leaves server

**Alternatives Considered:**
- **OpenAI GPT-4**: More expensive, slower
- **Ollama (local)**: Privacy-first but requires GPU and slower
- **Anthropic Claude**: Good but more expensive

**Why Groq:**
- Blazingly fast (500+ tokens/sec)
- Free tier is generous
- LLaMA 3 quality is excellent for this task

---

## 6. Database: SQLite

### Decision: SQLite for Metadata
**Chosen:** Local SQLite database

**Rationale:**
- **Zero configuration**: No setup needed
- **File-based**: Easy backup and portability
- **Sufficient for scope**: Handles expected load
- **Simple**: No connection pooling complexity
- **SQLAlchemy ORM**: Easy to upgrade to PostgreSQL later

**Trade-offs:**
- ✅ **Pro**: No setup required
- ✅ **Pro**: Easy to develop with
- ✅ **Pro**: Perfect for single instance
- ❌ **Con**: Limited concurrent writes
- ❌ **Con**: No network access
- ❌ **Con**: Not suitable for multi-instance deployment

**When to Upgrade to PostgreSQL:**
```python
# Just change the connection string
DATABASE_URL = "postgresql://user:pass@localhost/docdb"
# All SQLAlchemy code remains the same
```

**Upgrade Triggers:**
- Multiple API instances needed
- Write contention issues
- Need for advanced queries
- Production deployment

---

## 7. Chunking Strategy

### Decision: Fixed-size with Overlap
**Chosen:** 500 characters with 50 character overlap

**Rationale:**
- **Preserves context**: Overlap prevents cutting sentences
- **Manageable size**: Fits in LLM context easily
- **Consistent**: Predictable chunk count
- **Well-tested**: Industry standard approach

**Trade-offs:**
- ✅ **Pro**: Simple to implement
- ✅ **Pro**: Consistent behavior
- ✅ **Pro**: Good for most documents
- ❌ **Con**: May split important passages
- ❌ **Con**: Not semantic
- ❌ **Con**: Fixed size ignores structure

**Alternatives Considered:**
- **Sentence-based**: Better semantic boundaries but variable size
- **Paragraph-based**: Best for structured docs but fails on unstructured
- **Semantic chunking**: Best quality but requires extra model

**Future Enhancement:**
```python
# Recursive semantic chunking
def semantic_chunk(text, model):
    # Split by paragraphs first
    # Then by sentences
    # Then by fixed size if needed
    pass
```

---

## 8. Error Handling Strategy

### Decision: Fail Fast with Clear Messages
**Chosen:** Validate early, fail explicitly, return detailed errors

**Rationale:**
- **User clarity**: Users know exactly what went wrong
- **Debugging**: Logs contain full context
- **Safety**: Invalid input rejected early
- **Reliability**: No silent failures

**Implementation:**
```python
# Validate at multiple levels
1. API layer: File type, size
2. Agent layer: Content validity
3. Service layer: Operation success
```

**Trade-offs:**
- ✅ **Pro**: Clear error messages
- ✅ **Pro**: Easy to debug
- ✅ **Pro**: Safe behavior
- ❌ **Con**: More validation code
- ❌ **Con**: Slightly verbose

---

## 9. File Storage

### Decision: Local Filesystem
**Chosen:** Store files in `storage/uploads/`

**Rationale:**
- **Simple**: No cloud service needed
- **Fast**: Direct filesystem access
- **Cost-free**: No storage charges
- **Aligned with scope**: Local deployment assumption

**Trade-offs:**
- ✅ **Pro**: Zero complexity
- ✅ **Pro**: Fast access
- ✅ **Pro**: No external dependencies
- ❌ **Con**: Not distributed
- ❌ **Con**: No automatic backups
- ❌ **Con**: Not scalable to multi-instance

**Production Path:**
```python
# Upgrade to S3
import boto3
s3 = boto3.client('s3')
s3.upload_file(file_path, bucket, key)
```

---

## 10. API Design

### Decision: RESTful with Clear Contracts
**Chosen:** 
- `POST /documents/upload` → Upload document
- `POST /documents/ask` → Ask question
- Pydantic models for validation

**Rationale:**
- **Standard**: REST is widely understood
- **Self-documenting**: FastAPI generates OpenAPI docs
- **Type-safe**: Pydantic ensures valid input
- **Simple**: Only two main endpoints needed

**Trade-offs:**
- ✅ **Pro**: Easy to understand
- ✅ **Pro**: Automatic documentation
- ✅ **Pro**: Type validation
- ❌ **Con**: Could add GraphQL for flexibility
- ❌ **Con**: No batch operations

---

## Summary of Key Trade-offs

| Decision | Favored | Sacrificed |
|----------|---------|------------|
| **Synchronous** | Simplicity | Scalability |
| **Local FAISS** | Zero cost | Distributed search |
| **SQLite** | Easy setup | Concurrent writes |
| **Sentence Transformers** | Free + Fast | Slight quality |
| **Fixed chunking** | Simplicity | Semantic awareness |
| **Local storage** | No dependencies | Multi-instance |

## Guiding Principles

1. **Clarity over cleverness**: Simple, understandable code
2. **Working over perfect**: Functional system within time constraint
3. **Extensible over complete**: Easy to upgrade later
4. **Explicit over implicit**: Clear error messages and flow
5. **Testable over monolithic**: Isolated components

## Future Improvements Roadmap

### Phase 1: Production Ready (1-2 weeks)
- [ ] Async processing with Celery
- [ ] PostgreSQL migration
- [ ] Authentication & authorization
- [ ] Comprehensive error handling
- [ ] Structured logging

### Phase 2: Enhanced Features (2-4 weeks)
- [ ] Multi-document QA
- [ ] Document similarity search
- [ ] Query caching
- [ ] Support more file types (DOCX, TXT)
- [ ] Batch upload

### Phase 3: Scalability (1-2 months)
- [ ] Pinecone/Weaviate integration
- [ ] Load balancing
- [ ] Distributed processing
- [ ] S3 storage
- [ ] Redis caching

---

**These decisions prioritize demonstrating system design skills and architectural thinking over premature optimization.**