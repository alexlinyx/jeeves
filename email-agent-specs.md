# Email Auto-Responder Agent — Technical Specification

## Overview
AI-powered email assistant that learns your writing style and drafts responses for your review.

## Architecture Workflow

```
[User OAuth] → [Ingest History] → [Train Model] → [Process New] → [Draft Reply] → [User Review] → [Send]
     ↓              ↓                ↓              ↓              ↓            ↓          ↓
   gog/          IMAP/API       LLMMe +        LangChain      Gmail API      Web UI    Gmail API
   Google         + mbox        LoRA/QLoRA     + Ollama       Drafts         (gradio)  Send
   OAuth
```

---

## Step 1: Gmail OAuth Connection

### Purpose
Authenticate and authorize access to user's Gmail account.

### Open Source Stack
| Component | Package | Purpose |
|-----------|---------|---------|
| OAuth Flow | `google-auth-oauthlib` | Google OAuth 2.0 flow |
| Token Storage | `keyring` | Secure credential storage |
| API Client | `google-api-python-client` | Gmail API wrapper |
| Alternative | `gog` (existing) | Already configured in your setup |

**Recommended:** Use existing `gog` CLI (already authenticated) via:
```bash
export GOG_KEYRING_PASSWORD=...
gog gmail search "newer_than:30d"
```

### Data Retrieved
- OAuth refresh token (long-lived)
- Scope: `gmail.readonly`, `gmail.modify`, `gmail.compose`

---

## Step 2: Email Ingestion

### Purpose
Download email history for training data.

### Open Source Stack
| Component | Package | Purpose |
|-----------|---------|---------|
| IMAP Client | `imaplib` (stdlib) | Alternative to Gmail API |
| mbox Parser | `mailbox` (stdlib) | Parse Gmail Takeout exports |
| Email Parsing | `email` (stdlib) | Extract headers, body, attachments |
| HTML to Text | `html2text` | Clean HTML emails |
| Progress Bar | `tqdm` | Show ingestion progress |

### Data Extraction
```python
# Schema per email
{
  "message_id": "<unique-id@example.com>",
  "thread_id": "thread-123",
  "timestamp": "2026-01-15T09:30:00Z",
  "from": "sender@example.com",
  "to": ["you@gmail.com"],
  "cc": [],
  "subject": "Project Update",
  "body_text": "plain text content",
  "body_html": "<html>...</html>",
  "is_reply": true,
  "in_reply_to": "<parent-msg-id@example.com>",
  "references": ["<thread-root@example.com>"],
  "labels": ["INBOX", "IMPORTANT"],
  "sent_by_you": false
}
```

### Storage
- **Local SQLite** for metadata indexing
- **Local filesystem** for raw mbox files
- **ChromaDB** (vector store) for semantic search

---

## Step 3: LLM Training (Writing Style)

### Purpose
Fine-tune a model to write like the user in different modes.

### Open Source Stack
| Component | Package | Purpose |
|-----------|---------|---------|
| Training Framework | `trl` (Transformers Reinforcement Learning) | Fine-tuning utilities |
| PEFT | `peft` | LoRA/QLoRA for efficient training |
| Dataset Processing | `datasets` (Hugging Face) | Data loading and preprocessing |
| Local LLM | `ollama` | Run models locally |
| GGUF Conversion | `llama.cpp` | Quantize for local inference |
| Alternative | `h2o-llmstudio` | LLMMe's recommended tool |
| Alternative | `axolotl` | YAML-configured training |
| Alternative | `unsloth` | 2x faster training, less memory |

### Training Pipeline

#### 3a. Dataset Preparation
```python
# Convert emails to instruction-following format
{
  "instruction": "Reply to this email in a casual, friendly tone.",
  "input": "Email: Hey, can we reschedule our meeting to Thursday?",
  "output": "No worries at all! Thursday works perfectly for me. How about 2pm?"
}
```

**Tools:**
- `pandas` — Data manipulation
- `sklearn` — Train/test split
- `jinja2` — Prompt templating

