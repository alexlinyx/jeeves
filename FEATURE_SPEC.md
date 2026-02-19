# Feature Spec: Email Watcher Service

**Phase:** 4.1  
**Branch:** `feature/4.1-email-watcher`  
**Priority:** P0  
**Est. Time:** 6 hours

---

## Objective

Implement background service that polls Gmail for new emails and triggers draft generation automatically.

---

## Acceptance Criteria

- [ ] `src/watcher.py` implements email watcher service
- [ ] Polls Gmail API every 5 minutes for new emails
- [ ] Filters: only unread, non-spam, non-promotional
- [ ] Integrates with GmailClient to fetch emails
- [ ] Integrates with ResponseGenerator to create drafts
- [ ] Stores processed emails in database (marks as processed)
- [ ] Configurable poll interval via environment variable
- [ ] Graceful shutdown on SIGTERM/SIGINT
- [ ] Tests verify polling logic and filtering
- [ ] Unit tests pass

---

## Deliverable

### `src/watcher.py`

```python
"""Email watcher service for Jeeves."""
import os
import signal
import time
import logging
from typing import Optional, Callable
from datetime import datetime


class EmailWatcher:
    """Background service that polls Gmail for new emails."""
    
    DEFAULT_POLL_INTERVAL = 300  # 5 minutes
    DEFAULT_BATCH_SIZE = 10
    
    def __init__(
        self,
        gmail_client=None,
        response_generator=None,
        db=None,
        notifier=None,
        poll_interval: int = None,
        batch_size: int = None,
        on_new_email: Callable = None
    ):
        """Initialize email watcher.
        
        Args:
            gmail_client: GmailClient instance
            response_generator: ResponseGenerator instance
            db: Database instance
            notifier: Notifier instance (optional)
            poll_interval: Seconds between polls (default: 300)
            batch_size: Max emails to process per poll (default: 10)
            on_new_email: Callback for new email processing
        """
        self.gmail_client = gmail_client
        self.response_generator = response_generator
        self.db = db
        self.notifier = notifier
        self.poll_interval = poll_interval or int(os.environ.get('POLL_INTERVAL', self.DEFAULT_POLL_INTERVAL))
        self.batch_size = batch_size or self.DEFAULT_BATCH_SIZE
        self.on_new_email = on_new_email
        self._running = False
        self._last_check = None
    
    def start(self):
        """Start the watcher loop."""
        pass
    
    def stop(self):
        """Stop the watcher loop."""
        pass
    
    def poll(self) -> list:
        """Poll for new emails.
        
        Returns:
            List of new email dicts
        """
        pass
    
    def process_email(self, email: dict) -> Optional[dict]:
        """Process a single email.
        
        Args:
            email: Email dict from GmailClient
            
        Returns:
            Draft dict if draft was created, None otherwise
        """
        pass
    
    def should_process(self, email: dict) -> bool:
        """Determine if email should be processed.
        
        Filters out:
        - Already processed emails
        - Spam
        - Promotional emails
        - Sent emails
        - Automated/no-reply emails
        
        Args:
            email: Email dict
            
        Returns:
            True if email should be processed
        """
        pass
    
    def _setup_signal_handlers(self):
        """Set up graceful shutdown handlers."""
        pass
    
    def get_status(self) -> dict:
        """Get watcher status.
        
        Returns:
            Dict with running status, last check time, stats
        """
        pass


# Email filtering utilities

def is_automated_email(email: dict) -> bool:
    """Check if email is from automated system."""
    pass


def is_promotional_email(email: dict) -> bool:
    """Check if email is promotional/marketing."""
    pass


def extract_sender_domain(email: dict) -> str:
    """Extract domain from sender email address."""
    pass


# Domain patterns to filter out
SKIP_DOMAINS = [
    'noreply', 'no-reply', 'donotreply', 'do-not-reply',
    'notifications', 'notification', 'alerts', 'alert',
    'automated', 'automation', 'bot', 'system'
]

SKIP_PATTERNS = [
    'unsubscribe', 'opt-out', 'opt out',
    'marketing', 'newsletter', 'promotion',
    'auto-generated', 'auto generated', 'automated'
]


def run_watcher():
    """CLI entry point to run the watcher."""
    pass


if __name__ == '__main__':
    run_watcher()
```

