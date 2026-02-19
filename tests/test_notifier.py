"""Tests for the Notifier notification system."""
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from notifier import Notifier, notify_draft_ready, notify_draft_sent, notify_error, send


class TestNotifierImport(unittest.TestCase):
    """Test file can be imported."""
    
    def test_file_exists(self):
        """Test that notifier.py exists."""
        self.assertTrue(os.path.exists(os.path.join(os.path.dirname(__file__), '..', 'src', 'notifier.py')))
    
    def test_import(self):
        """Test that Notifier can be imported."""
        from src.notifier import Notifier
        self.assertIsNotNone(Notifier)


class TestNotifierClass(unittest.TestCase):
    """Test Notifier class structure."""
    
    def test_class_exists(self):
        """Test Notifier class exists."""
        self.assertTrue(hasattr(__import__('src.notifier', fromlist=['Notifier']), 'Notifier'))
    
    def test_class_has_required_methods(self):
        """Test class has all required methods."""
        notifier = Notifier()
        self.assertTrue(hasattr(notifier, 'send'))
        self.assertTrue(hasattr(notifier, 'notify_draft_ready'))
        self.assertTrue(hasattr(notifier, 'notify_draft_sent'))
        self.assertTrue(hasattr(notifier, 'notify_error'))
        self.assertTrue(callable(notifier.send))
        self.assertTrue(callable(notifier.notify_draft_ready))
        self.assertTrue(callable(notifier.notify_draft_sent))
        self.assertTrue(callable(notifier.notify_error))


class TestNotifierDefaults(unittest.TestCase):
    """Test default values."""
    
    def test_default_topic(self):
        """Test default topic is 'jeeves-drafts'."""
        notifier = Notifier()
        self.assertEqual(notifier.DEFAULT_TOPIC, "jeeves-drafts")
        self.assertEqual(notifier.topic, "jeeves-drafts")
    
    def test_default_url(self):
        """Test default URL is 'https://ntfy.sh'."""
        notifier = Notifier()
        self.assertEqual(notifier.DEFAULT_URL, "https://ntfy.sh")
        self.assertEqual(notifier.base_url, "https://ntfy.sh")
    
    def test_custom_topic(self):
        """Test custom topic can be set."""
        notifier = Notifier(topic="custom-topic")
        self.assertEqual(notifier.topic, "custom-topic")
    
    def test_custom_url(self):
        """Test custom URL can be set."""
        notifier = Notifier(base_url="https://custom.ntfy.sh")
        self.assertEqual(notifier.base_url, "https://custom.ntfy.sh")


class TestNotifierSend(unittest.TestCase):
    """Test send method."""
    
    @patch('src.notifier.requests.post')
    def test_send_basic(self, mock_post):
        """Test basic send functionality."""
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        notifier = Notifier()
        response = notifier.send("Test Title", "Test Message")
        
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertIn("Test Title", str(call_args))
        self.assertIn("Test Message", str(call_args))
    
    @patch('src.notifier.requests.post')
    def test_send_with_priority(self, mock_post):
        """Test send with custom priority."""
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        notifier = Notifier()
        notifier.send("Test", "Message", priority="high")
        
        call_args = mock_post.call_args
        self.assertIn("priority", str(call_args))


class TestNotifierDraftReady(unittest.TestCase):
    """Test notify_draft_ready method."""
    
    @patch('src.notifier.requests.post')
    def test_notify_draft_ready(self, mock_post):
        """Test draft ready notification."""
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        notifier = Notifier()
        response = notifier.notify_draft_ready(
            subject="Test Subject",
            sender="sender@example.com",
            preview="Preview text",
            draft_id="12345"
        )
        
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        # Verify the URL contains the topic
        self.assertIn("jeeves-drafts", str(call_args))
    
    @patch('src.notifier.requests.post')
    def test_notify_draft_ready_returns_response(self, mock_post):
        """Test draft ready returns response object."""
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        notifier = Notifier()
        response = notifier.notify_draft_ready(
            subject="Test",
            sender="test@example.com",
            preview="Preview",
            draft_id="123"
        )
        
        self.assertEqual(response, mock_response)


class TestNotifierDraftSent(unittest.TestCase):
    """Test notify_draft_sent method."""
    
    @patch('src.notifier.requests.post')
    def test_notify_draft_sent(self, mock_post):
        """Test draft sent notification."""
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        notifier = Notifier()
        response = notifier.notify_draft_sent(
            subject="Test Subject",
            recipient="recipient@example.com"
        )
        
        mock_post.assert_called_once()
    
    @patch('src.notifier.requests.post')
    def test_notify_draft_sent_returns_response(self, mock_post):
        """Test draft sent returns response object."""
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        notifier = Notifier()
        response = notifier.notify_draft_sent(
            subject="Test",
            recipient="test@example.com"
        )
        
        self.assertEqual(response, mock_response)


class TestNotifierError(unittest.TestCase):
    """Test notify_error method."""
    
    @patch('src.notifier.requests.post')
    def test_notify_error(self, mock_post):
        """Test error notification."""
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        notifier = Notifier()
        response = notifier.notify_error("Something went wrong")
        
        mock_post.assert_called_once()
    
    @patch('src.notifier.requests.post')
    def test_notify_error_returns_response(self, mock_post):
        """Test error returns response object."""
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        notifier = Notifier()
        response = notifier.notify_error("Error message")
        
        self.assertEqual(response, mock_response)


class TestNotifierNotificationStructure(unittest.TestCase):
    """Test notification structure."""
    
    def test_priorities_dict_exists(self):
        """Test priorities dictionary exists."""
        notifier = Notifier()
        self.assertTrue(hasattr(notifier, 'PRIORITIES'))
        self.assertIn("low", notifier.PRIORITIES)
        self.assertIn("default", notifier.PRIORITIES)
        self.assertIn("high", notifier.PRIORITIES)
        self.assertIn("urgent", notifier.PRIORITIES)
    
    @patch('src.notifier.requests.post')
    def test_notification_contains_subject(self, mock_post):
        """Test notification contains subject field."""
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        notifier = Notifier()
        notifier.notify_draft_ready(
            subject="My Subject",
            sender="test@example.com",
            preview="Preview",
            draft_id="123"
        )
        
        call_args = mock_post.call_args
        # Check that subject appears in the call
        self.assertIn("My Subject", str(call_args))


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions."""
    
    @patch('src.notifier.requests.post')
    def test_notify_draft_ready_function(self, mock_post):
        """Test notify_draft_ready convenience function."""
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        response = notify_draft_ready(
            subject="Test",
            sender="test@example.com",
            preview="Preview",
            draft_id="123"
        )
        
        self.assertEqual(response, mock_response)
    
    @patch('src.notifier.requests.post')
    def test_notify_draft_sent_function(self, mock_post):
        """Test notify_draft_sent convenience function."""
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        response = notify_draft_sent(
            subject="Test",
            recipient="test@example.com"
        )
        
        self.assertEqual(response, mock_response)
    
    @patch('src.notifier.requests.post')
    def test_notify_error_function(self, mock_post):
        """Test notify_error convenience function."""
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        response = notify_error("Error occurred")
        
        self.assertEqual(response, mock_response)
    
    @patch('src.notifier.requests.post')
    def test_send_function(self, mock_post):
        """Test send convenience function."""
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response
        
        response = send("Title", "Message")
        
        self.assertEqual(response, mock_response)


if __name__ == '__main__':
    unittest.main()
