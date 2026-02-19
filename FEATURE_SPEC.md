# Feature Spec: Documentation

**Phase:** 5.3  
**Branch:** `feature/5.3-documentation`  
**Priority:** P2  
**Est. Time:** 6 hours

---

## Objective

Create comprehensive documentation for users and developers to understand, install, configure, and extend Jeeves.

---

## Acceptance Criteria

- [ ] `README.md` complete with install + usage
- [ ] `ARCHITECTURE.md` documents system design
- [ ] `CONTRIBUTING.md` for contributors
- [ ] `CHANGELOG.md` for version history
- [ ] API documentation for all modules
- [ ] Configuration guide
- [ ] Troubleshooting guide
- [ ] Demo video recorded
- [ ] New developer can set up in <30 min

---

## Deliverable

### `README.md`

```markdown
# Jeeves - AI Email Assistant

Jeeves is an AI-powered email assistant that learns your writing style and drafts responses automatically.

## Features

- 🤖 **AI-Powered Responses** - Uses local LLM (Ollama) to generate contextual replies
- 📚 **Style Learning** - Learns from your past emails to match your writing style
- 🎨 **Multiple Tones** - Casual, formal, concise, or style-match modes
- 🔒 **Privacy First** - All processing happens locally, no data leaves your machine
- 📊 **Review Dashboard** - Gradio UI to review and edit drafts before sending
- 🔔 **Push Notifications** - Get notified when new drafts are ready

## Quick Start

### Prerequisites

- Python 3.11+
- Ollama (for local LLM)
- Gmail account with API access

### Installation

\`\`\`bash
# Clone the repository
git clone https://github.com/alexlinyx/jeeves.git
cd jeeves

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Install Ollama and download model
# See: https://ollama.ai
ollama pull mistral:7b-instruct

# Set up Gmail OAuth
# See: docs/gmail-setup.md
\`\`\`

### Configuration

\`\`\`bash
# Copy example config
cp .env.example .env

# Edit with your settings
nano .env
\`\`\`

Required environment variables:

\`\`\`
GMAIL_CREDENTIALS_PATH=data/credentials.json
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral:7b-instruct
\`\`\`

### Run

\`\`\`bash
# Ingest your email history (one-time)
python -m src.ingest --mbox ~/Downloads/takeout.mbox --user-email you@example.com

# Start the dashboard
python -m src.dashboard

# Or run in background with email watcher
python -m src.watcher
\`\`\`

## Usage

### Dashboard

Open http://localhost:7860 to access the Gradio dashboard.

1. View pending drafts in the table
2. Select a draft to review
3. Edit the draft text if needed
4. Choose a tone (casual/formal/concise/match_style)
5. Click Approve to send, or Delete to discard

### Tone Modes

| Mode | Description |
|------|-------------|
| `casual` | Friendly, conversational, uses contractions |
| `formal` | Professional, proper grammar, polite |
| `concise` | Brief, to-the-point, minimal fluff |
| `match_style` | Mimics your writing style from past emails |

### Notifications

Set up push notifications via ntfy.sh:

\`\`\`bash
# Set your topic in .env
NTFY_TOPIC=your-unique-topic

# Subscribe on your phone
# iOS: https://apps.apple.com/app/ntfy
# Android: https://play.google.com/store/apps/details?id=io.heckel.ntfy
\`\`\`

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for system design.

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## License

MIT License - see [LICENSE](LICENSE)
```

### `ARCHITECTURE.md`

```markdown
# Jeeves Architecture

## System Overview

\`\`\`
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
\`\`\`

## Components

### Core Modules

| Module | Purpose | Dependencies |
|--------|---------|--------------|
| `gmail_client.py` | Gmail API wrapper | google-api-python-client |
| `ingest.py` | Email ingestion from mbox | mailbox |
| `llm.py` | Ollama LLM wrapper | requests |
| `rag.py` | ChromaDB RAG pipeline | chromadb, sentence-transformers |
| `response_generator.py` | Draft generation | llm, rag |

### Automation Modules

| Module | Purpose | Dependencies |
|--------|---------|--------------|
| `watcher.py` | Email polling service | gmail_client, response_generator |
| `confidence.py` | Confidence scoring | rag |
| `db.py` | SQLite database layer | sqlite3 |
| `notifier.py` | Push notifications | requests |

### Interface Modules

| Module | Purpose | Dependencies |
|--------|---------|--------------|
| `dashboard.py` | Gradio web UI | gradio, db |

### Utility Modules

| Module | Purpose | Dependencies |
|--------|---------|--------------|
| `logger.py` | Structured logging | structlog |
| `metrics.py` | Metrics collection | - |
| `security.py` | Security utilities | - |

## Data Flow

### Email Processing Flow

\`\`\`
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
\`\`\`

### Style Learning Flow

\`\`\`
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
\`\`\`

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GMAIL_CREDENTIALS_PATH` | `data/credentials.json` | OAuth credentials |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama API URL |
| `OLLAMA_MODEL` | `mistral:7b-instruct` | LLM model |
| `EMBEDDING_MODEL` | `BAAI/bge-base-en-v1.5` | Embedding model |
| `POLL_INTERVAL` | `300` | Email poll interval (seconds) |
| `AUTO_SEND_THRESHOLD` | `0.9` | Confidence threshold for auto-send |
| `NTFY_TOPIC` | `jeeves-drafts` | ntfy.sh topic |