---

## Testing Requirements

### Unit Tests (tests/test_watcher.py)

```python
class TestEmailWatcher:
    """Test cases for EmailWatcher."""
    
    def test_file_exists(self):
        """Test watcher.py exists."""
    
    def test_import(self):
        """Test EmailWatcher can be imported."""
    
    def test_class_has_required_methods(self):
        """Test all required methods exist:
        - start, stop, poll, process_email, should_process, get_status
        """
    
    def test_default_poll_interval(self):
        """Test default poll interval is 300 seconds (5 min)."""
    
    def test_default_batch_size(self):
        """Test default batch size is 10."""
    
    def test_should_process_filters_spam(self):
        """Test spam emails are filtered out."""
    
    def test_should_process_filters_promotional(self):
        """Test promotional emails are filtered out."""
    
    def test_should_process_filters_noreply(self):
        """Test noreply emails are filtered out."""
    
    def test_should_process_accepts_valid_email(self):
        """Test valid emails pass the filter."""
    
    def test_get_status_returns_running_state(self):
        """Test get_status returns running state."""
    
    def test_graceful_shutdown(self):
        """Test stop() sets running to False."""
    
    def test_environment_poll_interval(self):
        """Test POLL_INTERVAL env var is respected."""


class TestFilteringFunctions:
    """Test email filtering utilities."""
    
    def test_is_automated_email_detects_noreply(self):
        """Test automated detection for noreply addresses."""
    
    def test_is_promotional_email_detects_newsletter(self):
        """Test promotional detection for newsletters."""
    
    def test_extract_sender_domain(self):
        """Test domain extraction from email address."""
```

---

## Tasks

### 4.1.1 Scaffold Watcher Class (1 hr)
- [ ] Create EmailWatcher class
- [ ] Add initialization with dependencies
- [ ] Set up signal handlers

### 4.1.2 Implement Polling Loop (2 hrs)
- [ ] Implement start/stop methods
- [ ] Implement poll method
- [ ] Add configurable interval

### 4.1.3 Implement Email Filtering (2 hrs)
- [ ] Implement should_process method
- [ ] Add domain-based filtering
- [ ] Add pattern-based filtering
- [ ] Filter out sent emails

### 4.1.4 Integrate Components (1 hr)
- [ ] Connect to GmailClient
- [ ] Connect to ResponseGenerator
- [ ] Connect to Database
- [ ] Optional: Connect to Notifier

---

## Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| src.gmail_client | ✅ Done | GmailClient from 1.2 |
| src.response_generator | ✅ Done | From 2.3 |
| src.db | 🔲 3.2 | Optional, can work without |
| src.notifier | 🔲 3.3 | Optional, can work without |

---

## Configuration

```bash
# Environment variables
POLL_INTERVAL=300        # Seconds between polls
BATCH_SIZE=10            # Max emails per poll
WATCHER_ENABLED=true     # Enable/disable watcher
```

---

## Running the Watcher

```bash
# Run in foreground
python -m src.watcher

# Run with custom interval
POLL_INTERVAL=60 python -m src.watcher

# Run tests
pytest tests/test_watcher.py -v
```

---

## Integration Points

```
┌─────────────────┐
│  EmailWatcher   │
└────────┬────────┘
         │
    ┌────┴────┬──────────┬──────────┐
    ▼         ▼          ▼          ▼
┌───────┐ ┌──────┐ ┌─────────┐ ┌────────┐
│Gmail  │ │Resp  │ │Database │ │Notifier│
│Client │ │Gen   │ │(future) │ │(future)│
└───────┘ └──────┘ └─────────┘ └────────┘
```

---

## Definition of Done

1. `src/watcher.py` implements EmailWatcher class
2. Polling loop works with configurable interval
3. Email filtering correctly excludes spam/promotional/noreply
4. Integrates with GmailClient and ResponseGenerator
5. Graceful shutdown on signals
6. All unit tests pass (minimum 12 tests)
7. Branch pushed to GitHub
8. PR created (not merged until dependencies ready)
