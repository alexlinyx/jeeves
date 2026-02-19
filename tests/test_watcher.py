"""Tests for email watcher service."""
import os
import signal
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Import the modules to test
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.watcher import (
    EmailWatcher,
    is_automated_email,
    is_promotional_email,
    extract_sender_domain,
    SKIP_DOMAINS,
    SKIP_PATTERNS,
    run_watcher
)


class TestEmailWatcher:
    """Test cases for EmailWatcher."""
    
    def test_file_exists(self):
        """Test watcher.py exists."""
        import src.watcher
        assert src.watcher is not None
    
    def test_import(self):
        """Test EmailWatcher can be imported."""
        from src.watcher import EmailWatcher
        assert EmailWatcher is not None
    
    def test_class_has_required_methods(self):
        """Test all required methods exist."""
        watcher = EmailWatcher()
        
        # Check all required methods exist
        assert hasattr(watcher, 'start')
        assert hasattr(watcher, 'stop')
        assert hasattr(watcher, 'poll')
        assert hasattr(watcher, 'process_email')
        assert hasattr(watcher, 'should_process')
        assert hasattr(watcher, 'get_status')
        
        # Check they are callable
        assert callable(watcher.start)
        assert callable(watcher.stop)
        assert callable(watcher.poll)
        assert callable(watcher.process_email)
        assert callable(watcher.should_process)
        assert callable(watcher.get_status)
    
    def test_default_poll_interval(self):
        """Test default poll interval is 300 seconds (5 min)."""
        watcher = EmailWatcher()
        assert watcher.poll_interval == 300
    
    def test_default_batch_size(self):
        """Test default batch size is 10."""
        watcher = EmailWatcher()
        assert watcher.batch_size == 10
    
    def test_should_process_filters_spam(self):
        """Test spam emails are filtered out."""
        watcher = EmailWatcher()
        
        # Spam email
        spam_email = {
            'id': '123',
            'subject': 'Buy now!',
            'labelIds': ['SPAM']
        }
        
        assert watcher.should_process(spam_email) is False
    
    def test_should_process_filters_promotional(self):
        """Test promotional emails are filtered out."""
        watcher = EmailWatcher()
        
        # Promotional email
        promo_email = {
            'id': '456',
            'subject': 'Special Offer - 50% Off!',
            'snippet': 'Click here for great deals',
            'labelIds': ['INBOX', 'CATEGORY_PROMOTIONS']
        }
        
        assert watcher.should_process(promo_email) is False
    
    def test_should_process_filters_noreply(self):
        """Test noreply emails are filtered out."""
        watcher = EmailWatcher()
        
        # noreply email
        noreply_email = {
            'id': '789',
            'from': 'noreply@example.com',
            'subject': 'Your order confirmation',
            'labelIds': ['INBOX']
        }
        
        assert watcher.should_process(noreply_email) is False
    
    def test_should_process_accepts_valid_email(self):
        """Test valid emails pass the filter."""
        watcher = EmailWatcher()
        
        # Valid email from a real person
        valid_email = {
            'id': 'abc123',
            'from': 'john.doe@gmail.com',
            'subject': 'Meeting tomorrow',
            'snippet': 'Hey, are we still on for tomorrow?',
            'labelIds': ['INBOX', 'UNREAD']
        }
        
        assert watcher.should_process(valid_email) is True
    
    def test_get_status_returns_running_state(self):
        """Test get_status returns running state."""
        watcher = EmailWatcher()
        
        # Initially not running
        status = watcher.get_status()
        assert 'running' in status
        assert status['running'] is False
        
        # Set running to True
        watcher._running = True
        status = watcher.get_status()
        assert status['running'] is True
    
    def test_graceful_shutdown(self):
        """Test stop() sets running to False."""
        watcher = EmailWatcher()
        watcher._running = True
        
        watcher.stop()
        
        assert watcher._running is False
    
    def test_environment_poll_interval(self):
        """Test POLL_INTERVAL env var is respected."""
        # Set environment variable
        with patch.dict(os.environ, {'POLL_INTERVAL': '60'}):
            watcher = EmailWatcher()
            assert watcher.poll_interval == 60
        
        # Clean up
        if 'POLL_INTERVAL' in os.environ:
            del os.environ['POLL_INTERVAL']
    
    def test_environment_batch_size(self):
        """Test BATCH_SIZE env var is respected."""
        with patch.dict(os.environ, {'BATCH_SIZE': '25'}):
            watcher = EmailWatcher()
            assert watcher.batch_size == 25
        
        if 'BATCH_SIZE' in os.environ:
            del os.environ['BATCH_SIZE']


