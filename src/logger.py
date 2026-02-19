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
        self.log_dir = log_dir or self.DEFAULT_LOG_DIR
        self.log_file = log_file or self.DEFAULT_LOG_FILE
        self.component = component
        self.level = level
        
        # Create log directory if it doesn't exist
        Path(self.log_dir).mkdir(parents=True, exist_ok=True)
        
        self._log_path = os.path.join(self.log_dir, self.log_file)
        
        # Open file in append mode
        self._file = open(self._log_path, 'a', encoding='utf-8')
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO 8601 format."""
        return datetime.utcnow().isoformat(timespec='milliseconds') + 'Z'
    
    def _should_log(self, level: LogLevel) -> bool:
        """Check if the given level should be logged."""
        level_order = [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARNING, LogLevel.ERROR, LogLevel.CRITICAL]
        return level_order.index(level) >= level_order.index(self.level)
    
    def _create_entry(
        self,
        level: LogLevel,
        message: str,
        action: str,
        data: Dict = None,
        duration_ms: float = None,
        error: str = None,
        trace_id: str = None,
        **kwargs
    ) -> LogEntry:
        """Create a log entry."""
        return LogEntry(
            timestamp=self._get_timestamp(),
            level=level.value,
            message=message,
            component=self.component,
            action=action,
            data=data or {},
            duration_ms=duration_ms,
            error=error,
            trace_id=trace_id,
            **kwargs
        )
    
    def info(self, message: str, action: str, data: Dict = None, **kwargs):
        """Log info level."""
        if self._should_log(LogLevel.INFO):
            entry = self._create_entry(LogLevel.INFO, message, action, data, **kwargs)
            self._write(entry)
    
    def warning(self, message: str, action: str, data: Dict = None, **kwargs):
        """Log warning level."""
        if self._should_log(LogLevel.WARNING):
            entry = self._create_entry(LogLevel.WARNING, message, action, data, **kwargs)
            self._write(entry)
    
    def error(self, message: str, action: str, error: Exception = None, data: Dict = None, **kwargs):
        """Log error level."""
        if self._should_log(LogLevel.ERROR):
            if error:
                error_str = f"{type(error).__name__}: {str(error)}"
            else:
                error_str = kwargs.get('error')
            entry = self._create_entry(LogLevel.ERROR, message, action, data, error=error_str, **kwargs)
            self._write(entry)
    
    def debug(self, message: str, action: str, data: Dict = None, **kwargs):
        """Log debug level."""
        if self._should_log(LogLevel.DEBUG):
            entry = self._create_entry(LogLevel.DEBUG, message, action, data, **kwargs)
            self._write(entry)
    
    def log_draft_created(self, draft_id: int, email_id: int, tone: str, confidence: float):
        """Log draft creation."""
        self.info(
            message="Draft created",
            action="draft_created",
            data={
                "draft_id": draft_id,
                "email_id": email_id,
                "tone": tone,
                "confidence": confidence
            }
        )
    
    def log_draft_sent(self, draft_id: int, subject: str, recipient: str):
        """Log draft sent."""
        self.info(
            message="Draft sent",
            action="draft_sent",
            data={
                "draft_id": draft_id,
                "subject": subject,
                "recipient": recipient
            }
        )
    
    def log_draft_edited(self, draft_id: int, edits_count: int):
        """Log draft edited."""
        self.info(
            message="Draft edited",
            action="draft_edited",
            data={
                "draft_id": draft_id,
                "edits_count": edits_count
            }
        )
    
    def log_draft_rejected(self, draft_id: int, reason: str = None):
        """Log draft rejected."""
        self.warning(
            message="Draft rejected",
            action="draft_rejected",
            data={
                "draft_id": draft_id,
                "reason": reason or "unspecified"
            }
        )
    
    def log_email_processed(self, email_id: str, processing_time_ms: float):
        """Log email processing."""
        self.info(
            message="Email processed",
            action="email_processed",
            data={
                "email_id": email_id,
                "processing_time_ms": processing_time_ms
            },
            duration_ms=processing_time_ms
        )
    
    def log_error(self, component: str, error: Exception, context: Dict = None):
        """Log error with context."""
        error_str = f"{type(error).__name__}: {str(error)}"
        self.error(
            message=f"Error in {component}",
            action="error",
            error=error_str,
            data=context or {}
        )
    
    def _write(self, entry: LogEntry):
        """Write log entry to file."""
        try:
            json_line = json.dumps(asdict(entry), ensure_ascii=False)
            self._file.write(json_line + '\n')
            self._file.flush()
        except Exception as e:
            # Fallback to stderr if file write fails
            import sys
            print(f"Failed to write log: {e}", file=sys.stderr)
    
    def close(self):
        """Close the log file."""
        if hasattr(self, '_file') and self._file:
            self._file.close()
    
    def __del__(self):
        """Cleanup on deletion."""
        self.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Global logger instance
_logger: Optional[JeevesLogger] = None


def get_logger(component: str = None) -> JeevesLogger:
    """Get or create logger instance."""
    global _logger
    if _logger is None:
        _logger = JeevesLogger(component=component or "jeeves")
    elif component:
        # Create a new logger with the specified component
        return JeevesLogger(component=component)
    return _logger


def configure_logging(log_dir: str = None, level: LogLevel = LogLevel.INFO):
    """Configure global logging."""
    global _logger
    _logger = JeevesLogger(log_dir=log_dir, level=level)
    return _logger
