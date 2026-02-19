"""Tests for Gmail client."""
import pytest
import os
from unittest.mock import Mock, patch, MagicMock


class TestGmailClient:
    """Test cases for GmailClient."""
    
    def test_gmail_client_file_exists(self):
        """Test gmail_client.py file exists."""
        assert os.path.exists('src/gmail_client.py'), "gmail_client.py not found"
    
    def test_client_import(self):
        """Test client can be imported."""
        from src.gmail_client import GmailClient
        assert GmailClient is not None
    
    def test_scopes_defined(self):
        """Test OAuth scopes are properly defined."""
        from src.gmail_client import GmailClient
        assert hasattr(GmailClient, 'SCOPES')
        scopes_str = ' '.join(GmailClient.SCOPES)
        assert 'gmail.readonly' in scopes_str
        assert 'gmail.compose' in scopes_str
        assert 'gmail.send' in scopes_str
    
    def test_list_emails_method_exists(self):
        """Test list_emails method exists."""
        from src.gmail_client import GmailClient
        assert hasattr(GmailClient, 'list_emails'), "list_emails method missing"
    
    def test_get_email_method_exists(self):
        """Test get_email method exists."""
        from src.gmail_client import GmailClient
        assert hasattr(GmailClient, 'get_email'), "get_email method missing"
    
    def test_create_draft_method_exists(self):
        """Test create_draft method exists."""
        from src.gmail_client import GmailClient
        assert hasattr(GmailClient, 'create_draft'), "create_draft method missing"
    
    def test_send_draft_method_exists(self):
        """Test send_draft method exists."""
        from src.gmail_client import GmailClient
        assert hasattr(GmailClient, 'send_draft'), "send_draft method missing"
    
    def test_list_drafts_method_exists(self):
        """Test list_drafts method exists."""
        from src.gmail_client import GmailClient
        assert hasattr(GmailClient, 'list_drafts'), "list_drafts method missing"
    
    def test_requirements_have_dependencies(self):
        """Test requirements.txt has required dependencies."""
        with open('requirements.txt', 'r') as f:
            content = f.read()
        
        assert 'google-auth-oauthlib' in content, "google-auth-oauthlib missing"
        assert 'google-auth-httplib2' in content, "google-auth-httplib2 missing"
        assert 'google-api-python-client' in content, "google-api-python-client missing"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])