#### 3b. Training Modes
| Mode | Description | Training Data Filter |
|------|-------------|---------------------|
| **Personal** | Your actual writing style | All your sent emails |
| **Casual** | Relaxed, conversational | Personal emails only (friends, family) |
| **Formal** | Professional, business | Work emails, formal correspondence |
| **Concise** | Brief, to-the-point | Short replies < 50 words |
| **Detailed** | Thorough explanations | Long replies with context |

#### 3c. Base Models (Open Source)
| Model | Size | Best For |
|-------|------|----------|
| `mistralai/Mistral-7B-Instruct-v0.3` | 7B | Good balance quality/speed |
| `meta-llama/Llama-3.1-8B-Instruct` | 8B | Strong instruction following |
| `Qwen/Qwen2.5-7B-Instruct` | 7B | Multilingual, efficient |
| `microsoft/Phi-3-mini-4k-instruct` | 3.8B | Fast, edge devices |

#### 3d. Training Config (LoRA)
```yaml
# LoRA for efficient fine-tuning
method: lora
r: 16                    # LoRA rank
lora_alpha: 32          # Scaling factor
target_modules: ["q_proj", "v_proj", "k_proj", "o_proj"]
learning_rate: 2e-4
epochs: 3
batch_size: 4
gradient_accumulation_steps: 4
quantization: 4bit      # QLoRA for GPU efficiency
```

**Tools:**
- `bitsandbytes` — 4-bit quantization
- `accelerate` — Multi-GPU training
- `wandb` or `tensorboard` — Training metrics

#### 3e. Model Storage
- **Local path:** `~/.email-agent/models/{mode}/`
- **Format:** GGUF for fast inference
- **Size:** ~4-8GB per model (quantized)

---

## Step 4: Message Processing

### Purpose
Classify incoming emails and generate context-aware responses.

### Open Source Stack
| Component | Package | Purpose |
|-----------|---------|---------|
| LLM Framework | `langchain` or `langgraph` | Agent orchestration |
| RAG | `llama-index` | Retrieval from email history |
| Vector DB | `chromadb` | Local vector storage |
| Embeddings | `sentence-transformers` | Text embeddings |
| NER | `spaCy` | Named entity recognition |
| Classification | `transformers` | Zero-shot classification |

### Processing Pipeline

#### 4a. Intent Classification
```python
from transformers import pipeline

classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli"
)

intents = [
    "request_information",
    "schedule_meeting",
    "urgent_action_required",
    "newsletter_marketing",
    "personal_update",
    "introduction_networking"
]

result = classifier(email_body, intents)
# → {"labels": ["schedule_meeting", ...], "scores": [0.85, ...]}
```

**Alternative Models:**
- `joeddav/xlm-roberta-large-xnli` — Multilingual
- `MoritzLaurer/DeBERTa-v3-base-mnli-fever-docnli-ling-2c` — Better accuracy

#### 4b. Context Retrieval (RAG)
```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# Load previous emails
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")
index = VectorStoreIndex.from_documents(emails, embed_model=embed_model)

# Query similar emails
retriever = index.as_retriever(similarity_top_k=5)
context = retriever.retrieve(new_email_subject)
```

**Embeddings:**
- `BAAI/bge-base-en-v1.5` — Best for retrieval
- `sentence-transformers/all-MiniLM-L6-v2` — Fast, smaller
- `mixedbread-ai/mxbai-embed-large-v1` — High quality

#### 4c. Response Generation
```python
from langchain_community.llms import Ollama

# Load fine-tuned model
llm = Ollama(model="email-agent-formal:latest")

prompt = f"""You are writing an email reply. Tone: Formal business.

Context from similar past emails:
{retrieved_context}

Email to reply to:
From: {sender}
Subject: {subject}
Body: {body}

Draft a professional reply:"""

response = llm.invoke(prompt)
```

---

## Step 5: Draft Creation

### Purpose
Create Gmail draft with generated response.

### Open Source Stack
| Component | Package | Purpose |
|-----------|---------|---------|
| Gmail API | `google-api-python-client` | Create drafts |
| Email Compose | `email.mime` (stdlib) | Build email structure |
| HTML Generation | `jinja2` | Email templates |

