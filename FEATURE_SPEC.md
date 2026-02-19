# Feature Spec: Email Ingestion Pipeline

**Phase:** 1.3  
**Branch:** `feature/1.3-email-ingestion`  
**Priority:** P0 (Blocking)  
**Est. Time:** 14 hours

---

## Objective

Build the pipeline to ingest email history from Gmail, extract training data (sent emails), and save as CSV for downstream AI training.

---

## Acceptance Criteria

- [ ] Gmail Takeout export instructions provided to user
- [ ] `src/ingest.py` can parse `.mbox` files
- [ ] Extracts sent emails (from "Sent" folder or by filtering `sent_by_you` field)
- [ ] Outputs `data/training_emails.csv` with schema:
  - `thread_id`
  - `from`
  - `subject`
  - `body_text`
  - `sent_by_you` (boolean)
  - `timestamp`
- [ ] Command `python src/ingest.py --mbox ~/Downloads/takeout.mbox` produces valid CSV
- [ ] Unit tests for parser pass

---

## Deliverable

### `src/ingest.py`

```python
"""Email ingestion from Gmail Takeout .mbox files."""
import argparse
import csv
import os
from datetime import datetime
from email import policy
from email.parser import BytesParser
from mailbox import mbox
from typing import List, Dict, Optional
import re


def parse_mbox(mbox_path: str, output_csv: str = "data/training_emails.csv") -> int:
    """Parse .mbox file and extract email data.
    
    Args:
        mbox_path: Path to the .mbox file
        output_csv: Path to output CSV file
        
    Returns:
        Number of emails processed
    """
    pass


def extract_email_address(header_value: str) -> str:
    """Extract email address from From header.
    
    Args:
        header_value: Full From header (e.g., "John Doe <john@example.com>")
        
    Returns:
        Email address only
    """
    pass


def clean_body(body: str) -> str:
    """Clean email body text.
    
    - Remove quoted replies (lines starting with >)
    - Remove signatures (-- \n...)
    - Strip whitespace
    - Remove excessive newlines
    
    Args:
        body: Raw email body
        
    Returns:
        Cleaned body text
    """
    pass


def is_sent_email(email_message, user_email: str) -> bool:
    """Determine if email was sent by user.
    
    Checks:
    - Is in Sent folder (folder name)
    - From address matches user's email
    - X-Gmail-Labels contains "Sent"
    
    Args:
        email_message: email.message.Message object
        user_email: User's email address
        
    Returns:
        True if sent by user
    """
    pass


def get_timestamp(email_message) -> Optional[str]:
    """Extract timestamp from email.
    
    Args:
        email_message: email.message.Message object
        
    Returns:
        ISO format timestamp or None
    """
    pass


def extract_thread_id(email_message) -> Optional[str]:
    """Extract thread ID from email headers.
    
    Looks in:
    - X-Gmail-Thread-Top
    - X-Gmail-Thread-Index
    - References header
    
    Args:
        email_message: email.message.Message object
        
    Returns:
        Thread ID or None
    """
    pass


def extract_subject(email_message) -> str:
    """Extract subject line, handling Re:, Fwd:, etc.
    
    Args:
        email_message: email.message.Message object
        
    Returns:
        Cleaned subject line
    """
    pass


def extract_body(email_message) -> str:
    """Extract body text from email.
    
    Handles:
    - Plain text
    - HTML (strips tags)
    - Multipart (prefers plain text)
    
    Args:
        email_message: email.message.Message object
        
    Returns:
        Body text
    """
    pass


def filter_useful_email(body: str, subject: str) -> bool:
    """Filter out auto-generated emails.
    
    Excludes:
    - Auto-replies (auto-generated, auto-reply, out of office)
    - Bounces (delivery failed, undelivered)
    - Notifications (new followup, mention)
    - Empty or very short emails
    
    Args:
        body: Email body text
        subject: Email subject
        
    Returns:
        True if email is useful for training
    """
    # Auto-generated patterns
    auto_patterns = [
        r'auto-?generated',
        r'auto-?reply',
        r'out of office',
        r'ooo',
        r'delivery failed',
        r'undelivered',
        r'mailer-?daemon',
        r'noreply',
        r'no-?reply',
        r'don\'t reply',
        r'notification',
    ]
    
    # Check subject and body
    text = (subject + ' ' + body).lower()
    for pattern in auto_patterns:
        if re.search(pattern, text):
            return False
    
    # Minimum length check
    if len(body.strip()) < 50:
        return False
    
    return True


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Ingest emails from Gmail Takeout .mbox file"
    )
    parser.add_argument(
        "--mbox",
        required=True,
        help="Path to .mbox file from Google Takeout"
    )
    parser.add_argument(
        "--output",
        default="data/training_emails.csv",
        help="Output CSV file path"
    )
    parser.add_argument(
        "--user-email",
        help="Your email address (to detect sent emails)"
    )
    parser.add_argument(
        "--sent-only",
        action="store_true",
        help="Only extract sent emails (skip inbox)"
    )
    
    args = parser.parse_args()
    
    count = parse_mbox(args.mbox, args.output)
    print(f"Processed {count} emails -> {args.output}")


if __name__ == "__main__":
    main()
```

