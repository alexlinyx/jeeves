# Feature Spec: End-to-End Testing

**Phase:** 5.1  
**Branch:** `feature/5.1-e2e-testing`  
**Priority:** P1  
**Est. Time:** 8 hours

---

## Objective

Implement comprehensive end-to-end tests covering the full email processing pipeline from email receipt to draft sending.

---

## Acceptance Criteria

- [ ] `tests/e2e/` directory created with test suite
- [ ] Test: email → draft generation → approval → send flow
- [ ] Test: each tone mode (casual, formal, concise, match_style)
- [ ] Test: error handling (network failures, API limits)
- [ ] Test: confidence scoring and auto-send logic
- [ ] Test: filtering (spam, promotional, noreply)
- [ ] Test fixtures for sample emails
- [ ] CI integration (GitHub Actions)
- [ ] 95% success rate target on test suite
- [ ] All E2E tests pass

---

## Deliverable

### `tests/e2e/conftest.py`

```python
"""E2E test configuration and fixtures."""
import pytest
from unittest.mock import Mock, MagicMock
from src.gmail_client import GmailClient
from src.llm import LLM
from src.rag import RAGPipeline
from src.response_generator import ResponseGenerator
from src.confidence import ConfidenceScorer
from src.db import Database
from src.watcher import EmailWatcher


@pytest.fixture
def sample_emails():
    """Sample email fixtures for testing."""
    return [
        {
            "id": "email_001",
            "thread_id": "thread_001",
            "from": "colleague@company.com",
            "to": "me@example.com",
            "subject": "Project Update Request",
            "body_text": "Hey, can you give me an update on the project status?",
            "date": "2024-01-15T10:00:00Z"
        },
        {
            "id": "email_002",
            "thread_id": "thread_002",
            "from": "client@external.com",
            "to": "me@example.com",
            "subject": "Meeting Tomorrow",
            "body_text": "I'd like to schedule a meeting tomorrow at 2pm. Does that work?",
            "date": "2024-01-15T11:00:00Z"
        },
        {
            "id": "email_003",
            "thread_id": "thread_003",
            "from": "noreply@newsletter.com",
            "to": "me@example.com",
            "subject": "Your Weekly Newsletter",
            "body_text": "Here are this week's top stories...",
            "date": "2024-01-15T12:00:00Z"
        },
        {
            "id": "email_004",
            "thread_id": "thread_004",
            "from": "spam@unknown.com",
            "to": "me@example.com",
            "subject": "CONGRATULATIONS YOU WON!!!",
            "body_text": "Click here to claim your prize...",
            "date": "2024-01-15T13:00:00Z"
        },
        {
            "id": "email_005",
            "thread_id": "thread_005",
            "from": "bank@financial.com",
            "to": "me@example.com",
            "subject": "Wire Transfer Confirmation",
            "body_text": "Please confirm the wire transfer of $50,000...",
            "date": "2024-01-15T14:00:00Z"
        }
    ]


@pytest.fixture
def mock_gmail_client(sample_emails):
    """Mock Gmail client for testing."""
    pass


@pytest.fixture
def mock_llm():
    """Mock LLM for deterministic testing."""
    pass


@pytest.fixture
def mock_rag():
    """Mock RAG pipeline for testing."""
    pass


@pytest.fixture
def test_db(tmp_path):
    """Temporary database for testing."""
    pass


@pytest.fixture
def e2e_pipeline(mock_gmail_client, mock_llm, mock_rag, test_db):
    """Complete E2E pipeline with mocked components."""
    pass
```

### `tests/e2e/test_full_flow.py`

