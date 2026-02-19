# Feature Spec: Monitoring & Logging

**Phase:** 4.3  
**Branch:** `feature/4.3-monitoring-logging`  
**Priority:** P2  
**Est. Time:** 6 hours

---

## Objective

Implement structured logging and metrics collection to track system performance, draft quality, and operational health.

---

## Acceptance Criteria

- [ ] `src/logger.py` implements structured logging
- [ ] `src/metrics.py` implements metrics collection
- [ ] Uses `structlog` for JSON-formatted logs
- [ ] Logs to `logs/jeeves.jsonl`
- [ ] Tracks: drafts created, sent, edited, rejected
- [ ] Tracks: processing times, error rates
- [ ] Provides metrics endpoint for dashboard
- [ ] Tests verify logging and metrics
- [ ] Unit tests pass

---

## Deliverable

### `src/logger.py`

```python
"""Structured logging for Jeeves."""
import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class LogLevel(Enum):
    """Log levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class LogEntry:
    """Structured log entry."""
    timestamp: str
    level: str
    message: str
    component: str
    action: str
    data: Dict[str, Any]
    duration_ms: Optional[float] = None
    error: Optional[str] = None
    trace_id: Optional[str] = None


class JeevesLogger:
    """Structured logger for Jeeves operations."""
    
    DEFAULT_LOG_DIR = "logs"
    DEFAULT_LOG_FILE = "jeeves.jsonl"
    
    def __init__(
        self,
        log_dir: str = None,
        log_file: str = None,
        component: str = "jeeves",
        level: LogLevel = LogLevel.INFO
    ):
        """Initialize logger.
        
        Args:
            log_dir: Directory for log files
            log_file: Log file name
            component: Component name for all logs
            level: Minimum log level
        """
        pass
    
    def info(self, message: str, action: str, data: Dict = None, **kwargs):
        """Log info level."""
        pass
    
    def warning(self, message: str, action: str, data: Dict = None, **kwargs):
        """Log warning level."""
        pass
    
    def error(self, message: str, action: str, error: Exception = None, data: Dict = None, **kwargs):
        """Log error level."""
        pass
    
    def debug(self, message: str, action: str, data: Dict = None, **kwargs):
        """Log debug level."""
        pass
    
    def log_draft_created(self, draft_id: int, email_id: int, tone: str, confidence: float):
        """Log draft creation."""
        pass
    
    def log_draft_sent(self, draft_id: int, subject: str, recipient: str):
        """Log draft sent."""
        pass
    
    def log_draft_edited(self, draft_id: int, edits_count: int):
        """Log draft edited."""
        pass
    
    def log_draft_rejected(self, draft_id: int, reason: str = None):
        """Log draft rejected."""
        pass
    
    def log_email_processed(self, email_id: str, processing_time_ms: float):
        """Log email processing."""
        pass
    
    def log_error(self, component: str, error: Exception, context: Dict = None):
        """Log error with context."""
        pass
    
    def _write(self, entry: LogEntry):
        """Write log entry to file."""
        pass


# Global logger instance
_logger: Optional[JeevesLogger] = None


def get_logger(component: str = None) -> JeevesLogger:
    """Get or create logger instance."""
    pass


def configure_logging(log_dir: str = None, level: LogLevel = LogLevel.INFO):
    """Configure global logging."""
    pass
```

### `src/metrics.py`

```python
"""Metrics collection for Jeeves."""
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from collections import defaultdict
from pathlib import Path
import threading


@dataclass
class MetricPoint:
    """Single metric data point."""
    timestamp: str
    value: float
    tags: Dict[str, str] = field(default_factory=dict)


@dataclass
class MetricSummary:
    """Summary of metric over time period."""
    name: str
    count: int
    sum: float
    min: float
    max: float
    avg: float
    period_seconds: int


class MetricsCollector:
    """Collect and aggregate metrics."""
    
    METRICS_FILE = "logs/metrics.jsonl"
    
    def __init__(self, persist: bool = True):
        """Initialize metrics collector.
        
        Args:
            persist: Whether to persist metrics to file
        """
        pass
    
    def increment(self, name: str, value: float = 1.0, tags: Dict[str, str] = None):
        """Increment a counter metric."""
        pass
    
    def gauge(self, name: str, value: float, tags: Dict[str, str] = None):
        """Set a gauge metric."""
        pass
    
    def timing(self, name: str, duration_ms: float, tags: Dict[str, str] = None):
        """Record a timing metric."""
        pass
    
    def get_summary(self, name: str, period_seconds: int = 3600) -> MetricSummary:
        """Get summary of metric over time period."""
        pass
    
    def get_all_metrics(self) -> Dict[str, List[MetricPoint]]:
        """Get all collected metrics."""
        pass
    
    def get_dashboard_data(self) -> Dict:
        """Get metrics formatted for dashboard display.
        
        Returns:
            Dict with:
            - drafts_created_total
            - drafts_sent_total
            - drafts_edited_total
            - drafts_rejected_total
            - avg_processing_time_ms
            - avg_confidence_score
            - error_rate
            - uptime_seconds
        """
        pass
    
    def reset(self):
        """Reset all metrics."""
        pass
    
    def _persist(self, name: str, point: MetricPoint):
        """Persist metric to file."""
        pass


# Convenience metric functions
METRICS = None


def get_metrics() -> MetricsCollector:
    """Get global metrics collector."""
    pass


# Metric names as constants
class MetricName:
    """Standard metric names."""
    DRAFTS_CREATED = "drafts.created"
    DRAFTS_SENT = "drafts.sent"
    DRAFTS_EDITED = "drafts.edited"
    DRAFTS_REJECTED = "drafts.rejected"
    EMAILS_PROCESSED = "emails.processed"
    PROCESSING_TIME_MS = "processing.time_ms"
    CONFIDENCE_SCORE = "confidence.score"
    ERRORS = "errors.total"
    WATCHER_POLLS = "watcher.polls"
    LLM_GENERATIONS = "llm.generations"
    RAG_QUERIES = "rag.queries"
```

