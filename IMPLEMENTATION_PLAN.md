# Email Auto-Responder Agent — Implementation Plan

**Project Owner:** Alyx  
**Tech Lead:** [TBD]  
**Start Date:** [TBD]  
**Target MVP:** 4-6 weeks  
**Risk Level:** Medium (AI/ML integration, OAuth complexity)

---

## Executive Summary

Build an AI-powered email assistant that:
1. Learns your writing style from email history
2. Drafts responses to new emails automatically
3. Presents drafts for review before sending
4. Supports multiple tones (casual, formal, concise)

**Tech Stack:** Python, Gmail API, Ollama (local LLM), LangChain, ChromaDB, Gradio

---

## Phase 1: Foundation (Week 1-2)

### 1.1 Environment Setup
| Task | Owner | Est. Time | Dependencies |
|------|-------|-----------|-------------|
| Create project repo (`email-agent`) | Tech Lead | 2 hrs | — |
| Set up Python virtualenv | Tech Lead | 1 hr | — |
| Install core dependencies (see `requirements.txt`) | Tech Lead | 2 hrs | — |
| Configure `.env` file (OAuth creds, API keys) | Tech Lead | 1 hr | — |
| **Milestone:** `python -m pip install -r requirements.txt` works |

### 1.2 Gmail OAuth Integration
| Task | Owner | Est. Time | Dependencies |
|------|-------|-----------|-------------|
| Enable Gmail API in Google Cloud Console | PM | 30 min | Google Cloud account |
| Create OAuth 2.0 credentials (Desktop app) | PM | 30 min | — |
| Store credentials in AWS Secrets Manager | Tech Lead | 1 hr | AWS access |
| Test `gog` CLI authentication | Tech Lead | 1 hr | Credentials stored |
| Build Python Gmail client wrapper | Eng | 4 hrs | `gog` working |
| **Milestone:** Can fetch last 10 emails via Python |

**Deliverable:** `src/gmail_client.py` with methods:
- `list_emails(limit=100)`
- `get_email(message_id)`
- `create_draft(thread_id, body)`
- `send_draft(draft_id)`

---

### 1.3 Email Ingestion Pipeline
| Task | Owner | Est. Time | Dependencies |
|------|-------|-----------|-------------|
| Export Gmail history via Google Takeout | PM | 2 hrs (wait time: 24-48 hrs) | — |
| Download `.mbox` file | PM | 30 min | Takeout ready |
| Build mbox parser script | Eng | 4 hrs | `mailbox` lib |
| Extract sent emails (for training data) | Eng | 4 hrs | Parser working |
| Save as CSV (prompt/response pairs) | Eng | 2 hrs | Extraction done |
| **Milestone:** `python src/ingest.py --mbox ~/Downloads/takeout.mbox` → `data/training_emails.csv` |

**Deliverable:** `src/ingest.py` producing:
```csv
thread_id,from,subject,body_text,sent_by_you,timestamp
...
```

---

## Phase 2: AI/ML Core (Week 2-4)

### 2.1 LLM Setup
| Task | Owner | Est. Time | Dependencies |
|------|-------|-----------|-------------|
| Install Ollama | Eng | 30 min | — |
| Pull base model (`mistral:7b-instruct`) | Eng | 10 min | Ollama running |
| Test local inference | Eng | 1 hr | Model downloaded |
| Build LLM wrapper class | Eng | 3 hrs | Inference working |
| **Milestone:** `python -c "from src.llm import LLM; print(LLM().generate('Hello'))"` |

**Deliverable:** `src/llm.py` with:
- `generate(prompt, max_tokens=500)`
- `generate_with_context(prompt, context_docs)`

---

### 2.2 RAG Pipeline
| Task | Owner | Est. Time | Dependencies |
|------|-------|-----------|-------------|
| Install ChromaDB | Eng | 30 min | — |
| Build embedding pipeline (`BAAI/bge-base-en`) | Eng | 4 hrs | — |
| Index training emails into ChromaDB | Eng | 4 hrs | Ingestion done |
| Build retrieval function | Eng | 3 hrs | Index ready |
| Test retrieval quality | Tech Lead | 2 hrs | Retrieval working |
| **Milestone:** Query "refund request" → returns 5 similar past emails |

**Deliverable:** `src/rag.py` with:
- `index_emails(emails_df)`
- `search(query, top_k=5)`

---

