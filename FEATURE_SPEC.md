# Feature Spec: Gmail OAuth Integration

**Phase:** 1.2  
**Branch:** `feature/1.2-gmail-oauth`  
**Priority:** P0 (Blocking)  
**Est. Time:** 8 hours

---

## Objective

Enable Jeeves to authenticate with Gmail via OAuth 2.0 and provide a Python client wrapper for email operations.

---

## Acceptance Criteria

- [ ] Gmail API enabled in Google Cloud Console
- [ ] OAuth 2.0 Desktop credentials created
- [ ] Credentials stored in AWS Secrets Manager (`alyxclaw/google/`)
- [ ] `gog` CLI authentication verified
- [ ] `src/gmail_client.py` implements required methods
- [ ] Can fetch last 10 emails via Python

---

## Deliverable

### `src/gmail_client.py`

```python
from typing import List, Dict, Optional

class GmailClient:
    """Gmail API wrapper for Jeeves email operations."""
    
    def list_emails(self, limit: int = 100) -> List[Dict]:
        """Fetch recent emails.
        
        Args:
            limit: Maximum number of emails to fetch (default 100)
            
        Returns:
            List of email dicts with keys: id, thread_id, subject, from, date, snippet
        """
        pass
    
    def get_email(self, message_id: str) -> Dict:
        """Fetch a specific email by message ID.
        
        Args:
            message_id: Gmail message ID
            
        Returns:
            Email dict with keys: id, thread_id, subject, from, to, date, body_text, body_html
        """
        pass
    
    def create_draft(self, thread_id: str, to: str, subject: str, body: str) -> str:
        """Create a draft reply.
        
        Args:
            thread_id: Gmail thread ID
            to: Recipient email address
            subject: Email subject
            body: Draft body content
            
        Returns:
            Draft ID
        """
        pass
    
    def send_draft(self, draft_id: str) -> bool:
        """Send a draft.
        
        Args:
            draft_id: Gmail draft ID
            
        Returns:
            True if successful
        """
        pass
    
    def list_drafts(self, limit: int = 10) -> List[Dict]:
        """List drafts.
        
        Args:
            limit: Maximum number of drafts to fetch
            
        Returns:
            List of draft dicts
        """
        pass
```

---

## Tasks

### 1.2.1 Enable Gmail API (30 min)
- [ ] Navigate to Google Cloud Console
- [ ] Create new project or select existing
- [ ] Enable Gmail API
- [ ] Configure OAuth consent screen

### 1.2.2 Create OAuth Credentials (30 min)
- [ ] Create OAuth 2.0 Desktop app credentials
- [ ] Download `credentials.json`
- [ ] Note: Client secret needed for AWS SM

### 1.2.3 Store Credentials in AWS (1 hr)
- [ ] Store in `alyxclaw/google/` prefix
- [ ] Keys needed:
  - `gmail-oauth-client-id`
  - `gmail-oauth-client-secret`
  - `gmail-refresh-token` (after first auth)

### 1.2.4 Test gog CLI (1 hr)
- [ ] Verify gog can authenticate with Gmail
- [ ] Test `gog gmail list --limit 10`

### 1.2.5 Build Gmail Client Wrapper (4 hrs)
- [ ] Implement `GmailClient` class
- [ ] Use google-auth-oauthlib for authentication
- [ ] Handle token refresh automatically
- [ ] Implement all methods in deliverable spec
- [ ] Add error handling for rate limits

---

## Dependencies

| Dependency | Purpose |
|------------|---------|
| google-auth-oauthlib | OAuth 2.0 flow |
| google-auth-httplib2 | HTTP requests |
| google-api-python-client | Gmail API |
| gog CLI | Credentials management |

---

## Testing

```python
from src.gmail_client import GmailClient

client = GmailClient()

# Test fetching emails
emails = client.list_emails(limit=10)
print(f"Fetched {len(emails)} emails")

# Test getting a specific email
if emails:
    email = client.get_email(emails[0]['id'])
    print(f"Subject: {email['subject']}")

# Test draft creation
draft_id = client.create_draft(
    thread_id=emails[0]['thread_id'],
    to=email['from'],
    subject=f"Re: {email['subject']}",
    body="This is a test draft."
)
print(f"Created draft: {draft_id}")
```

---

## Notes

- Refresh tokens don't expire unless revoked — store securely
- Gmail API rate limit: 250 calls/second/user
- Use batch requests for bulk operations
- `gog` CLI handles OAuth flow conveniently — leverage it for initial auth

---

## Definition of Done

1. OAuth credentials created and stored in AWS SM
2. `gog gmail list` works from CLI
3. `src/gmail_client.py` implements all 5 methods
4. `python -c "from src.gmail_client import GmailClient; c = GmailClient(); print(len(c.list_emails(10)))"` succeeds
5. Branch pushed to GitHub
6. PR created