---

## Output Format

### `data/training_emails.csv`

```csv
thread_id,from,subject,body_text,sent_by_you,timestamp
123abc,"John Doe <john@example.com>","Re: Project update","Hey team, just wanted to...","True","2024-01-15T10:30:00Z"
456def,"Jane Smith <jane@company.com>","Meeting notes","Here are the notes from...","False","2024-01-15T09:15:00Z"
```

| Column | Type | Description |
|--------|------|-------------|
| thread_id | string | Gmail thread ID (or generated hash) |
| from | string | Sender email (with name if available) |
| subject | string | Email subject line |
| body_text | string | Cleaned email body |
| sent_by_you | boolean | True if user sent this email |
| timestamp | ISO 8601 | When email was sent/received |

---

## Tasks

### 1.3.1 User Instructions for Gmail Takeout (1 hr)
- [ ] Document how to export Gmail via Google Takeout
- [ ] Include step-by-step with expected wait time (24-48 hrs)

### 1.3.2 Build Mbox Parser (4 hrs)
- [ ] Parse .mbox file format
- [ ] Handle large files (streaming if needed)
- [ ] Extract all required fields

### 1.3.3 Detect Sent Emails (4 hrs)
- [ ] Detect "Sent" folder
- [ ] Match user's email address in From
- [ ] Handle X-Gmail-Labels

### 1.3.4 Clean Email Data (2 hrs)
- [ ] Strip signatures
- [ ] Remove quoted replies
- [ ] Filter auto-generated emails
- [ ] Handle HTML → text conversion

### 1.3.5 Output CSV (1 hr)
- [ ] Write to CSV with correct schema
- [ ] Handle special characters (encoding)
- [ ] Create data/ directory if needed

### 1.3.6 Tests (2 hrs)
- [ ] Unit tests for each function
- [ ] Test with sample .mbox file
- [ ] Verify CSV output schema

---

## Dependencies

| Dependency | Purpose |
|------------|---------|
| python-email | Standard library email parsing |
| mailbox | Standard library .mbox handling |
| html2text | Convert HTML to plain text |

---

## Testing

```bash
# Basic usage
python src/ingest.py --mbox ~/Downloads/takeout.mbox --output data/training_emails.csv

# With user email (better sent detection)
python src/ingest.py --mbox ~/Downloads/takeout.mbox --user-email your@email.com

# Sent emails only
python src/ingest.py --mbox ~/Downloads/takeout.mbox --sent-only

# Run tests
pytest tests/test_ingest.py -v
```

---

## Google Takeout Instructions (to include in docs)

1. Go to: https://takeout.google.com/
2. Sign in with your Google account
3. Click **"Create a new export"**
4. Select **Gmail** (only)
5. Click **All Mail** (include starred, important, etc.)
6. Click **Next**
7. Export format: **.mbox** (not .json)
8. File frequency: **Once**
9. Click **Create export**
10. Wait 24-48 hours for Google to prepare your download
11. Download and unzip
12. Find the `.mbox` file in the extracted folder

---

## Notes

- Gmail Takeout produces one `.mbox` file per label/folder
- Main files of interest: `All Mail.mbox`, `Sent.mbox`, `INBOX.mbox`
- Large accounts: Takeout can produce GBs of data
- Parser should handle malformed emails gracefully

---

## Definition of Done

1. `src/ingest.py` implements all functions in deliverable spec
2. `python src/ingest.py --mbox <file>` produces valid CSV
3. CSV has correct schema: thread_id, from, subject, body_text, sent_by_you, timestamp
4. Auto-generated emails are filtered out
5. Unit tests pass
6. Google Takeout instructions documented
7. Branch pushed to GitHub
8. PR created