class TestFilteringFunctions:
    """Test email filtering utilities."""
    
    def test_is_automated_email_detects_noreply(self):
        """Test automated detection for noreply addresses."""
        email = {
            'from': 'noreply@amazon.com',
            'subject': 'Your order'
        }
        
        assert is_automated_email(email) is True
    
    def test_is_automated_email_detects_notifications(self):
        """Test automated detection for notification addresses."""
        email = {
            'from': 'notifications@github.com',
            'subject': 'New issue'
        }
        
        assert is_automated_email(email) is True
    
    def test_is_promotional_email_detects_newsletter(self):
        """Test promotional detection for newsletters."""
        email = {
            'subject': 'Weekly Newsletter',
            'snippet': 'Check out our latest updates'
        }
        
        assert is_promotional_email(email) is True
    
    def test_is_promotional_email_detects_promotion(self):
        """Test promotional detection for promotions."""
        email = {
            'subject': 'Special Promotion',
            'snippet': '50% off everything',
            'labelIds': ['CATEGORY_PROMOTIONS']
        }
        
        assert is_promotional_email(email) is True
    
    def test_extract_sender_domain(self):
        """Test domain extraction from email address."""
        email = {
            'from': 'john.doe@gmail.com'
        }
        
        assert extract_sender_domain(email) == 'gmail.com'
    
    def test_extract_sender_domain_with_name(self):
        """Test domain extraction from email with display name."""
        email = {
            'from': 'John Doe <john.doe@company.org>'
        }
        
        assert extract_sender_domain(email) == 'company.org'
    
    def test_extract_sender_domain_missing(self):
        """Test domain extraction when no email address."""
        email = {
            'subject': 'Test email'
        }
        
        assert extract_sender_domain(email) == ''
    
    def test_skip_domains_constant(self):
        """Test SKIP_DOMAINS constant is defined."""
        assert isinstance(SKIP_DOMAINS, list)
        assert len(SKIP_DOMAINS) > 0
        assert 'noreply' in SKIP_DOMAINS
    
    def test_skip_patterns_constant(self):
        """Test SKIP_PATTERNS constant is defined."""
        assert isinstance(SKIP_PATTERNS, list)
        assert len(SKIP_PATTERNS) > 0
        assert 'unsubscribe' in SKIP_PATTERNS


class TestEmailWatcherIntegration:
    """Integration tests for EmailWatcher."""
    
    def test_poll_with_no_gmail_client(self):
        """Test poll returns empty list when no gmail_client."""
        watcher = EmailWatcher()
        
        result = watcher.poll()
        
        assert result == []
    
    def test_process_email_with_callback(self):
        """Test process_email uses callback when provided."""
        callback = Mock(return_value={'draft_id': '123'})
        watcher = EmailWatcher(on_new_email=callback)
        
        email = {'id': 'test123', 'subject': 'Test'}
        result = watcher.process_email(email)
        
        callback.assert_called_once_with(email)
        assert result == {'draft_id': '123'}
        assert watcher._processed_count == 1
        assert watcher._draft_created_count == 1
    
    def test_process_email_without_handler(self):
        """Test process_email returns None when no handler."""
        watcher = EmailWatcher()
        
        email = {'id': 'test123', 'subject': 'Test'}
        result = watcher.process_email(email)
        
        assert result is None
    
    def test_get_status_contains_stats(self):
        """Test get_status includes statistics."""
        watcher = EmailWatcher()
        watcher._processed_count = 5
        watcher._draft_created_count = 3
        watcher._error_count = 1
        
        status = watcher.get_status()
        
        assert status['processed_count'] == 5
        assert status['draft_created_count'] == 3
        assert status['error_count'] == 1
    
    def test_should_process_filters_trash(self):
        """Test trash emails are filtered out."""
        watcher = EmailWatcher()
        
        trash_email = {
            'id': '123',
            'labelIds': ['TRASH']
        }
        
        assert watcher.should_process(trash_email) is False
    
    def test_should_process_filters_sent(self):
        """Test sent emails are filtered out."""
        watcher = EmailWatcher()
        
        sent_email = {
            'id': '123',
            'labelIds': ['SENT']
        }
        
        assert watcher.should_process(sent_email) is False