### Draft API Call
```python
from googleapiclient.discovery import build

service = build('gmail', 'v1', credentials=creds)

# Create draft message
message = {
    'message': {
        'threadId': original_thread_id,
        'labelIds': ['DRAFT'],
        'payload': {
            'headers': [
                {'name': 'To', 'value': original_sender},
                {'name': 'From', 'value': 'you@gmail.com'},
                {'name': 'Subject', 'value': f"Re: {original_subject}"},
                {'name': 'In-Reply-To', 'value': original_message_id},
                {'name': 'References', 'value': original_references}
            ],
            'body': {
                'data': base64.urlsafe_b64encode(response_text.encode()).decode()
            }
        }
    }
}

draft = service.users().drafts().create(userId='me', body=message).execute()
# → draft['id'] for later use
```

**Alternative via gog:**
```bash
export GOG_KEYRING_PASSWORD=...
gog gmail drafts create --to sender@example.com \
  --subject "Re: Original Subject" \
  --body-file ./generated_reply.txt
```

---

## Step 6: User Review Interface

### Purpose
Present drafts to user for approval/editing.

### Open Source Stack
| Component | Package | Purpose |
|-----------|---------|---------|
| Web UI | `gradio` | Simple interface (what LLMMe uses) |
| Alternative | `streamlit` | More flexible, Python-native |
| Alternative | `nicegui` | Modern, Vue.js-based |
| API Server | `fastapi` | Backend for web UI |
| Real-time Updates | `websockets` or `sse-starlette` | Push new drafts |
| Notifications | `ntfy` or `gotify` | Mobile push notifications |

### UI Components

#### 6a. Dashboard (Gradio Example)
```python
import gradio as gr

def load_pending_drafts():
    return db.get_drafts(status="pending_review")

def approve_draft(draft_id):
    gmail_send(draft_id)
    return "Sent!"

def edit_draft(draft_id, new_text):
    gmail_update_draft(draft_id, new_text)
    return "Updated!"

with gr.Blocks() as demo:
    gr.Markdown("## Email Agent — Pending Drafts")
    
    drafts = gr.Dataframe(load_pending_drafts, every=30)
    
    with gr.Row():
        draft_text = gr.Textbox(label="Edit Draft", lines=10)
        approve_btn = gr.Button("Approve & Send")
        edit_btn = gr.Button("Update Draft")
    
    approve_btn.click(approve_draft, inputs=[draft_id], outputs=[status])
    edit_btn.click(edit_draft, inputs=[draft_id, draft_text], outputs=[status])

demo.launch()
```

#### 6b. Mobile Notifications
```python
# Using ntfy (self-hosted push notifications)
import requests

def notify_user(draft_id, subject, preview):
    requests.post("https://ntfy.sh/your-topic", 
        data=f"New draft: {subject}\n\n{preview[:100]}...".encode(),
        headers={
            "Title": "Email Agent",
            "Priority": "high",
            "Click": f"https://your-app.com/draft/{draft_id}"
        }
    )
```

#### 6c. Confidence-Based Routing
```python
if confidence > 0.9 and not is_sensitive(intent):
    # Auto-send, notify after
    send_email(draft_id)
    notify_user(f"Sent: {subject}")
elif confidence > 0.7:
    # One-tap approval
    notify_user(f"Approve: {subject}", action="approve")
else:
    # Full review required
    create_draft(draft_id)
    notify_user(f"Review: {subject}", priority="high")
```

---

## Step 7: Send Email (Optional)

### Purpose
Send approved drafts or auto-send high-confidence responses.

### Open Source Stack
| Component | Package | Purpose |
|-----------|---------|---------|
| Gmail API | `google-api-python-client` | Send emails |
| Rate Limiting | `ratelimit` or `slowapi` | Prevent spam |
| Logging | `structlog` or `loguru` | Audit trail |
| Analytics | `prometheus-client` | Metrics (optional) |

### Send Methods

#### 7a. Send Draft
```python
# Send existing draft
service.users().drafts().send(
    userId='me',
    body={'id': draft_id}
).execute()
```

#### 7b. Direct Send (No Draft)
```python
# For auto-send high confidence
message = MIMEText(body)
message['to'] = to_email
message['subject'] = subject
message['in-reply-to'] = original_msg_id

raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
service.users().messages().send(
    userId='me',
    body={'raw': raw, 'threadId': thread_id}
).execute()
```