### 2.3 Fine-Tuning (Optional, Parallel Track)
| Task | Owner | Est. Time | Dependencies |
|------|-------|-----------|-------------|
| Prepare fine-tuning dataset (JSONL) | Eng | 4 hrs | Training CSV ready |
| Set up Unsloth or Axolotl | Eng | 4 hrs | GPU access |
| Fine-tune `Phi-3-mini` on style | Eng | 8 hrs + training time | Dataset ready |
| Export model to GGUF format | Eng | 2 hrs | Training complete |
| Test fine-tuned model vs base | Tech Lead | 4 hrs | Model exported |
| **Decision Gate:** Does fine-tuned model justify extra complexity? |

**Deliverable:** `models/email-agent-personal/ggml-model-f16.gguf`

---

### 2.4 Response Generator
| Task | Owner | Est. Time | Dependencies |
|------|-------|-----------|-------------|
| Build prompt template system | Eng | 3 hrs | LLM working |
| Define tone modes (casual, formal, concise) | PM | 2 hrs | — |
| Integrate RAG context into prompt | Eng | 3 hrs | RAG working |
| Test response quality (10 sample emails) | Tech Lead | 4 hrs | Templates ready |
| **Milestone:** Input email → output draft in <30 sec |

**Deliverable:** `src/response_generator.py` with:
- `generate_reply(incoming_email, tone="formal")` → `str`

---

## Phase 3: User Interface (Week 3-4)

### 3.1 Gradio Dashboard
| Task | Owner | Est. Time | Dependencies |
|------|-------|-----------|-------------|
| Scaffold Gradio app | Eng | 2 hrs | — |
| Build pending drafts table | Eng | 4 hrs | DB schema ready |
| Add approve/send button | Eng | 2 hrs | — |
| Add edit draft text area | Eng | 2 hrs | — |
| Add tone selector dropdown | Eng | 1 hr | — |
| **Milestone:** `python src/dashboard.py` → localhost:7860 |

**Deliverable:** `src/dashboard.py` with UI showing:
- Pending drafts (subject, sender, preview)
- Draft text editor
- Approve / Edit / Delete buttons
- Real-time refresh (every 30 sec)

---

### 3.2 Database Layer
| Task | Owner | Est. Time | Dependencies |
|------|-------|-----------|-------------|
| Design SQLite schema (emails, drafts, runs) | Tech Lead | 2 hrs | — |
| Build DAO layer | Eng | 4 hrs | Schema approved |
| Add draft tracking (status, confidence) | Eng | 3 hrs | DAO ready |
| **Milestone:** Drafts persist across restarts |

**Deliverable:** `src/db.py` with tables:
- `emails(id, thread_id, sender, subject, received_at)`
- `drafts(id, email_id, generated_text, tone, status, created_at)`

---

### 3.3 Notification System
| Task | Owner | Est. Time | Dependencies |
|------|-------|-----------|-------------|
| Set up ntfy.sh topic | PM | 30 min | — |
| Build notification sender | Eng | 2 hrs | — |
| Trigger on new draft created | Eng | 2 hrs | Dashboard working |
| **Milestone:** New draft → push notification to phone |

**Deliverable:** `src/notifier.py` with:
- `notify_draft_ready(subject, preview, draft_id)`

---

## Phase 4: Automation (Week 4-5)

### 4.1 Email Watcher Service
| Task | Owner | Est. Time | Dependencies |
|------|-------|-----------|-------------|
| Implement Gmail polling (every 5 min) | Eng | 4 hrs | Gmail client ready |
| OR set up Gmail push notifications | Eng | 6 hrs | Pub/Sub topic |
| Filter: only process unread, non-spam | Eng | 2 hrs | Polling working |
| **Milestone:** New email → draft created within 10 min |

**Deliverable:** `src/watcher.py` running as:
- `python src/watcher.py` (foreground)
- Or `systemd` service / cron job

---

### 4.2 Confidence Scoring & Auto-Send
| Task | Owner | Est. Time | Dependencies |
|------|-------|-----------|-------------|
| Define confidence thresholds | PM + Tech Lead | 2 hrs | — |
| Build scorer (0.0-1.0) | Eng | 4 hrs | Response gen working |
| Implement auto-send for high-confidence | Eng | 3 hrs | Scorer ready |
| Add safety rules (never auto-send financial) | Eng | 3 hrs | Auto-send working |
| **Milestone:** Low-risk emails auto-sent, high-risk queued |

**Deliverable:** `src/confidence.py` with:
- `score(incoming_email, draft) -> float`
- `should_auto_send(draft) -> bool`

---

### 4.3 Monitoring & Logging
| Task | Owner | Est. Time | Dependencies |
|------|-------|-----------|-------------|
| Add structured logging (`structlog`) | Eng | 3 hrs | — |
| Track: drafts created, sent, edited | Eng | 3 hrs | Logging ready |
| Build simple metrics dashboard | Eng | 4 hrs | Data logged |
| **Milestone:** Can answer "how many drafts sent last week?" |

