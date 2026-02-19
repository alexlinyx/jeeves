"""Tests for JeevesLogger."""
import os
import json
import tempfile
import shutil
import pytest
from datetime import datetime
from pathlib import Path

from src.logger import (
    LogLevel,
    LogEntry,
    JeevesLogger,
    get_logger,
    configure_logging
)


class TestJeevesLogger:
    """Test cases for JeevesLogger."""
    
    @pytest.fixture
    def temp_log_dir(self):
        """Create a temporary directory for logs."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_file_exists(self):
        """Test logger.py exists."""
        assert os.path.exists('src/logger.py')
    
    def test_import(self):
        """Test JeevesLogger can be imported."""
        from src.logger import JeevesLogger
        assert JeevesLogger is not None
    
    def test_log_entry_creation(self):
        """Test LogEntry dataclass creation."""
        entry = LogEntry(
            timestamp="2024-01-15T10:30:00.123Z",
            level="info",
            message="Test message",
            component="test",
            action="test_action",
            data={"key": "value"}
        )
        assert entry.timestamp == "2024-01-15T10:30:00.123Z"
        assert entry.level == "info"
        assert entry.message == "Test message"
        assert entry.component == "test"
        assert entry.data == {"key": "value"}
    
    def test_info_logging(self, temp_log_dir):
        """Test info level logging."""
        log_file = "test.log"
        logger = JeevesLogger(log_dir=temp_log_dir, log_file=log_file, component="test")
        
        logger.info("Test info message", action="test", data={"key": "value"})
        
        logger.close()
        
        log_path = os.path.join(temp_log_dir, log_file)
        assert os.path.exists(log_path)
        
        with open(log_path, 'r') as f:
            line = f.readline()
            entry = json.loads(line)
            assert entry['level'] == 'info'
            assert entry['message'] == 'Test info message'
            assert entry['action'] == 'test'
            assert entry['data'] == {"key": "value"}
    
    def test_error_logging(self, temp_log_dir):
        """Test error level logging with exception."""
        log_file = "test.log"
        logger = JeevesLogger(log_dir=temp_log_dir, log_file=log_file, component="test")
        
        try:
            raise ValueError("Test error")
        except ValueError as e:
            logger.error("Error occurred", action="error_test", error=e, data={"context": "test"})
        
        logger.close()
        
        log_path = os.path.join(temp_log_dir, log_file)
        with open(log_path, 'r') as f:
            line = f.readline()
            entry = json.loads(line)
            assert entry['level'] == 'error'
            assert 'ValueError' in entry['error']
            assert 'Test error' in entry['error']
    
    def test_log_file_created(self, temp_log_dir):
        """Test log file is created."""
        log_file = "test.log"
        logger = JeevesLogger(log_dir=temp_log_dir, log_file=log_file, component="test")
        
        logger.info("Test", action="test")
        logger.close()
        
        log_path = os.path.join(temp_log_dir, log_file)
        assert os.path.exists(log_path)
        assert os.path.getsize(log_path) > 0
    
    def test_json_format(self, temp_log_dir):
        """Test logs are valid JSON."""
        log_file = "test.log"
        logger = JeevesLogger(log_dir=temp_log_dir, log_file=log_file, component="test")
        
        logger.info("Test message", action="test", data={"nested": {"key": "value"}})
        logger.close()
        
        log_path = os.path.join(temp_log_dir, log_file)
        with open(log_path, 'r') as f:
            for line in f:
                entry = json.loads(line)
                assert 'timestamp' in entry
                assert 'level' in entry
                assert 'message' in entry
                assert 'component' in entry
                assert 'action' in entry
                assert 'data' in entry
    
    def test_log_draft_created(self, temp_log_dir):
        """Test log_draft_created convenience method."""
        log_file = "test.log"
        logger = JeevesLogger(log_dir=temp_log_dir, log_file=log_file, component="test")
        
        logger.log_draft_created(draft_id=123, email_id=456, tone="formal", confidence=0.85)
        logger.close()
        
        log_path = os.path.join(temp_log_dir, log_file)
        with open(log_path, 'r') as f:
            line = f.readline()
            entry = json.loads(line)
            assert entry['action'] == 'draft_created'
            assert entry['data']['draft_id'] == 123
            assert entry['data']['email_id'] == 456
            assert entry['data']['tone'] == 'formal'
            assert entry['data']['confidence'] == 0.85
    
    def test_log_draft_sent(self, temp_log_dir):
        """Test log_draft_sent convenience method."""
        log_file = "test.log"
        logger = JeevesLogger(log_dir=temp_log_dir, log_file=log_file, component="test")
        
        logger.log_draft_sent(draft_id=123, subject="Test Subject", recipient="test@example.com")
        logger.close()
        
        log_path = os.path.join(temp_log_dir, log_file)
        with open(log_path, 'r') as f:
            line = f.readline()
            entry = json.loads(line)
            assert entry['action'] == 'draft_sent'
            assert entry['data']['draft_id'] == 123
            assert entry['data']['subject'] == "Test Subject"
            assert entry['data']['recipient'] == "test@example.com"
    
    def test_timestamp_format(self, temp_log_dir):
        """Test timestamp is ISO 8601 format."""
        log_file = "test.log"
        logger = JeevesLogger(log_dir=temp_log_dir, log_file=log_file, component="test")
        
        logger.info("Test", action="test")
        logger.close()
        
        log_path = os.path.join(temp_log_dir, log_file)
        with open(log_path, 'r') as f:
            line = f.readline()
            entry = json.loads(line)
            # Should end with Z and be ISO 8601 format
            assert entry['timestamp'].endswith('Z')
            # Should be parseable
            dt = datetime.fromisoformat(entry['timestamp'].rstrip('Z'))
            assert dt is not None
    
    def test_warning_logging(self, temp_log_dir):
        """Test warning level logging."""
        log_file = "test.log"
        logger = JeevesLogger(log_dir=temp_log_dir, log_file=log_file, component="test")
        
        logger.warning("Warning message", action="warn_test")
        logger.close()
        
        log_path = os.path.join(temp_log_dir, log_file)
        with open(log_path, 'r') as f:
            line = f.readline()
            entry = json.loads(line)
            assert entry['level'] == 'warning'
            assert entry['message'] == 'Warning message'
    
    def test_debug_logging(self, temp_log_dir):
        """Test debug level logging."""
        log_file = "test.log"
        logger = JeevesLogger(log_dir=temp_log_dir, log_file=log_file, component="test", level=LogLevel.DEBUG)
        
        logger.debug("Debug message", action="debug_test")
        logger.close()
        
        log_path = os.path.join(temp_log_dir, log_file)
        with open(log_path, 'r') as f:
            line = f.readline()
            entry = json.loads(line)
            assert entry['level'] == 'debug'
            assert entry['message'] == 'Debug message'
    
    def test_log_draft_edited(self, temp_log_dir):
        """Test log_draft_edited convenience method."""
        log_file = "test.log"
        logger = JeevesLogger(log_dir=temp_log_dir, log_file=log_file, component="test")
        
        logger.log_draft_edited(draft_id=123, edits_count=5)
        logger.close()
        
        log_path = os.path.join(temp_log_dir, log_file)
        with open(log_path, 'r') as f:
            line = f.readline()
            entry = json.loads(line)
            assert entry['action'] == 'draft_edited'
            assert entry['data']['draft_id'] == 123
            assert entry['data']['edits_count'] == 5
    
    def test_log_draft_rejected(self, temp_log_dir):
        """Test log_draft_rejected convenience method."""
        log_file = "test.log"
        logger = JeevesLogger(log_dir=temp_log_dir, log_file=log_file, component="test")
        
        logger.log_draft_rejected(draft_id=123, reason="Too informal")
        logger.close()
        
        log_path = os.path.join(temp_log_dir, log_file)
        with open(log_path, 'r') as f:
            line = f.readline()
            entry = json.loads(line)
            assert entry['action'] == 'draft_rejected'
            assert entry['level'] == 'warning'
            assert entry['data']['draft_id'] == 123
            assert entry['data']['reason'] == 'Too informal'
    
    def test_log_email_processed(self, temp_log_dir):
        """Test log_email_processed convenience method."""
        log_file = "test.log"
        logger = JeevesLogger(log_dir=temp_log_dir, log_file=log_file, component="test")
        
        logger.log_email_processed(email_id="abc123", processing_time_ms=1500.5)
        logger.close()
        
        log_path = os.path.join(temp_log_dir, log_file)
        with open(log_path, 'r') as f:
            line = f.readline()
            entry = json.loads(line)
            assert entry['action'] == 'email_processed'
            assert entry['data']['email_id'] == 'abc123'
            assert entry['data']['processing_time_ms'] == 1500.5
            assert entry['duration_ms'] == 1500.5
    
    def test_log_error_method(self, temp_log_dir):
        """Test log_error convenience method."""
        log_file = "test.log"
        logger = JeevesLogger(log_dir=temp_log_dir, log_file=log_file, component="test")
        
        try:
            raise ValueError("Test error")
        except ValueError as e:
            logger.log_error(component="test_component", error=e, context={"email_id": 123})
        
        logger.close()
        
        log_path = os.path.join(temp_log_dir, log_file)
        with open(log_path, 'r') as f:
            line = f.readline()
            entry = json.loads(line)
            assert entry['action'] == 'error'
            assert entry['level'] == 'error'
            assert 'ValueError' in entry['error']
            assert entry['data']['email_id'] == 123
    
    def test_get_logger_function(self):
        """Test get_logger global function."""
        logger = get_logger(component="test")
        assert logger is not None
        assert logger.component == "test"
    
    def test_configure_logging(self):
        """Test configure_logging global function."""
        logger = configure_logging(level=LogLevel.DEBUG)
        assert logger is not None
        assert logger.level == LogLevel.DEBUG
