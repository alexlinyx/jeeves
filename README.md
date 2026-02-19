# Jeeves - AI Email Assistant

Jeeves is an AI-powered email assistant that learns your writing style and drafts contextual responses automatically. All processing happens locally — your email data never leaves your machine.

## Features

- 🤖 **AI-Powered Responses** — Uses local LLM (Ollama) to generate contextual replies
- 📚 **Style Learning** — Learns from your past emails to match your writing style
- 🎨 **Multiple Tones** — Casual, formal, concise, or style-match modes
- 🔒 **Privacy First** — All processing happens locally, no data leaves your machine
- 📊 **Review Dashboard** — Gradio UI to review and edit drafts before sending
- 🔔 **Push Notifications** — Get notified when new drafts are ready

## Quick Start

### Prerequisites

- Python 3.11+
- Ollama (for local LLM)
- Gmail account with API access

### Installation

```bash
# Clone the repository
git clone https://github.com/alexlinyx/jeeves.git
cd jeeves

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Ollama and download model
# See: https://ollama.ai
ollama pull mistral:7b-instruct

# Set up Gmail OAuth (see docs/gmail-setup.md)
```

### Configuration

```bash
# Copy example config
cp .env.example .env

# Edit with your settings
nano .env
```

Required environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `OLLAMA_BASE_URL` | Ollama API URL | `http://localhost:11434` |
| `DEFAULT_MODEL` | LLM model | `mistral:7b-instruct` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `DATA_DIR` | Data directory | `./data` |
| `MODELS_DIR` | Models directory | `./models` |

For Gmail OAuth setup, see [Gmail Setup Guide](docs/gmail-setup.md).

### Run

```bash
# Ingest your email history (one-time)
python -m src.ingest --mbox ~/Downloads/takeout.mbox --user-email you@example.com

# Start the dashboard
python -m src.dashboard

# Or run in background with email watcher
python -m src.watcher
```

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

```bash
# Set your topic in .env
NTFY_TOPIC=your-unique-topic

# Subscribe on your phone
# iOS: https://apps.apple.com/app/ntfy
# Android: https://play.google.com/store/apps/details?id=io.heckel.ntfy
```

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for system design details.

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## License

MIT License - see [LICENSE](LICENSE)