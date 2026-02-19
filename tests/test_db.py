"""Tests for database layer (Feature 3.2)."""
import os
import sqlite3
import tempfile
import pytest
from src.db import (
    Database,
    SCHEMA,
    DraftStatus,
    get_db,
)


class TestDatabaseFile:
    """Test file and import tests."""
    
    def test_file_exists(self):
        """Test that db.py exists."""
        assert os.path.exists("src/db.py")
    
    def test_import(self):
        """Test that Database can be imported."""
        from src.db import Database
        assert Database is not None


class TestDatabaseClass:
    """Test Database class methods."""
    
    def test_class_has_required_methods(self):
        """Test Database class has required CRUD methods."""
        db = Database(":memory:")
        
        # Email methods
        assert hasattr(db, 'create_email')
        assert hasattr(db, 'get_email')
        assert hasattr(db, 'list_emails')
        assert hasattr(db, 'update_email')
        assert hasattr(db, 'delete_email')
        
        # Draft methods
        assert hasattr(db, 'create_draft')
        assert hasattr(db, 'get_draft')
        assert hasattr(db, 'list_drafts')
        assert hasattr(db, 'update_draft')
        assert hasattr(db, 'delete_draft')
        
        # Utility methods
        assert hasattr(db, 'get_stats')
        assert hasattr(db, 'get_pending_drafts')
    
    def test_schema_defined(self):
        """Test SCHEMA constant is defined."""
        assert SCHEMA is not None
        assert "CREATE TABLE" in SCHEMA
        assert "emails" in SCHEMA
        assert "drafts" in SCHEMA


class TestDefaultDbPath:
    """Test default database path."""
    
    def test_default_db_path(self):
        """Test default db path is data/jeeves.db."""
        db = Database()
        assert db.db_path == "data/jeeves.db"
    
    def test_custom_db_path(self):
        """Test custom db path works."""
        db = Database("/tmp/test_jeeves.db")
        assert db.db_path == "/tmp/test_jeeves.db"
        # Cleanup
        if os.path.exists("/tmp/test_jeeves.db"):
            os.remove("/tmp/test_jeeves.db")


class TestDraftStatusValues:
    """Test draft status constants."""
    
    def test_draft_status_values(self):
        """Test all draft status values are defined."""
        assert DraftStatus.PENDING == "pending"
        assert DraftStatus.APPROVED == "approved"
        assert DraftStatus.SENT == "sent"
        assert DraftStatus.REJECTED == "rejected"
    
    def test_draft_status_all(self):
        """Test DraftStatus.ALL contains all statuses."""
        assert len(DraftStatus.ALL) == 4
        assert "pending" in DraftStatus.ALL
        assert "approved" in DraftStatus.ALL
        assert "sent" in DraftStatus.ALL
        assert "rejected" in DraftStatus.ALL


class TestEmailCRUD:
    """Test email CRUD operations."""
    
    @pytest.fixture
    def db(self):
        """Create in-memory database for testing."""
        return Database(":memory:")
    
    def test_create_email(self, db):
        """Test creating an email."""
        email_id = db.create_email(
            sender="test@example.com",
            subject="Test Subject",
            body_text="Test body"
        )
        assert email_id is not None
        assert email_id > 0
    
    def test_get_email(self, db):
        """Test getting an email by ID."""
        email_id = db.create_email(
            sender="test@example.com",
            subject="Test Subject",
            body_text="Test body"
        )
        email = db.get_email(email_id)
        assert email is not None
        assert email['sender'] == "test@example.com"
        assert email['subject'] == "Test Subject"
    
    def test_get_email_not_found(self, db):
        """Test getting non-existent email returns None."""
        email = db.get_email(9999)
        assert email is None
    
    def test_list_emails(self, db):
        """Test listing emails."""
        db.create_email(sender="a@test.com", subject="A")
        db.create_email(sender="b@test.com", subject="B")
        
        emails = db.list_emails()
        assert len(emails) == 2
    
    def test_update_email(self, db):
        """Test updating an email."""
        email_id = db.create_email(sender="test@example.com")
        
        result = db.update_email(email_id, subject="Updated Subject")
        assert result is True
        
        email = db.get_email(email_id)
        assert email['subject'] == "Updated Subject"
    
    def test_delete_email(self, db):
        """Test deleting an email."""
        email_id = db.create_email(sender="test@example.com")
        
        result = db.delete_email(email_id)
        assert result is True
        
        email = db.get_email(email_id)
        assert email is None