#### 7c. Via gog CLI
```bash
gog gmail send \
  --to sender@example.com \
  --subject "Re: Original" \
  --reply-to-message-id "<original-id@example.com>" \
  --body-file ./reply.txt
```

---

## Data Storage Architecture

### Local-First Stack
| Data Type | Storage | Tool |
|-----------|---------|------|
| Email Metadata | SQLite | `sqlite3` |
| Email Content | Filesystem | `.mbox` or `.eml` files |
| Vector Embeddings | ChromaDB | `chromadb` |
| Fine-tuned Models | Filesystem | `~/.email-agent/models/` |
| Training Datasets | Parquet | `pyarrow` |
| Logs | SQLite or JSONL | `sqlite3` |

### Schema (SQLite)
```sql
-- Emails table
CREATE TABLE emails (
    id TEXT PRIMARY KEY,
    thread_id TEXT,
    timestamp DATETIME,
    sender TEXT,
    subject TEXT,
    body_preview TEXT,
    labels TEXT, -- JSON array
    is_sent BOOLEAN,
    embedding_id TEXT -- Foreign key to vector DB
);

-- Drafts table
CREATE TABLE drafts (
    id TEXT PRIMARY KEY,
    original_email_id TEXT,
    draft_gmail_id TEXT,
    generated_text TEXT,
    confidence_score FLOAT,
    mode TEXT, -- personal, casual, formal
    status TEXT, -- pending, approved, rejected, sent
    created_at DATETIME,
    FOREIGN KEY (original_email_id) REFERENCES emails(id)
);

-- Training runs
CREATE TABLE training_runs (
    id INTEGER PRIMARY KEY,
    mode TEXT,
    base_model TEXT,
    dataset_size INTEGER,
    epochs INTEGER,
    final_loss FLOAT,
    model_path TEXT,
    created_at DATETIME
);
```

---

## Security & Privacy

### Local-First Design
- **No cloud LLM by default** — Use Ollama locally
- **No email data leaves machine** — Vector DB is local
- **Encrypted at rest** — SQLite encryption with `sqlcipher`
- **Secure credential storage** — Use `keyring` or 1Password CLI

### Sensitive Data Handling
```python
# Auto-detect sensitive content
sensitive_patterns = [
    r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',  # Credit cards
    r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
    r'password[:\s]+\S+',  # Passwords
    r'api[_-]?key[:\s]+\S+',  # API keys
]

if any(re.search(pattern, email_body) for pattern in sensitive_patterns):
    require_manual_review = True
    log_security_event("Sensitive content detected")
```

---

## Deployment Options

### Option A: Desktop App (Recommended for MVP)
- **Stack:** Python + Gradio/Streamlit + Ollama
- **Pros:** Simple, local, no server needed
- **Cons:** Must keep computer on

### Option B: Self-Hosted Server
- **Stack:** FastAPI + Docker + GPU server
- **Pros:** Always-on, mobile access
- **Cons:** Infrastructure complexity

### Option C: Hybrid (Future)
- **Edge:** Lightweight classification on-device
- **Cloud:** Heavy LLM inference on GPU server
- **Sync:** End-to-end encrypted

---

## Complete Package List

### Core Dependencies
```txt
# Gmail & OAuth
google-auth-oauthlib
google-api-python-client
gog  # your existing tool

# Email Processing
html2text
tqdm

# ML/AI
torch
transformers
datasets
peft
bitsandbytes
accelerate
ollama
chromadb
sentence-transformers

# RAG & Agents
langchain
langchain-community
llama-index
llama-index-embeddings-huggingface

# Training (choose one)
# h2o-llmstudio  # or
# axolotl        # or
# unsloth

# UI
gradio
streamlit
fastapi
uvicorn

# Data
pandas
pyarrow
sqlcipher

# Utils
python-dotenv
structlog
keyring
requests
```

---

## Next Steps

1. **Validate OAuth flow** — Test gog integration
2. **Ingest sample data** — Download 1000 emails, verify parsing
3. **Build dataset converter** — mbox → training format
4. **Fine-tune small model** — Test with Phi-3-mini (3.8B)
5. **Build Gradio UI** — Draft review interface
6. **Integrate end-to-end** — Gmail → Model → Draft → UI

Want me to expand any section or start on implementation plan?