---

## Testing Requirements

### Unit Tests (tests/test_logger.py)

```python
class TestJeevesLogger:
    """Test cases for JeevesLogger."""
    
    def test_file_exists(self):
        """Test logger.py exists."""
    
    def test_import(self):
        """Test JeevesLogger can be imported."""
    
    def test_log_entry_creation(self):
        """Test LogEntry dataclass creation."""
    
    def test_info_logging(self):
        """Test info level logging."""
    
    def test_error_logging(self):
        """Test error level logging with exception."""
    
    def test_log_file_created(self):
        """Test log file is created."""
    
    def test_json_format(self):
        """Test logs are valid JSON."""
    
    def test_log_draft_created(self):
        """Test log_draft_created convenience method."""
    
    def test_log_draft_sent(self):
        """Test log_draft_sent convenience method."""
    
    def test_timestamp_format(self):
        """Test timestamp is ISO 8601 format."""


class TestMetricsCollector:
    """Test cases for MetricsCollector."""
    
    def test_file_exists(self):
        """Test metrics.py exists."""
    
    def test_import(self):
        """Test MetricsCollector can be imported."""
    
    def test_increment(self):
        """Test counter increment."""
    
    def test_gauge(self):
        """Test gauge metric."""
    
    def test_timing(self):
        """Test timing metric."""
    
    def test_get_summary(self):
        """Test summary calculation."""
    
    def test_get_dashboard_data(self):
        """Test dashboard data format."""
    
    def test_metric_persistence(self):
        """Test metrics persist to file."""
```

---

## Tasks

### 4.3.1 Set Up Structured Logging (2 hrs)
- [ ] Install structlog
- [ ] Implement JeevesLogger class
- [ ] Implement LogEntry dataclass
- [ ] Add convenience methods

### 4.3.2 Implement Metrics Collection (2 hrs)
- [ ] Implement MetricsCollector class
- [ ] Add counter, gauge, timing methods
- [ ] Add summary calculations
- [ ] Add persistence

### 4.3.3 Add Dashboard Integration (1 hr)
- [ ] Implement get_dashboard_data()
- [ ] Add uptime tracking
- [ ] Add error rate calculation

### 4.3.4 Write Tests (1 hr)
- [ ] Write logger tests
- [ ] Write metrics tests
- [ ] Test file persistence

---

## Log Format

```json
{
  "timestamp": "2024-01-15T10:30:00.123Z",
  "level": "info",
  "message": "Draft created",
  "component": "response_generator",
  "action": "draft_created",
  "data": {
    "draft_id": 123,
    "email_id": 456,
    "tone": "formal",
    "confidence": 0.85
  },
  "duration_ms": 1250.5,
  "trace_id": "abc-123-def"
}
```

---

## Metrics Format

```json
{
  "timestamp": "2024-01-15T10:30:00.123Z",
  "name": "drafts.created",
  "value": 1.0,
  "tags": {
    "tone": "formal",
    "confidence_bucket": "high"
  }
}
```

---

## Dashboard Metrics

| Metric | Description | Type |
|--------|-------------|------|
| `drafts.created` | Total drafts created | Counter |
| `drafts.sent` | Total drafts sent | Counter |
| `drafts.edited` | Total drafts edited | Counter |
| `drafts.rejected` | Total drafts rejected | Counter |
| `processing.time_ms` | Email processing time | Timing |
| `confidence.score` | Draft confidence scores | Gauge |
| `errors.total` | Total errors | Counter |

---

## Dependencies

```bash
pip install structlog
```

---

## Running Tests

```bash
pytest tests/test_logger.py tests/test_metrics.py -v
```

---

## Definition of Done

1. `src/logger.py` implements structured logging
2. `src/metrics.py` implements metrics collection
3. Logs written to `logs/jeeves.jsonl`
4. Metrics persisted to `logs/metrics.jsonl`
5. Convenience methods for common operations
6. All unit tests pass
7. Branch pushed to GitHub
8. PR created