**Deliverable:** `logs/email-agent.jsonl` + `src/metrics.py`

---

## Phase 5: Testing & Polish (Week 5-6)

### 5.1 End-to-End Testing
| Task | Owner | Est. Time | Dependencies |
|------|-------|-----------|-------------|
| Test full flow: email → draft → send | PM | 4 hrs | All components ready |
| Test each tone mode | PM | 2 hrs | — |
| Test error cases (network, API limits) | Eng | 4 hrs | — |
| Load test: 100 emails in 1 hour | Eng | 4 hrs | — |
| **Milestone:** 95% success rate on test suite |

**Deliverable:** `tests/e2e_test.py` + test results doc

---

### 5.2 Security Review
| Task | Owner | Est. Time | Dependencies |
|------|-------|-----------|-------------|
| Audit credential storage | Tech Lead | 2 hrs | — |
| Verify no email data leaves machine | Tech Lead | 2 hrs | — |
| Add rate limiting (prevent spam) | Eng | 3 hrs | — |
| Red-team: try to trick into sending bad emails | PM | 2 hrs | — |
| **Milestone:** Security sign-off |

**Deliverable:** `SECURITY.md` with audit results

---

### 5.3 Documentation
| Task | Owner | Est. Time | Dependencies |
|------|-------|-----------|-------------|
| Write `README.md` (install + usage) | Tech Lead | 3 hrs | — |
| Write `ARCHITECTURE.md` (for future devs) | Tech Lead | 3 hrs | — |
| Record 2-min demo video | PM | 1 hr | UI ready |
| **Milestone:** New dev can set up in <30 min |

---

## Phase 6: Launch (Week 6)

### 6.1 Soft Launch
| Task | Owner | Est. Time | Dependencies |
|------|-------|-----------|-------------|
| Deploy to personal machine | Tech Lead | 2 hrs | All testing done |
| Run for 1 week, collect feedback | PM | Ongoing | Deployed |
| Track: drafts created, approved, edited, rejected | PM | Ongoing | — |
| **Milestone:** 100+ emails processed, <5% rejection rate |

---

### 6.2 Iteration
| Task | Owner | Est. Time | Dependencies |
|------|-------|-----------|-------------|
| Review feedback, prioritize fixes | Tech Lead | 2 hrs | 1 week of data |
| Ship weekly updates | Eng | Ongoing | Backlog ready |
| **Milestone:** v1.0 release |

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Draft quality (user edits per draft) | <2 edits/draft | Dashboard logs |
| Time saved (manual vs AI draft) | >70% reduction | User survey |
| False positive auto-sends | 0 | Error logs |
| Uptime | >99% | Monitoring |
| User satisfaction | >4/5 | Weekly survey |

---

## Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Gmail API rate limits | Medium | High | Batch requests, exponential backoff |
| Fine-tuned model underperforms | Medium | Medium | Fallback to prompt engineering |
| OAuth token expires | Low | High | Auto-refresh, monitoring alerts |
| Email data leak | Low | Critical | Local-only processing, encryption at rest |
| User rejects too many drafts | Medium | Medium | Improve RAG, tune prompts, more training data |

---

## Resource Requirements

| Resource | Quantity | Cost |
|----------|----------|------|
| GPU (training) | 1x A10G or equivalent | ~$50 (one-time) |
| AWS Secrets Manager | 3 secrets | ~$1/month |
| ntfy.sh (notifications) | Free tier | $0 |
| Developer time | 4-6 weeks | [Internal] |

---

## Appendix: File Structure

```
email-agent/
├── README.md
├── requirements.txt
├── .env.example
├── src/
│   ├── __init__.py
│   ├── gmail_client.py      # Gmail API wrapper
│   ├── ingest.py            # mbox → CSV
│   ├── llm.py               # Ollama wrapper
│   ├── rag.py               # ChromaDB retrieval
│   ├── response_generator.py
│   ├── confidence.py        # Scoring logic
│   ├── db.py                # SQLite DAO
│   ├── dashboard.py         # Gradio UI
│   ├── watcher.py           # Email polling
│   └── notifier.py          # Push notifications
├── tests/
│   ├── test_gmail.py
│   ├── test_rag.py
│   └── e2e_test.py
├── data/
│   ├── training_emails.csv
│   └── email_agent.db
├── models/                   # Fine-tuned models (optional)
└── logs/
```

---

**Next Steps:**
1. PM assigns owners to Phase 1 tasks
2. Tech Lead sets up repo + env
3. First standup: [Date]
