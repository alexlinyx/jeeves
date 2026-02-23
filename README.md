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
```

### Ollama Setup

Jeeves uses Ollama for local LLM inference. All AI processing happens on your machine.

#### Install Ollama

**macOS / Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
Download from https://ollama.ai/download

**Verify installation:**
```bash
ollama --version
```

#### Start Ollama Service

Ollama runs as a background service:

```bash
# Start the service (runs on http://localhost:11434)
ollama serve

# In a new terminal, verify it's running
curl http://localhost:11434/api/tags
```

#### Download a Model

Jeeves works best with instruction-tuned models:

```bash
# Recommended: Mistral 7B (best balance of speed and quality)
ollama pull mistral:7b-instruct

# Alternative: Llama 3.2 3B (faster, lower quality)
ollama pull llama3.2:3b

# Alternative: Qwen 2.5 7B (good for non-English)
ollama pull qwen2.5:7b
```

#### Hardware Requirements

| Model | RAM | GPU | Speed |
|-------|-----|-----|-------|
| mistral:7b-instruct | 8GB | 6GB VRAM (optional) | ~3-5s per draft |
| llama3.2:3b | 4GB | 4GB VRAM (optional) | ~1-2s per draft |
| qwen2.5:7b | 8GB | 6GB VRAM (optional) | ~3-5s per draft |

**Note:** GPU is optional but significantly faster. Without GPU, models run on CPU (slower but works fine).

#### Test Your Setup

```bash
# Quick test
ollama run mistral:7b-instruct "Say hello in one sentence."

# Should output a greeting and exit
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

### Run & Data Ingestion

To use the "Match Style" feature, Jeeves needs to analyze your past emails via a Google Takeout `.mbox` file.

**How to get your `.mbox` file:**
1. Go to **[Google Takeout](https://takeout.google.com/)**
2. Click **"Deselect all"**
3. Check the box next to **"Mail"** (Tip: Click "All Mail data included" and uncheck everything except your "Sent" folder to make the file smaller and faster to process)
4. Scroll to the bottom and click **"Next step"**, then **"Create export"**
5. Google will email you a download link (can take hours). Once downloaded and unzipped, you'll have your `.mbox` file.

```bash
# Ingest your email history (one-time)
python -m src.ingest --mbox ~/Downloads/Takeout/Mail/Sent.mbox --user-email you@example.com --sent-only

# Start the dashboard
python -m src.dashboard

# Or run in background with email watcher
python -m src.watcher
```
*(Note: You can run the dashboard and watcher without an `.mbox` file to use the default AI tones. The `.mbox` is only required for the "Match Style" feature.)*

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
| `match_style` | Mimics your writing style from past emails (requires `.mbox` ingestion) |

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