```python
"""End-to-end tests for complete email processing flow."""
import pytest
from unittest.mock import Mock, patch, MagicMock


class TestFullFlow:
    """Test complete email processing flow."""
    
    def test_email_to_draft_generation(self, e2e_pipeline, sample_emails):
        """Test: Email received → Draft generated."""
        pass
    
    def test_draft_to_approval_to_send(self, e2e_pipeline, sample_emails):
        """Test: Draft created → User approves → Email sent."""
        pass
    
    def test_draft_edit_and_send(self, e2e_pipeline, sample_emails):
        """Test: Draft created → User edits → Email sent."""
        pass
    
    def test_draft_rejection(self, e2e_pipeline, sample_emails):
        """Test: Draft created → User rejects → No email sent."""
        pass


class TestToneModes:
    """Test each tone mode produces appropriate responses."""
    
    def test_casual_tone(self, e2e_pipeline, sample_emails):
        """Test casual tone generates informal response."""
        pass
    
    def test_formal_tone(self, e2e_pipeline, sample_emails):
        """Test formal tone generates professional response."""
        pass
    
    def test_concise_tone(self, e2e_pipeline, sample_emails):
        """Test concise tone generates brief response."""
        pass
    
    def test_match_style_tone(self, e2e_pipeline, sample_emails):
        """Test match_style tone mimics user's style."""
        pass


class TestFiltering:
    """Test email filtering logic."""
    
    def test_filter_promotional_email(self, e2e_pipeline, sample_emails):
        """Test promotional emails are filtered out."""
        pass
    
    def test_filter_spam_email(self, e2e_pipeline, sample_emails):
        """Test spam emails are filtered out."""
        pass
    
    def test_filter_noreply_email(self, e2e_pipeline, sample_emails):
        """Test noreply emails are filtered out."""
        pass
    
    def test_accept_valid_email(self, e2e_pipeline, sample_emails):
        """Test valid emails are processed."""
        pass


class TestConfidenceScoring:
    """Test confidence scoring and auto-send logic."""
    
    def test_high_confidence_auto_send(self, e2e_pipeline, sample_emails):
        """Test high confidence score triggers auto-send."""
        pass
    
    def test_low_confidence_manual_review(self, e2e_pipeline, sample_emails):
        """Test low confidence score requires manual review."""
        pass
    
    def test_financial_email_no_auto_send(self, e2e_pipeline, sample_emails):
        """Test financial emails never auto-send."""
        pass
    
    def test_urgent_email_manual_review(self, e2e_pipeline, sample_emails):
        """Test urgent emails require manual review."""
        pass


class TestErrorHandling:
    """Test error handling and recovery."""
    
    def test_gmail_api_failure(self, e2e_pipeline):
        """Test handling of Gmail API failures."""
        pass
    
    def test_llm_timeout(self, e2e_pipeline):
        """Test handling of LLM timeouts."""
        pass
    
    def test_rag_index_corruption(self, e2e_pipeline):
        """Test handling of RAG index issues."""
        pass
    
    def test_database_connection_failure(self, e2e_pipeline):
        """Test handling of database failures."""
        pass
    
    def test_rate_limiting(self, e2e_pipeline):
        """Test handling of API rate limits."""
        pass
    
    def test_network_failure_recovery(self, e2e_pipeline):
        """Test recovery from network failures."""
        pass


class TestLoadTesting:
    """Test system under load."""
    
    def test_batch_email_processing(self, e2e_pipeline):
        """Test processing 100 emails in batch."""
        pass
    
    def test_concurrent_draft_generation(self, e2e_pipeline):
        """Test concurrent draft generation."""
        pass
    
    def test_memory_usage_under_load(self, e2e_pipeline):
        """Test memory doesn't leak under load."""
        pass
```

### `tests/e2e/test_integration.py`

