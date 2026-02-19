# Jeeves Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                           Jeeves                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐          │
│  │   Gmail     │    │   Email     │    │   Response  │          │
│  │   Client    │───▶│   Watcher   │───▶│   Generator │          │
│  └─────────────┘    └─────────────┘    └──────┬──────┘          │
│         │                                     │                  │
│         │              ┌─────────────┐        │                  │
│         │              │     RAG     │◀───────┤                  │
│         │              │  Pipeline   │        │                  │
│         │              └──────┬──────┘        │                  │
│         │                     │               │                  │
│         ▼                     ▼               ▼                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐          │
│  │  Database   │    │  ChromaDB   │    │    LLM      │          │
│  │  (SQLite)   │    │  (Vectors)  │    │  (Ollama)   │          │
│  └─────────────┘    └─────────────┘    └─────────────┘          │
│                                                                  │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐          │
│  │  Dashboard  │    │  Confidence │    │  Notifier   │          │
│  │  (Gradio)   │    │   Scorer    │    │  (ntfy.sh)  │          │
│  └─────────────┘    └─────────────┘    └─────────────┘          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Components

### Core Modules (src/)

| Module | Purpose | Status |
|--------|---------|--------|
| `gmail_client.py` | Gmail API wrapper for OAuth, reading, and sending emails | ✅ Implemented |
| `ingest.py` | Email ingestion from mbox files | ✅ Implemented |
| `llm.py` | Ollama LLM wrapper for generating responses | 🔜 Planned |
| `rag.py` | ChromaDB RAG pipeline for style matching | 🔜 Planned |
| `response_generator.py` | Draft generation combining LLM and RAG | 🔜 Planned |

### Automation Modules

| Module | Purpose | Status |
|--------|---------|--------|
| `watcher.py` | Email polling service | 🔜 Planned |
| `confidence.py` | Confidence scoring for draft quality | 🔜 Planned |
| `db.py` | SQLite database layer | 🔜 Planned |
| `notifier.py` | Push notifications via ntfy.sh | 🔜 Planned |

### Interface Modules

| Module | Purpose | Status |
|--------|---------|--------|
| `dashboard.py` | Gradio web UI for draft review | 🔜 Planned |

### Utility Modules

| Module | Purpose | Status |
|--------|---------|--------|
| `logger.py` | Structured logging with structlog | 🔜 Planned |
| `metrics.py` | Metrics collection | 🔜 Planned |
| `security.py` | Security utilities | 🔜 Planned |

## Data Flow

### Email Processing Flow

```
1. Email Watcher polls Gmail (every 5 min)
   │
   ▼
2. Filter: skip spam, promotional, noreply
   │
   ▼
3. Store email in Database
   │
   ▼
4. RAG: find similar past emails
   │
   ▼
5. LLM: generate draft response
   │
   ▼
6. Confidence Scorer: rate draft quality
   │
   ├── High confidence + low risk → Auto-send (optional)
   │
   └── Medium/Low confidence → Queue for review
   │
   ▼
7. Notifier: push notification
   │
   ▼
8. Dashboard: user reviews/approves
   │
   ▼
9. Gmail Client: send approved draft
```

### Style Learning Flow

```
1. Ingest: parse mbox file
   │
   ▼
2. Extract: sent emails only
   │
   ▼
3. Embed: create vector embeddings
   │
   ▼
4. Index: store in ChromaDB
   │
   ▼
5. Query: find similar emails for context
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama API URL |
| `DEFAULT_MODEL` | `mistral:7b-instruct` | LLM model |
| `EMBEDDING_MODEL` | `BAAI/bge-base-en-v1.5` | Embedding model (future) |
| `POLL_INTERVAL` | `300` | Email poll interval in seconds (future) |
| `AUTO_SEND_THRESHOLD` | `0.9` | Confidence threshold for auto-send (future) |
| `NTFY_TOPIC` | `jeeves-drafts` | ntfy.sh topic for notifications (future) |
| `LOG_LEVEL` | `INFO` | Logging level |
| `DATA_DIR` | `./data` | Data directory |
| `MODELS_DIR` | `./models` | Models directory |

### Gmail OAuth Variables

| Variable | Description |
|----------|-------------|
| `GDOCS_CLIENT_ID` | OAuth client ID from Google Cloud Console |
| `GDOCS_CLIENT_SECRET` | OAuth client secret |
| `GDOCS_REFRESH_TOKEN` | Long-lived refresh token for API access |

## Database Schema

```sql
-- Emails table
CREATE TABLE emails (
    id INTEGER PRIMARY KEY,
    thread_id TEXT,
    message_id TEXT UNIQUE,
    sender TEXT,
    recipient TEXT,
    subject TEXT,
    body_text TEXT,
    body_html TEXT,
    received_at TEXT,
    processed INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Drafts table
CREATE TABLE drafts (
    id INTEGER PRIMARY KEY,
    email_id INTEGER,
    generated_text TEXT,
    tone TEXT,
    status TEXT DEFAULT 'pending',
    confidence REAL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT,
    sent_at TEXT,
    FOREIGN KEY (email_id) REFERENCES emails(id)
);
```

## Performance

### Benchmarks (Projected)

| Operation | Time | Memory |
|-----------|------|--------|
| Email ingestion (1000 emails) | ~30s | ~200MB |
| RAG indexing (1000 emails) | ~2min | ~500MB |
| Draft generation | ~3-5s | ~100MB |
| Dashboard load | <1s | ~50MB |

### Optimization Tips

1. Use SSD for ChromaDB storage
2. Allocate 8GB+ RAM for Ollama
3. Use GPU for faster LLM inference
4. Increase batch size for bulk ingestion

## Security

For security architecture and best practices, see [SECURITY.md](SECURITY.md).

### Key Security Principles

- **Local Processing** — All LLM inference happens on your machine
- **OAuth Only** — No password storage, tokens are encrypted
- **Data Isolation** — Email}