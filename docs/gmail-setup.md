# Gmail Setup Guide

Jeeves requires OAuth 2.0 credentials to read your emails and save drafts securely. It does **not** use an app password, ensuring maximum security via OAuth.

## Setup Instructions

1. **Go to Google Cloud Console:** https://console.cloud.google.com/
2. **Create a Project:** Name it "Jeeves Email AI"
3. **Enable APIs:** Go to "APIs & Services" -> "Library" -> search for "Gmail API" and click Enable.
4. **Configure OAuth Consent Screen:**
   - User Type: Internal (if Google Workspace) or External (if regular @gmail.com)
   - Add scopes: `.../auth/gmail.readonly`, `.../auth/gmail.compose`, `.../auth/gmail.send`
   - Add your email as a test user if External.
5. **Create Credentials:**
   - Go to "Credentials" -> "Create Credentials" -> "OAuth client ID"
   - Application type: "Desktop app" (or "Web application")
   - Click "Download JSON"
6. **Save file:**
   - Move the downloaded JSON file to your Jeeves data directory and name it `credentials.json` (e.g., `data/credentials.json`).
   - If you want to use a different location, update `GMAIL_CREDENTIALS_PATH` in your `.env` file.
7. **First Run:**
   - When you first run `python -m src.ingest`, it will open a browser to authenticate.
   - It will save a `gmail_token.json` file in your data directory for future runs automatically.