```python
"""Integration tests between components."""
import pytest


class TestGmailRAGIntegration:
    """Test Gmail client + RAG integration."""
    
    def test_email_indexing(self, mock_gmail_client, mock_rag):
        """Test emails are properly indexed in RAG."""
        pass
    
    def test_context_retrieval(self, mock_gmail_client, mock_rag):
        """Test RAG retrieves relevant context for email."""
        pass


class TestLLMResponseIntegration:
    """Test LLM + Response Generator integration."""
    
    def test_response_generation(self, mock_llm, mock_rag):
        """Test response generator uses LLM correctly."""
        pass
    
    def test_context_injection(self, mock_llm, mock_rag):
        """Test context is injected into prompts."""
        pass


class TestDatabaseIntegration:
    """Test database integration."""
    
    def test_draft_persistence(self, test_db):
        """Test drafts persist across restarts."""
        pass
    
    def test_email_deduplication(self, test_db):
        """Test same email not processed twice."""
        pass
```

### `.github/workflows/e2e-tests.yml`

```yaml
name: E2E Tests

on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]

jobs:
  e2e-tests:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-asyncio
      
      - name: Run E2E tests
        run: |
          pytest tests/e2e/ -v --cov=src --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
```

---

## Test Fixtures

### `tests/e2e/fixtures/emails/`

```
tests/e2e/fixtures/emails/
├── simple_request.json      # Simple info request
├── meeting_invite.json      # Meeting invitation
├── project_update.json      # Project status request
├── financial_email.json     # Financial content (no auto-send)
├── urgent_email.json        # Urgent content
├── spam_email.json          # Spam (filtered)
├── newsletter.json          # Newsletter (filtered)
└── noreply_email.json       # Noreply sender (filtered)
```

### Sample fixture file

```json
{
  "id": "fixture_001",
  "thread_id": "thread_fixture_001",
  "from": "test@example.com",
  "to": "me@example.com",
  "subject": "Test Email Subject",
  "body_text": "This is a test email body.",
  "date": "2024-01-15T10:00:00Z",
  "expected": {
    "should_process": true,
    "min_confidence": 0.5,
    "suggested_tone": "casual"
  }
}
```

---

## Testing Requirements

### Test Coverage

| Component | Target Coverage |
|-----------|-----------------|
| Email flow | 100% |
| Tone modes | 100% |
| Filtering | 100% |
| Confidence | 100% |
| Error handling | 80% |
| Load tests | Basic |

### Success Metrics

| Metric | Target |
|--------|--------|
| Test pass rate | 95% |
| Code coverage | 80% |
| E2E test time | <5 min |

---

## Tasks

### 5.1.1 Set Up E2E Infrastructure (2 hrs)
- [ ] Create tests/e2e/ directory
- [ ] Set up pytest fixtures
- [ ] Create mock components
- [ ] Create sample email fixtures

### 5.1.2 Write Full Flow Tests (2 hrs)
- [ ] Test email → draft flow
- [ ] Test approval → send flow
- [ ] Test tone modes
- [ ] Test filtering

### 5.1.3 Write Confidence Tests (1 hr)
- [ ] Test scoring logic
- [ ] Test auto-send rules
- [ ] Test safety rules

### 5.1.4 Write Error Handling Tests (2 hrs)
- [ ] Test API failures
- [ ] Test timeouts
- [ ] Test rate limits

### 5.1.5 CI Integration (1 hr)
- [ ] Create GitHub Actions workflow
- [ ] Add coverage reporting
- [ ] Set up test artifacts

---

## Running Tests

```bash
# Run all E2E tests
pytest tests/e2e/ -v

# Run with coverage
pytest tests/e2e/ -v --cov=src --cov-report=html

# Run specific test class
pytest tests/e2e/test_full_flow.py -v

# Run with fixtures
pytest tests/e2e/ --fixtures

# Run load tests
pytest tests/e2e/test_load_testing.py -v -s
```

---

## Definition of Done

1. `tests/e2e/` directory with full test suite
2. All 4 tone modes tested
3. Error handling tests for 5+ scenarios
4. Filtering tests for spam/promotional/noreply
5. Confidence scoring tests
6. CI integration with GitHub Actions
7. 95% test pass rate
8. 80% code coverage
9. Branch pushed to GitHub
10. PR created