### Database Schema

\`\`\`sql
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
\`\`\`

## Security

See [SECURITY.md](SECURITY.md) for security architecture.

## Performance

### Benchmarks

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
```

### `CONTRIBUTING.md`

```markdown
# Contributing to Jeeves

Thank you for your interest in contributing to Jeeves!

## Development Setup

\`\`\`bash
# Clone and set up
git clone https://github.com/alexlinyx/jeeves.git
cd jeeves
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v

# Run linting
ruff check src/
black --check src/
\`\`\`

## Project Structure

\`\`\`
jeeves/
├── src/              # Main source code
│   ├── gmail_client.py
│   ├── ingest.py
│   ├── llm.py
│   ├── rag.py
│   ├── response_generator.py
│   ├── watcher.py
│   ├── confidence.py
│   ├── db.py
│   ├── dashboard.py
│   ├── notifier.py
│   ├── logger.py
│   ├── metrics.py
│   └── security.py
├── tests/            # Test files
├── data/             # Data files (gitignored)
├── logs/             # Log files (gitignored)
├── docs/             # Documentation
└── requirements.txt
\`\`\`

## Branch Naming

- `feature/X.Y-description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring

## Commit Messages

Follow conventional commits:

\`\`\`
feat: add new feature
fix: fix bug in X
docs: update documentation
refactor: restructure X
test: add tests for X
\`\`\`

## Pull Request Process

1. Create feature branch from `master`
2. Make changes with tests
3. Run tests: `pytest tests/ -v`
4. Run linting: `ruff check src/`
5. Update documentation if needed
6. Create PR with description
7. Wait for review

## Code Style

- Use type hints
- Write docstrings
- Keep functions <50 lines
- Keep files <500 lines
- Follow PEP 8

## Testing

- Write unit tests for new code
- Maintain 80%+ coverage
- Use pytest fixtures
- Mock external services
```

### `CHANGELOG.md`

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial implementation

## [0.1.0] - 2024-XX-XX

### Added
- Gmail OAuth integration
- Email ingestion from mbox
- LLM wrapper for Ollama
- RAG pipeline with ChromaDB
- Response generator with tone modes
- Gradio dashboard
- SQLite database layer
- Push notifications
- Email watcher service
- Confidence scoring
- Monitoring and logging
- Security hardening
```

---

## Tasks

### 5.3.1 Write README.md (1.5 hrs)
- [ ] Quick start guide
- [ ] Installation instructions
- [ ] Configuration guide
- [ ] Usage examples
- [ ] Feature overview

### 5.3.2 Write ARCHITECTURE.md (1.5 hrs)
- [ ] System overview diagram
- [ ] Component descriptions
- [ ] Data flow diagrams
- [ ] Database schema
- [ ] Configuration reference

### 5.3.3 Write CONTRIBUTING.md (1 hr)
- [ ] Development setup
- [ ] Project structure
- [ ] Branch naming
- [ ] Commit conventions
- [ ] PR process
- [ ] Code style

### 5.3.4 API Documentation (1 hr)
- [ ] Document all modules
- [ ] Document all classes
- [ ] Document all methods
- [ ] Add usage examples

### 5.3.5 Demo Video (1 hr)
- [ ] Record 2-3 minute demo
- [ ] Show installation
- [ ] Show dashboard
- [ ] Show draft generation
- [ ] Upload to YouTube

---

## Definition of Done

1. `README.md` complete with install + usage
2. `ARCHITECTURE.md` documents system design
3. `CONTRIBUTING.md` for contributors
4. `CHANGELOG.md` for version history
5. API documentation for all modules
6. Configuration guide in README
7. Troubleshooting section in README
8. Demo video recorded
9. New developer can set up in <30 min
10. Branch pushed to GitHub
11. PR created