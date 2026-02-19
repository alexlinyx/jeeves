# Contributing to Jeeves

Thank you for your interest in contributing to Jeeves!

## Development Setup

```bash
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
```

## Project Structure

```
jeeves/
├── src/              # Main source code
│   ├── __init__.py
│   ├── gmail_client.py   # Gmail API wrapper
│   ├── ingest.py         # Email ingestion from mbox
│   ├── llm.py            # Ollama LLM wrapper (planned)
│   ├── rag.py            # ChromaDB RAG pipeline (planned)
│   ├── response_generator.py  # Draft generation (planned)
│   ├── watcher.py        # Email polling service (planned)
│   ├── confidence.py     # Confidence scoring (planned)
│   ├── db.py             # SQLite database layer (planned)
│   ├── dashboard.py      # Gradio web UI (planned)
│   ├── notifier.py       # Push notifications (planned)
│   ├── logger.py         # Structured logging (planned)
│   ├── metrics.py        # Metrics collection (planned)
│   └── security.py       # Security utilities (planned)
├── tests/            # Test files
├── data/             # Data files (gitignored)
├── logs/             # Log files (gitignored)
├── docs/             # Documentation
├── requirements.txt  # Production dependencies
├── requirements-dev.txt  # Development dependencies
└── .env.example      # Environment variables template
```

## Branch Naming

- `feature/X.Y-description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring

## Commit Messages

Follow conventional commits:

```
feat: add new feature
fix: fix bug in X
docs: update documentation
refactor: restructure X
test: add tests for X
```

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