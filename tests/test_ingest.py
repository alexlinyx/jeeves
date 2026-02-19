"""Tests for email ingestion."""
import pytest
import sys
sys.path.insert(0, '/home/ubuntu/.openclaw/workspace/jeeves')

from src.ingest import (
    extract_email_address, clean_body, is_sent_email,
    get_timestamp, extract_thread_id, extract_subject,
    extract_body, filter_useful_email
)
from email.message import Message


class TestEmailIngest:
    def test_extract_email_simple(self):
        assert extract_email_address("test@example.com") == "test@example.com"
    
    def test_extract_email_with_name(self):
        result = extract_email_address("John Doe <john@example.com>")
        assert result == "john@example.com"
    
    def test_clean_body_removes_quoted(self):
        body = "Hello\n> quoted\nGoodbye"
        cleaned = clean_body(body)
        assert ">" not in cleaned
    
    def test_clean_body_removes_signature(self):
        body = "Hello\n\n--\nRegards\nJohn"
        cleaned = clean_body(body)
        assert "--" not in cleaned
    
    def test_filter_auto_reply(self):
        assert filter_useful_email("auto-reply", "Auto Reply") == False
    
    def test_filter_too_short(self):
        assert filter_useful_email("Hi", "Hello") == False
    
    def test_filter_good_email(self):
        body = "This is a meaningful email with enough content to be useful."
        assert filter_useful_email(body, "Meeting") == True
    
    def test_is_sent_label(self):
        msg = Message()
        msg['X-Gmail-Labels'] = 'Sent,Important'
        assert is_sent_email(msg, None) == True
    
    def test_is_sent_user_email(self):
        msg = Message()
        msg['From'] = 'John <john@example.com>'
        assert is_sent_email(msg, 'john@example.com') == True
    
    def test_file_exists(self):
        import os
        assert os.path.exists('/home/ubuntu/.openclaw/workspace/jeeves/src/ingest.py')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])