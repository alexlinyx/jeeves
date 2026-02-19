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

## Status

🚧 **In Development** — Feature 1.2 (Gmail OAuth) in progress

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/alexlinyx/jeeves.git
cd jeeves

# 2. Create virtual environment
python3 -m venv venv

# 3. Activate (Mac/Linux)
source venv/bin/activate

# 3. Activate (Windows)
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Set up Gmail access (see below)
```

---

# Gmail Setup (READ THIS FIRST)

**You need to give Jeeves permission to read and send emails.**  
This requires a one-time setup in Google's system. Don't worry — we'll walk you through it step by step.

**Estimated time:** 5 minutes

---

## Step 1: Create a Google Cloud Project

1. Go to: https://console.cloud.google.com/projectcreate
2. Enter a name, like: `jeeves-email-assistant`
3. Click **CREATE**
4. Wait for it to finish (this takes ~30 seconds)

**Important:** Keep this tab open — you'll need it for the next steps.

---

## Step 2: Enable the Gmail API

1. In the Google Cloud Console (your project), go to the menu (☰) on the left
2. Click **APIs & Services** → **Library**
3. In the search bar, type: `Gmail API`
4. Click on **Gmail API** when it appears
5. Click **ENABLE**

---

## Step 3: Configure OAuth Consent Screen

This tells Google what permissions Jeeves needs.

1. Go to: **APIs & Services** → **OAuth consent screen** (in the left menu)
2. Click **CREATE**
3. Fill in the form:

   | Field | What to enter |
   |-------|---------------|
   | User Type | **External** (unless you have a Google Workspace) |
   | App name | `Jeeves` |
   | User support email | Your email address |
   | Developer contact email | Your email address |

4. Click **SAVE AND CONTINUE** (you can skip scopes for now)
5. Click **SAVE AND CONTINUE** again (skip test users)
6. Click **BACK TO DASHBOARD**

---

## Step 4: Create OAuth Credentials

Now we create the "keys" that let Jeeves access your Gmail.

1. Go to: **APIs & Services** → **Credentials** (in the left menu)
2. Click **+ CREATE CREDENTIALS** (top of page)
3. Select **OAuth client ID**
4. Fill in:

   | Field | What to enter |
   |-------|---------------|
   | Application type | **Desktop app** |
   | Name | `Jeeves Desktop Client` |

5. Click **CREATE**
6. A popup will appear — click **DOWNLOAD JSON**
7. This downloads a file named something like `client_secret_12345.json`

---

## Step 5: Save the Credentials File

1. Create a folder named `data` in the jeeves repo:
   ```bash
   mkdir -p data
   ```

2. Rename your downloaded file to `credentials.json`
3. Move it into the `data` folder:
   ```bash
   # Mac/Linux
   mv ~/Downloads/client_secret_*.json data/credentials.json
   
   # Windows (in File Explorer)
   # Copy the file into the data folder
   ```

---

## Step 6: First Run (Authenticate)

Now we'll test that everything works. When you run this, a browser window will open asking you to grant permission.

```bash
# Activate the virtual environment (if not already activated)
source venv/bin/activate   # Mac/Linux
# or
venv\Scripts\activate       # Windows

# Test Gmail connection
python -c "from src.gmail_client import GmailClient; c = GmailClient(); print('Success!', len(c.list_emails(5)), 'emails fetched')"
```

**What happens:**
1. A browser window opens
2. Sign in to your Google account (if not already)
3. You'll see a warning: "Google hasn't verified this app" — this is **normal** for personal projects
4. Click **Advanced** → **Go to Jeeves (unsafe)** (or similar)
5. Click **Allow** for the three permissions (Read, Compose, Send)
6. The browser will show "You can close this window"
7. Switch back to your terminal — you should see "Success! 5 emails fetched"

If it worked, you're all set!

---

## Step 7: What Just Happened?

After authenticating, Google gave Jeeves a "refresh token" that lets it access your email without asking for permission every time.

This token is saved in: `data/gmail_token.json`

**⚠️ Important:** Add this file to `.gitignore` so you don't accidentally commit it to Git:
```bash
echo "data/gmail_token.json" >> .gitignore
```

---

## Troubleshooting

### "Client is not authorized to access this API"
- Go back to Step 2 and make sure you clicked **ENABLE** on the Gmail API

### "invalid_client"
- Check that `data/credentials.json` exists and contains valid JSON
- Make sure you didn't accidentally edit the file

### Browser doesn't open
- Run the command with `--noauth_local_webserver` flag and copy the URL manually

### "This app is not verified"
- This is normal for self-hosted apps
- Click "Advanced" → "Go to [App Name] (unsafe)" to proceed

### Token expired or revoked
- Delete `data/gmail_token.json` and run Step 6 again

---

## Common Issues

**Q: Does Jeeves store my email password?**
No. It uses OAuth, which means you give permission through Google directly. Jeeves never sees your password.

**Q: Can I revoke access later?**
Yes. Go to your Google Account → Security → Third-party app access → Manage third-party access → Remove Jeeves.

**Q: Does this work with Google Workspace / business accounts?**
Yes, but you may need an admin to approve the app. For personal Gmail, it works out of the box.

---

## Development Setup

```bash
# Clone
git clone https://github.com/alexlinyx/jeeves.git
cd jeeves

# Set up Python environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure Gmail (see steps above)
mkdir -p data
# ... download credentials.json to data/ ...

# Test it works
python -c "from src.gmail_client import GmailClient; print(GmailClient().list_emails(1))"

# Run tests
pytest tests/ -v
```

---

## Roadmap

| Phase | Description | Status |
|-------|-------------|--------|
| 1.1 | Environment Setup | ✅ Done |
| 1.2 | Gmail OAuth | 🔄 In Progress |
| 1.3 | Email Ingestion | 🔜 Planned |
| 2 | AI/ML Core (LLM, RAG) | 🔜 Planned |
| 3 | UI (Gradio dashboard) | 🔜 Planned |
| 4 | Automation (watcher, auto-send) | 🔜 Planned |

---

## License

MIT

---

*"Indeed, sir, I endeavor to give satisfaction."* 🎩
