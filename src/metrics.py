"""Metrics collection for Jeeves."""
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict
from collections import defaultdict
from pathlib import Path
import os


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
        self._metrics: Dict[str, List[MetricPoint]] = defaultdict(list)
        self._lock = threading.Lock()
        self._persist = persist
        self._start_time = time.time()
        
        # Create log directory if it doesn't exist
        if self._persist:
            Path("logs").mkdir(parents=True, exist_ok=True)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO 8601 format."""
        return datetime.utcnow().isoformat(timespec='milliseconds') + 'Z'
    
    def _get_metric_key(self, name: str, tags: Dict[str, str] = None) -> str:
        """Get a unique key for a metric with tags."""
        if not tags:
            return name
        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}#{tag_str}"
    
    def increment(self, name: str, value: float = 1.0, tags: Dict[str, str] = None):
        """Increment a counter metric."""
        with self._lock:
            point = MetricPoint(
                timestamp=self._get_timestamp(),
                value=value,
                tags=tags or {}
            )
            self._metrics[name].append(point)
            if self._persist:
                self._persist_to_file(name, point)
    
    def gauge(self, name: str, value: float, tags: Dict[str, str] = None):
        """Set a gauge metric."""
        with self._lock:
            point = MetricPoint(
                timestamp=self._get_timestamp(),
                value=value,
                tags=tags or {}
            )
            self._metrics[name].append(point)
            if self._persist:
                self._persist_to_file(name, point)
    
    def timing(self, name: str, duration_ms: float, tags: Dict[str, str] = None):
        """Record a timing metric."""
        with self._lock:
            point = MetricPoint(
                timestamp=self._get_timestamp(),
                value=duration_ms,
                tags=tags or {}
            )
            self._metrics[name].append(point)
            if self._persist:
                self._persist_to_file(name, point)
    
    def get_summary(self, name: str, period_seconds: int = 3600) -> MetricSummary:
        """Get summary of metric over time period."""
        with self._lock:
            points = self._metrics.get(name, [])
            if not points:
                return MetricSummary(
                    name=name,
                    count=0,
                    sum=0.0,
                    min=0.0,
                    max=0.0,
                    avg=0.0,
                    period_seconds=period_seconds
                )
            
            # Filter by time period
            cutoff = datetime.utcnow() - timedelta(seconds=period_seconds)
            cutoff_str = cutoff.isoformat(timespec='milliseconds') + 'Z'
            
            filtered_points = [p for p in points if p.timestamp >= cutoff_str]
            
            if not filtered_points:
                return MetricSummary(
                    name=name,
                    count=0,
                    sum=0.0,
                    min=0.0,
                    max=0.0,
                    avg=0.0,
                    period_seconds=period_seconds
                )
            
            values = [p.value for p in filtered_points]
            return MetricSummary(
                name=name,
                count=len(values),
                sum=sum(values),
                min=min(values),
                max=max(values),
                avg=sum(values) / len(values),
                period_seconds=period_seconds
            )
    
    def get_all_metrics(self) -> Dict[str, List[MetricPoint]]:
        """Get all collected metrics."""
        with self._lock:
            return dict(self._metrics)
    
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
        with self._lock:
            uptime = time.time() - self._start_time
            
            # Get totals
            drafts_created = len(self._metrics.get(MetricName.DRAFTS_CREATED, []))
            drafts_sent = len(self._metrics.get(MetricName.DRAFTS_SENT, []))
            drafts_edited = len(self._metrics.get(MetricName.DRAFTS_EDITED, []))
            drafts_rejected = len(self._metrics.get(MetricName.DRAFTS_REJECTED, []))
            emails_processed = len(self._metrics.get(MetricName.EMAILS_PROCESSED, []))
            total_errors = len(self._metrics.get(MetricName.ERRORS, []))
            
            # Calculate averages
            processing_times = self._metrics.get(MetricName.PROCESSING_TIME_MS, [])
            if processing_times:
                avg_processing_time = sum(p.value for p in processing_times) / len(processing_times)
            else:
                avg_processing_time = 0.0
            
            confidence_scores = self._metrics.get(MetricName.CONFIDENCE_SCORE, [])
            if confidence_scores:
                avg_confidence = sum(p.value for p in confidence_scores) / len(confidence_scores)
            else:
                avg_confidence = 0.0
            
            # Calculate error rate (errors per email processed)
            if emails_processed > 0:
                error_rate = total_errors / emails_processed
            else:
                error_rate = 0.0
            
            return {
                "drafts_created_total": drafts_created,
                "drafts_sent_total": drafts_sent,
                "drafts_edited_total": drafts_edited,
                "drafts_rejected_total": drafts_rejected,
                "emails_processed_total": emails_processed,
                "avg_processing_time_ms": round(avg_processing_time, 2),
                "avg_confidence_score": round(avg_confidence, 2),
                "error_rate": round(error_rate, 4),
                "uptime_seconds": round(uptime, 2)
            }
    
    def reset(self):
        """Reset all metrics."""
        with self._lock:
            self._metrics.clear()
            self._start_time = time.time()
    
    def _persist_to_file(self, name: str, point: MetricPoint):
        """Persist metric to file."""
        try:
            log_entry = {
                "timestamp": point.timestamp,
                "name": name,
                "value": point.value,
                "tags": point.tags
            }
            with open(self.METRICS_FILE, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            import sys
            print(f"Failed to persist metric: {e}", file=sys.stderr)


# Convenience metric functions
METRICS: Optional[MetricsCollector] = None


def get_metrics() -> MetricsCollector:
    """Get global metrics collector."""
    global METRICS
    if METRICS is None:
        METRICS = MetricsCollector()
    return METRICS


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