class TestDraftCRUD:
    """Test draft CRUD operations."""
    
    @pytest.fixture
    def db(self):
        """Create in-memory database for testing."""
        return Database(":memory:")
    
    @pytest.fixture
    def email_id(self, db):
        """Create a test email."""
        return db.create_email(
            sender="test@example.com",
            subject="Test Subject"
        )
    
    def test_create_draft(self, db, email_id):
        """Test creating a draft."""
        draft_id = db.create_draft(
            email_id=email_id,
            generated_text="This is a draft response.",
            tone="formal"
        )
        assert draft_id is not None
        assert draft_id > 0
    
    def test_get_draft(self, db, email_id):
        """Test getting a draft by ID."""
        draft_id = db.create_draft(
            email_id=email_id,
            generated_text="Draft text",
            tone="casual"
        )
        draft = db.get_draft(draft_id)
        assert draft is not None
        assert draft['generated_text'] == "Draft text"
        assert draft['tone'] == "casual"
        assert draft['status'] == "pending"
    
    def test_get_draft_not_found(self, db):
        """Test getting non-existent draft returns None."""
        draft = db.get_draft(9999)
        assert draft is None
    
    def test_list_drafts(self, db, email_id):
        """Test listing drafts."""
        db.create_draft(email_id=email_id, generated_text="Draft 1")
        db.create_draft(email_id=email_id, generated_text="Draft 2")
        
        drafts = db.list_drafts()
        assert len(drafts) == 2
    
    def test_update_draft(self, db, email_id):
        """Test updating a draft."""
        draft_id = db.create_draft(
            email_id=email_id,
            generated_text="Original text"
        )
        
        result = db.update_draft(
            draft_id,
            generated_text="Updated text",
            confidence=0.95
        )
        assert result is True
        
        draft = db.get_draft(draft_id)
        assert draft['generated_text'] == "Updated text"
        assert draft['confidence'] == 0.95
    
    def test_update_draft_status(self, db, email_id):
        """Test updating draft status."""
        draft_id = db.create_draft(
            email_id=email_id,
            generated_text="Draft text"
        )
        
        result = db.update_draft_status(draft_id, DraftStatus.APPROVED)
        assert result is True
        
        draft = db.get_draft(draft_id)
        assert draft['status'] == "approved"
    
    def test_update_draft_status_invalid(self, db, email_id):
        """Test updating to invalid status raises error."""
        draft_id = db.create_draft(
            email_id=email_id,
            generated_text="Draft text"
        )
        
        with pytest.raises(ValueError):
            db.update_draft_status(draft_id, "invalid_status")
    
    def test_delete_draft(self, db, email_id):
        """Test deleting a draft."""
        draft_id = db.create_draft(
            email_id=email_id,
            generated_text="Draft text"
        )
        
        result = db.delete_draft(draft_id)
        assert result is True
        
        draft = db.get_draft(draft_id)
        assert draft is None
    
    def test_get_drafts_by_status(self, db, email_id):
        """Test getting drafts by status."""
        db.create_draft(
            email_id=email_id,
            generated_text="Draft 1",
            status=DraftStatus.PENDING
        )
        db.create_draft(
            email_id=email_id,
            generated_text="Draft 2",
            status=DraftStatus.APPROVED
        )
        
        pending = db.get_drafts_by_status(DraftStatus.PENDING)
        assert len(pending) == 1
        assert pending[0]['status'] == "pending"
    
    def test_get_pending_drafts(self, db):
        """Test getting pending drafts with email info."""
        email_id = db.create_email(
            sender="test@example.com",
            subject="Test"
        )
        db.create_draft(
            email_id=email_id,
            generated_text="Pending draft",
            status=DraftStatus.PENDING
        )
        
        pending = db.get_pending_drafts()
        assert len(pending) == 1
        assert pending[0]['sender'] == "test@example.com"


class TestDatabaseStats:
    """Test database statistics."""
    
    @pytest.fixture
    def db(self):
        """Create in-memory database for testing."""
        return Database(":memory:")
    
    def test_get_stats_empty(self, db):
        """Test stats on empty database."""
        stats = db.get_stats()
        assert stats['emails'] == 0
        assert stats['drafts'] == 0
        assert stats['pending'] == 0
    
    def test_get_stats_with_data(self, db):
        """Test stats with data."""
        email_id = db.create_email(sender="test@example.com")
        db.create_draft(
            email_id=email_id,
            generated_text="Draft 1",
            status=DraftStatus.PENDING
        )
        db.create_draft(
            email_id=email_id,
            generated_text="Draft 2",
            status=DraftStatus.APPROVED
        )
        
        stats = db.get_stats()
        assert stats['emails'] == 1
        assert stats['drafts'] == 2
        assert stats['pending'] == 1
        assert stats['approved'] == 1


class TestConvenienceFunction:
    """Test convenience function."""
    
    def test_get_db_function(self):
        """Test get_db convenience function."""
        db = get_db(":memory:")
        assert isinstance(db, Database)
    
    def test_get_db_with_custom_path(self):
        """Test get_db with custom path."""
        db = get_db("/tmp/test_custom.db")
        assert db.db_path == "/tmp/test_custom.db"
        if os.path.exists("/tmp/test_custom.db"):
            os.remove("/tmp/test_custom.db")
