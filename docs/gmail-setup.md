# Gmail Setup Guide

Jeeves requires OAuth 2.0 credentials to read your emails and save drafts securely. It does **not** use an app password, ensuring maximum security via OAuth.

## Automated Setup (OpenClaw)
If you're running Jeeves on your OpenClaw host, your agent can automatically pull your existing Google Workspace credentials from AWS Secrets Manager (`alyxclaw/google/oauth-credentials` and `alyxclaw/google/refresh-token`). Just ask Claw to "configure Jeeves Gmail auth".

## Manual Setup

If you're running this on a new machine without AWS Secrets Manager access:

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
   - Move the downloaded JSON file to `jeeves/data/credentials.json`.
7. **First Run:**
   - When you first run `python -m src.ingest`, it will open a browser to authenticate.
   - It will save a `data/gmail_token.json` file for future runs automatically.