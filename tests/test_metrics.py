"""Tests for MetricsCollector."""
import os
import json
import tempfile
import shutil
import pytest
import time

from src.metrics import (
    MetricPoint,
    MetricSummary,
    MetricsCollector,
    MetricName,
    get_metrics
)


class TestMetricsCollector:
    """Test cases for MetricsCollector."""
    
    @pytest.fixture
    def metrics_collector(self):
        """Create a metrics collector instance."""
        collector = MetricsCollector(persist=False)
        yield collector
    
    def test_file_exists(self):
        """Test metrics.py exists."""
        assert os.path.exists('src/metrics.py')
    
    def test_import(self):
        """Test MetricsCollector can be imported."""
        from src.metrics import MetricsCollector
        assert MetricsCollector is not None
    
    def test_increment(self, metrics_collector):
        """Test counter increment."""
        metrics_collector.increment(MetricName.DRAFTS_CREATED, 1.0)
        
        all_metrics = metrics_collector.get_all_metrics()
        assert MetricName.DRAFTS_CREATED in all_metrics
        assert len(all_metrics[MetricName.DRAFTS_CREATED]) == 1
        assert all_metrics[MetricName.DRAFTS_CREATED][0].value == 1.0
    
    def test_increment_multiple(self, metrics_collector):
        """Test multiple counter increments."""
        metrics_collector.increment(MetricName.DRAFTS_CREATED, 1.0)
        metrics_collector.increment(MetricName.DRAFTS_CREATED, 1.0)
        metrics_collector.increment(MetricName.DRAFTS_CREATED, 1.0)
        
        all_metrics = metrics_collector.get_all_metrics()
        assert len(all_metrics[MetricName.DRAFTS_CREATED]) == 3
    
    def test_gauge(self, metrics_collector):
        """Test gauge metric."""
        metrics_collector.gauge(MetricName.CONFIDENCE_SCORE, 0.85)
        
        all_metrics = metrics_collector.get_all_metrics()
        assert MetricName.CONFIDENCE_SCORE in all_metrics
        assert all_metrics[MetricName.CONFIDENCE_SCORE][0].value == 0.85
    
    def test_timing(self, metrics_collector):
        """Test timing metric."""
        metrics_collector.timing(MetricName.PROCESSING_TIME_MS, 1500.5)
        
        all_metrics = metrics_collector.get_all_metrics()
        assert MetricName.PROCESSING_TIME_MS in all_metrics
        assert all_metrics[MetricName.PROCESSING_TIME_MS][0].value == 1500.5
    
    def test_get_summary(self, metrics_collector):
        """Test summary calculation."""
        metrics_collector.timing(MetricName.PROCESSING_TIME_MS, 1000.0)
        metrics_collector.timing(MetricName.PROCESSING_TIME_MS, 2000.0)
        metrics_collector.timing(MetricName.PROCESSING_TIME_MS, 3000.0)
        
        summary = metrics_collector.get_summary(MetricName.PROCESSING_TIME_MS)
        
        assert summary.name == MetricName.PROCESSING_TIME_MS
        assert summary.count == 3
        assert summary.sum == 6000.0
        assert summary.min == 1000.0
        assert summary.max == 3000.0
        assert summary.avg == 2000.0
    
    def test_get_summary_empty(self, metrics_collector):
        """Test summary with no data."""
        summary = metrics_collector.get_summary(MetricName.DRAFTS_CREATED)
        
        assert summary.name == MetricName.DRAFTS_CREATED
        assert summary.count == 0
        assert summary.sum == 0.0
    
    def test_get_dashboard_data(self, metrics_collector):
        """Test dashboard data format."""
        # Add some test data
        metrics_collector.increment(MetricName.DRAFTS_CREATED)
        metrics_collector.increment(MetricName.DRAFTS_SENT)
        metrics_collector.increment(MetricName.EMAILS_PROCESSED)
        metrics_collector.timing(MetricName.PROCESSING_TIME_MS, 1000.0)
        metrics_collector.gauge(MetricName.CONFIDENCE_SCORE, 0.85)
        
        dashboard = metrics_collector.get_dashboard_data()
        
        assert 'drafts_created_total' in dashboard
        assert 'drafts_sent_total' in dashboard
        assert 'avg_processing_time_ms' in dashboard
        assert 'avg_confidence_score' in dashboard
        assert 'uptime_seconds' in dashboard
        
        assert dashboard['drafts_created_total'] == 1
        assert dashboard['drafts_sent_total'] == 1
        assert dashboard['avg_processing_time_ms'] == 1000.0
        assert dashboard['avg_confidence_score'] == 0.85
    
    def test_metric_persistence(self):
        """Test metrics persist to file."""
        temp_dir = tempfile.mkdtemp()
        metrics_file = os.path.join(temp_dir, "test_metrics.jsonl")
        
        try:
            collector = MetricsCollector(persist=True)
            collector.METRICS_FILE = metrics_file
            
            collector.increment(MetricName.DRAFTS_CREATED, 1.0)
            
            # Give it a moment to write
            time.sleep(0.1)
            
            assert os.path.exists(metrics_file)
            
            with open(metrics_file, 'r') as f:
                line = f.readline()
                entry = json.loads(line)
                assert entry['name'] == MetricName.DRAFTS_CREATED
                assert entry['value'] == 1.0
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_reset(self, metrics_collector):
        """Test reset clears all metrics."""
        metrics_collector.increment(MetricName.DRAFTS_CREATED)
        metrics_collector.increment(MetricName.DRAFTS_SENT)
        
        metrics_collector.reset()
        
        all_metrics = metrics_collector.get_all_metrics()
        assert len(all_metrics) == 0
    
    def test_tags(self, metrics_collector):
        """Test metrics with tags."""
        metrics_collector.increment(
            MetricName.DRAFTS_CREATED,
            1.0,
            tags={"tone": "formal", "confidence_bucket": "high"}
        )
        
        all_metrics = metrics_collector.get_all_metrics()
        assert len(all_metrics[MetricName.DRAFTS_CREATED]) == 1
        assert all_metrics[MetricName.DRAFTS_CREATED][0].tags == {"tone": "formal", "confidence_bucket": "high"}
    
    def test_get_all_metrics(self, metrics_collector):
        """Test get_all_metrics returns all data."""
        metrics_collector.increment(MetricName.DRAFTS_CREATED)
        metrics_collector.increment(MetricName.DRAFTS_SENT)
        metrics_collector.gauge(MetricName.CONFIDENCE_SCORE, 0.9)
        
        all_metrics = metrics_collector.get_all_metrics()
        
        assert MetricName.DRAFTS_CREATED in all_metrics
        assert MetricName.DRAFTS_SENT in all_metrics
        assert MetricName.CONFIDENCE_SCORE in all_metrics
        assert len(all_metrics) == 3
    
    def test_error_rate_calculation(self, metrics_collector):
        """Test error rate calculation."""
        # Add some emails and errors
        metrics_collector.increment(MetricName.EMAILS_PROCESSED)
        metrics_collector.increment(MetricName.EMAILS_PROCESSED)
        metrics_collector.increment(MetricName.EMAILS_PROCESSED)
        metrics_collector.increment(MetricName.ERRORS)
        
        dashboard = metrics_collector.get_dashboard_data()
        
        assert dashboard['error_rate'] == pytest.approx(1/3, rel=0.01)
    
    def test_metric_name_constants(self):
        """Test MetricName constants are defined."""
        assert MetricName.DRAFTS_CREATED == "drafts.created"
        assert MetricName.DRAFTS_SENT == "drafts.sent"
        assert MetricName.DRAFTS_EDITED == "drafts.edited"
        assert MetricName.DRAFTS_REJECTED == "drafts.rejected"
        assert MetricName.EMAILS_PROCESSED == "emails.processed"
        assert MetricName.PROCESSING_TIME_MS == "processing.time_ms"
        assert MetricName.CONFIDENCE_SCORE == "confidence.score"
        assert MetricName.ERRORS == "errors.total"
    
    def test_get_metrics_function(self):
        """Test get_metrics global function."""
        metrics = get_metrics()
        assert metrics is not None
        assert isinstance(metrics, MetricsCollector)
    
    def test_metric_point_creation(self):
        """Test MetricPoint dataclass creation."""
        point = MetricPoint(
            timestamp="2024-01-15T10:30:00.123Z",
            value=1.0,
            tags={"key": "value"}
        )
        assert point.timestamp == "2024-01-15T10:30:00.123Z"
        assert point.value == 1.0
        assert point.tags == {"key": "value"}
    
    def test_metric_summary_creation(self):
        """Test MetricSummary dataclass creation."""
        summary = MetricSummary(
            name="test.metric",
            count=10,
            sum=100.0,
            min=5.0,
            max=20.0,
            avg=10.0,
            period_seconds=3600
        )
        assert summary.name == "test.metric"
        assert summary.count == 10
        assert summary.sum == 100.0
        assert summary.min == 5.0
        assert summary.max == 20.0
        assert summary.avg == 10.0
        assert summary.period_seconds == 3600
