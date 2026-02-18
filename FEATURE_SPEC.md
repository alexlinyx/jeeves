# Feature Spec: Environment Setup

**Phase:** 1.1  
**Branch:** `feature/1.1-environment-setup`  
**Priority:** P0 (Blocking)  
**Est. Time:** 4 hours

---

## Objective

Set up the Python project structure and dependencies for the Jeeves email agent.

---

## Acceptance Criteria

- [ ] Python 3.10+ virtual environment created
- [ ] `requirements.txt` with all core dependencies
- [ ] `.env.example` file with required environment variables
- [ ] `src/` directory structure created
- [ ] `python -m pip install -r requirements.txt` succeeds
- [ ] `python -c "import src"` succeeds

---

## Files to Create

### 1. `requirements.txt`
```
# Core
python-dotenv>=1.0.0

# Gmail & OAuth
google-auth-oauthlib>=1.2.0
google-auth-httplib2>=0.2.0
google-api-python-client>=2.100.0

# Email Processing
html2text>=2020.1.16

# ML/AI
torch>=2.0.0
transformers>=4.35.0
datasets>=2.14.0
peft>=0.7.0
accelerate>=0.24.0

# Local LLM
# ollama (install separately: curl -fsSL https://ollama.com/install.sh | sh)

# Vector DB
chromadb>=0.4.0
sentence-transformers>=2.2.0

# RAG & Agents
langchain>=0.1.0
langchain-community>=0.0.10
llama-index>=0.9.0
llama-index-embeddings-huggingface>=0.1.0

# UI
gradio>=4.0.0
fastapi>=0.104.0
uvicorn>=0.24.0

# Data
pandas>=2.0.0
pyarrow>=14.0.0

# Utils
structlog>=23.0.0
keyring>=24.0.0
requests>=2.31.0

# Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
```

### 2. `.env.example`
```
# Google OAuth
GDOCS_CLIENT_ID=your-client-id.apps.googleusercontent.com
GDOCS_CLIENT_SECRET=your-client-secret
GDOCS_REFRESH_TOKEN=your-refresh-token

# AWS (for secrets)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_DEFAULT_REGION=us-east-1

# LLM
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=mistral:7b-instruct

# App
LOG_LEVEL=INFO
DATA_DIR=./data
MODELS_DIR=./models
```

### 3. `src/__init__.py`
```python
"""
Jeeves - AI Email Assistant

An email agent that learns your writing style and drafts responses.
"""

__version__ = "0.1.0"
```

### 4. Directory Structure
```
jeeves/
├── src/
│   └── __init__.py
├── tests/
│   └── __init__.py
├── data/
│   └── .gitkeep
├── models/
│   └── .gitkeep
├── logs/
│   └── .gitkeep
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md (update if needed)
```

### 5. `.gitignore`
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
ENV/
env/
.venv/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Environment
.env
.env.local

# Data (keep structure, ignore content)
data/*.csv
data/*.db
data/*.mbox
!data/.gitkeep

# Models (keep structure, ignore content)
models/*.gguf
models/*.bin
!models/.gitkeep

# Logs
logs/*.log
logs/*.jsonl
!logs/.gitkeep

# Testing
.pytest_cache/
.coverage
htmlcov/

# OS
.DS_Store
Thumbs.db
```

---

## Testing

After implementation:
```bash
# Create and activate venv
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify import
python -c "import src; print('OK')"

# Run tests (placeholder)
pytest tests/ -v
```

---

## Notes

- `ollama` must be installed separately (system package)
- GPU dependencies (bitsandbytes) are optional for CPU-only setups
- `.env` file should NEVER be committed

---

## Definition of Done

1. All files created as specified
2. `pip install -r requirements.txt` completes without errors
3. `python -c "import src"` runs successfully
4. Branch pushed to GitHub
5. PR created with description matching this spec
