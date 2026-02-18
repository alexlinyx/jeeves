# Email Agent Tooling Analysis

## What Each Existing Tool Handles

| Step | Tool | What It Handles | What It DOESN'T Handle |
|------|------|-----------------|------------------------|
| **1. OAuth** | `gog` | ✅ Gmail auth, token refresh | ❌ You still need trigger logic |
| **1. OAuth** | n8n | ✅ Pre-built Gmail node, OAuth flow | ❌ Still need to orchestrate agent |
| **2. Ingest** | LLMMe | ✅ mbox → CSV conversion script | ❌ Real-time sync, API ingestion |
| **2. Ingest** | n8n | ✅ Gmail trigger (new emails), IMAP node | ❌ Full historical export (10k+ emails) |
| **3. Train** | LLMMe | ✅ Dataset prep, training instructions for H2O | ❌ Fine-tuning pipeline automation |
| **3. Train** | n8n | ❌ Nothing (no training nodes) | ❌ Use axolotl/unsloth separately |
| **4. Process** | n8n | ✅ HTTP request to Ollama/LM Studio, basic classification | ❌ RAG, complex agent logic |
| **4. Process** | LLMMe | ❌ Nothing | ❌ LLMMe is just training |
| **5. Draft** | n8n | ✅ Gmail node (create draft) | ❌ Response generation |
| **5. Draft** | `gog` | ✅ `gog gmail send --draft` | ❌ AI generation |
| **6. Review** | n8n | ✅ Form trigger (basic approval) | ❌ Rich UI, conversation threading |
| **7. Send** | n8n | ✅ Gmail node (send draft) or create new | ❌ Final confirmation logic |

---

## Recommendation: Hybrid Approach

**Use n8n as glue, build custom Python service for AI/ML**

```
┌─────────────────────────────────────────────────────────────────┐
│                        n8n (Orchestration)                      │
├─────────────────────────────────────────────────────────────────┤
│ Gmail Trigger → HTTP to AI Service → Wait for Approval → Send  │
└─────────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────────┐
│                  Custom Python Service (FastAPI)               │
├─────────────────────────────────────────────────────────────────┤
│ Ingestion → RAG (LlamaIndex) → Fine-tuned LLM → Response Gen  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Why Not N8N-Only?

**N8N limitations for this use case:**

1. **No fine-tuning nodes** — Can't train writing style models
2. **No local LLM with RAG** — HTTP to Ollama is basic, no memory/context
3. **No vector DB native integration** — ChromaDB/weaviate need custom code
4. **State management** — Hard to maintain conversation state across retries
5. **Batch processing** — Downloading 10k historical emails is clunky

**What n8n IS good for:**
- Trigger on new Gmail → webhook
- Human-in-the-loop approval forms
- Connecting to other services (Slack, calendar, etc.)
- Scheduling, retries, error handling

---

## Pure Python Alternative (No N8N)

**If you want minimal dependencies:**

| Step | Tool | Effort |
|------|------|--------|
| OAuth | `google-auth-oauthlib` + `keyring` | Medium |
| Ingest | `imaplib` + custom batching | Medium |
| Train | `axolotl` or `unsloth` | High (ML setup) |
| Process | `langchain` + `llama-index` | Medium |
| Draft | `google-api-python-client` | Low |
| Review | `gradio` or `streamlit` | Low |
| Send | Gmail API | Low |
| Trigger | `watchdog` or cron | Low |

**Trade-off:** More control, but you build orchestration yourself.

---

## What LLMMe Provides

**LLMMe is ONLY training infrastructure:**

✅ **Includes:**
- mbox → CSV converter (extract prompt/response pairs)
- Instructions for H2O LLM Studio training
- Gradio UI for testing model

❌ **Missing:**
- No Gmail API integration (reads mbox files only)
- No real-time processing
- No RAG/context retrieval
- No orchestration
- Single-user, not multi-tenant

**Verdict:** Use LLMMe's mbox converter, ignore rest (build your own pipeline).

---

## Recommended Stack

### Option A: N8N + Custom Python (Balanced)

| Component | Tool | Responsibility |
|-----------|------|----------------|
| Orchestration | n8n | Triggers, approval flows, error handling |
| AI Service | Python + FastAPI | Training, inference, RAG, state |
| Gmail | `gog` or n8n node | Authentication, draft/send |
| Review UI | n8n form or Gradio | Human approval |

**Pros:** Visual workflow, easy to extend, handles edge cases
**Cons:** Two systems to maintain

### Option B: Pure Python (Maximum Control)

| Component | Tool |
|-----------|------|
| Everything | Python + FastAPI + Celery |
| Queue | Redis + Celery |
| DB | PostgreSQL |
| Vector | ChromaDB |
| UI | Gradio or React |

**Pros:** Single codebase, easier to package as ClawHub skill
**Cons:** Build orchestration from scratch

### Option C: N8N-Only (MVP Fast)

**Abandon fine-tuning, use prompt engineering:**

1. Gmail trigger (n8n)
2. HTTP to Ollama with system prompt: "You write like [paste 3 examples]"
3. Draft via Gmail node
4. Form approval
5. Send

**Pros:** Working in hours, not days
**Cons:** No true style learning, context window limits

---

## Which Should You Choose?

| Goal | Recommendation |
|------|----------------|
| Ship fast, validate concept | Option C (n8n + prompting) |
| Build serious product | Option A (n8n + Python) |
| ClawHub skill + standalone | Option B (pure Python) |
| Maximum AI quality | Option A or B with fine-tuning |

---

## My Recommendation for You

**Option A with path to Option B:**

1. **Start with n8n + Gradio** — Get flow working fast
2. **Extract to Python service** — Once inference code stabilizes
3. **Package as ClawHub skill** — Pure Python is easier to distribute
4. **Add fine-tuning later** — Start with few-shot prompting

This lets you validate the UX before investing in ML infrastructure.
