# Jeeves

AI-powered email assistant that learns your writing style and drafts responses for you.

## What It Does

1. **Learns your style** — Fine-tunes an LLM on your email history
2. **Drafts responses** — Generates context-aware replies to new emails
3. **Tone modes** — Casual, formal, concise, or match your personal style
4. **Human-in-the-loop** — All drafts require your approval before sending
5. **Local-first** — Your email data never leaves your machine

## Tech Stack

- **Python** — Core language
- **Gmail API** — Email access via OAuth
- **Ollama** — Local LLM inference (Mistral, Llama, etc.)
- **LangChain** — Agent orchestration
- **ChromaDB** — Vector storage for RAG
- **Gradio** — Web dashboard for draft review

## Documentation

- [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md) — Project plan with phases, tasks, and milestones
- [email-agent-specs.md](./email-agent-specs.md) — Technical specification for each component
- [email-agent-tooling-analysis.md](./email-agent-tooling-analysis.md) — Tool comparison (n8n vs LLMMe vs custom)
- [auto-responder-design.md](./auto-responder-design.md) — Architecture overview

## Status

🚧 **Planning Phase** — Implementation starting soon

## Quick Start

```bash
# Clone the repo
git clone https://github.com/alexlinyx/jeeves.git
cd jeeves

# Install dependencies (coming soon)
pip install -r requirements.txt

# Run the agent (coming soon)
python src/dashboard.py
```

## Roadmap

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Foundation (OAuth, ingestion) | 🔜 Planned |
| 2 | AI/ML Core (LLM, RAG) | 🔜 Planned |
| 3 | UI (Gradio dashboard) | 🔜 Planned |
| 4 | Automation (watcher, auto-send) | 🔜 Planned |
| 5 | Testing & Polish | 🔜 Planned |
| 6 | Launch | 🔜 Planned |

## License

MIT

---

*"Indeed, sir, I endeavor to give satisfaction."* 🎩
