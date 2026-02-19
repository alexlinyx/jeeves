# Feature Spec: Notification System

**Phase:** 3.3  
**Branch:** `feature/3.3-notification-system`  
**Priority:** P1  
**Est. Time:** 4 hours

---

## Objective

Implement push notification system to alert user when new email drafts are ready for review.

---

## Acceptance Criteria

- [ ] `src/notifier.py` implements notification sender
- [ ] Uses ntfy.sh for notifications
- [ ] Sends notification on new draft created
- [ ] Notification includes subject, sender, preview
- [ ] Tests verify notification structure
- [ ] Unit tests pass

---

## Deliverable

### `src/notifier.py`

```python
"""Notification system for Jeeves."""
import requests
from typing import Dict, Optional


class Notifier:
    """Push notification sender using ntfy.sh."""
    
    DEFAULT_TOPIC = "jeeves-drafts"
    DEFAULT_URL = "https://ntfy.sh"
    
    def __init__(self, topic: str = None, base_url: str = None):
        """Initialize notifier."""
        self.topic = topic or self.DEFAULT_TOPIC
        self.base_url = base_url or self.DEFAULT_URL
    
    def notify_draft_ready(self, subject: str, sender: str, preview: str, draft_id: int) -> bool:
        """Send notification when new draft is ready.
        
        Args:
            subject: Email subject
            sender: Email sender
            preview: Draft preview text
            draft_id: Draft ID
            
        Returns:
            True if successful
        """
        pass
    
    def notify_draft_sent(self, subject: str, recipient: str) -> bool:
        """Send notification when draft is sent."""
        pass
    
    def notify_error(self, error_message: str) -> bool:
        """Send notification on error."""
        pass
    
    def send(self, title: str, message: str, priority: str = "default") -> bool:
        """Send a generic notification."""
        pass
```

---

## Testing Requirements

```python
class TestNotifier:
    def test_file_exists(self):
    def test_import(self):
    def test_class_has_required_methods(self): notify_draft_ready, notify_draft_sent, notify_error, send
    def test_default_topic(self):
    def test_default_url(self):
    def test_notification_structure(self):
```

---

## Tasks

3.3.1 Set up ntfy.sh topic (30 min)
3.3.2 Implement Notifier class (2 hrs)
3.3.3 Write tests (1.5 hrs)

---

## Testing

```bash
pytest tests/test_notifier.py -v
```

---

## Definition of Done

1. `src/notifier.py` works
2. Notifications sent on new draft
3. Tests pass
4. PR created (not merged)
