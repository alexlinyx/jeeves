"""Database layer for Jeeves Email Assistant using SQLite."""
import sqlite3
from typing import Optional, List, Dict, Any
from datetime import datetime
from contextlib import contextmanager


# Database schema constants
SCHEMA = """
CREATE TABLE IF NOT EXISTS emails (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id TEXT,
    sender TEXT NOT NULL,
    subject TEXT,
    body_text TEXT,
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS drafts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email_id INTEGER NOT NULL,
    generated_text TEXT NOT NULL,
    tone TEXT DEFAULT 'match_style',
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'approved', 'sent', 'rejected')),
    confidence REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (email_id) REFERENCES emails(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_emails_thread_id ON emails(thread_id);
CREATE INDEX IF NOT EXISTS idx_emails_sender ON emails(sender);
CREATE INDEX IF NOT EXISTS idx_drafts_email_id ON drafts(email_id);
CREATE INDEX IF NOT EXISTS idx_drafts_status ON drafts(status);
"""

# Draft status constants
class DraftStatus:
    PENDING = "pending"
    APPROVED = "approved"
    SENT = "sent"
    REJECTED = "rejected"
    
    ALL = [PENDING, APPROVED, SENT, REJECTED]


class Database:
    """SQLite database manager for Jeeves Email Assistant."""
    
    def __init__(self, db_path: str = "data/jeeves.db"):
        """Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file.
        """
        self.db_path = db_path
        self._connection = None
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema."""
        with self.get_connection() as conn:
            conn.executescript(SCHEMA)
            conn.commit()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        if self.db_path == ":memory:" and self._connection:
            # Reuse in-memory connection
            yield self._connection
        else:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            if self.db_path == ":memory:":
                self._connection = conn
            try:
                yield conn
            finally:
                if self.db_path != ":memory:":
                    conn.close()
    
    # ==================== Email Operations ====================
    
    def create_email(
        self,
        sender: str,
        subject: str = None,
        body_text: str = None,
        thread_id: str = None,
        received_at: str = None
    ) -> int:
        """Create a new email record.
        
        Args:
            sender: Email sender address.
            subject: Email subject.
            body_text: Email body text.
            thread_id: Gmail thread ID.
            received_at: ISO format timestamp string.
            
        Returns:
            New email ID.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO emails (sender, subject, body_text, thread_id, received_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (sender, subject, body_text, thread_id, received_at)
            )
            conn.commit()
            return cursor.lastrowid
    
    def get_email(self, email_id: int) -> Optional[Dict[str, Any]]:
        """Get an email by ID.
        
        Args:
            email_id: Email record ID.
            
        Returns:
            Email record as dictionary or None.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM emails WHERE id = ?", (email_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_email_by_thread_id(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Get an email by thread ID.
        
        Args:
            thread_id: Gmail thread ID.
            
        Returns:
            Email record as dictionary or None.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM emails WHERE thread_id = ?", (thread_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def list_emails(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """List all emails.
        
        Args:
            limit: Maximum number of emails to return.
            offset: Number of emails to skip.
            
        Returns:
            List of email records.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM emails ORDER BY received_at DESC LIMIT ? OFFSET ?",
                (limit, offset)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def update_email(self, email_id: int, **kwargs) -> bool:
        """Update an email record.
        
        Args:
            email_id: Email record ID.
            **kwargs: Fields to update.
            
        Returns:
            True if updated, False if not found.
        """
        if not kwargs:
            return False
        
        fields = ", ".join(f"{k} = ?" for k in kwargs.keys())
        values = list(kwargs.values()) + [email_id]
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE emails SET {fields} WHERE id = ?",
                values
                )
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_email(self, email_id: int) -> bool:
        """Delete an email and its drafts.
        
        Args:
            email_id: Email record ID.
            
        Returns:
            True if deleted, False if not found.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM emails WHERE id = ?", (email_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    # ==================== Draft Operations ====================
    
    def create_draft(
        self,
        email_id: int,
        generated_text: str,
        tone: str = "match_style",
        status: str = "pending",
        confidence: float = None
    ) -> int:
        """Create a new draft.
        
        Args:
            email_id: Associated email ID.
            generated_text: Draft email text.
            tone: Tone mode used (casual, formal, concise, match_style).
            status: Draft status (pending, approved, sent, rejected).
            confidence: Confidence score (0.0-1.0).
            
        Returns:
            New draft ID.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO drafts (email_id, generated_text, tone, status, confidence)
                   VALUES (?, ?, ?, ?, ?)""",
                (email_id, generated_text, tone, status, confidence)
            )
            conn.commit()
            return cursor.lastrowid
    
    def get_draft(self, draft_id: int) -> Optional[Dict[str, Any]]:
        """Get a draft by ID.
        
        Args:
            draft_id: Draft record ID.
            
        Returns:
            Draft record as dictionary or None.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM drafts WHERE id = ?", (draft_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_drafts_by_email(self, email_id: int) -> List[Dict[str, Any]]:
        """Get all drafts for an email.
        
        Args:
            email_id: Email record ID.
            
        Returns:
            List of draft records.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM drafts WHERE email_id = ? ORDER BY created_at DESC",
                (email_id,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def get_drafts_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get all drafts with a specific status.
        
        Args:
            status: Draft status (pending, approved, sent, rejected).
            
        Returns:
            List of draft records.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM drafts WHERE status = ? ORDER BY created_at DESC",
                (status,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def list_drafts(
        self,
        limit: int = 100,
        offset: int = 0,
        status: str = None
    ) -> List[Dict[str, Any]]:
        """List all drafts.
        
        Args:
            limit: Maximum number of drafts to return.
            offset: Number of drafts to skip.
            status: Filter by status.
            
        Returns:
            List of draft records.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if status:
                cursor.execute(
                    """SELECT * FROM drafts WHERE status = ? 
                       ORDER BY created_at DESC LIMIT ? OFFSET ?""",
                    (status, limit, offset)
                )
            else:
                cursor.execute(
                    "SELECT * FROM drafts ORDER BY created_at DESC LIMIT ? OFFSET ?",
                    (limit, offset)
                )
            return [dict(row) for row in cursor.fetchall()]
    
    def update_draft(
        self,
        draft_id: int,
        **kwargs
    ) -> bool:
        """Update a draft record.
        
        Args:
            draft_id: Draft record ID.
            **kwargs: Fields to update (generated_text, tone, status, confidence).
            
        Returns:
            True if updated, False if not found.
        """
        if not kwargs:
            return False
        
        # Add updated_at timestamp
        kwargs['updated_at'] = datetime.now().isoformat()
        
        fields = ", ".join(f"{k} = ?" for k in kwargs.keys())
        values = list(kwargs.values()) + [draft_id]
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE drafts SET {fields} WHERE id = ?",
                values
            )
            conn.commit()
            return cursor.rowcount > 0
    
    def update_draft_status(
        self,
        draft_id: int,
        status: str
    ) -> bool:
        """Update draft status.
        
        Args:
            draft_id: Draft record ID.
            status: New status (pending, approved, sent, rejected).
            
        Returns:
            True if updated, False if not found.
        """
        if status not in DraftStatus.ALL:
            raise ValueError(f"Invalid status: {status}. Must be one of {DraftStatus.ALL}")
        return self.update_draft(draft_id, status=status)
    
    def delete_draft(self, draft_id: int) -> bool:
        """Delete a draft.
        
        Args:
            draft_id: Draft record ID.
            
        Returns:
            True if deleted, False if not found.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM drafts WHERE id = ?", (draft_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_pending_drafts(self) -> List[Dict[str, Any]]:
        """Get all pending drafts.
        
        Returns:
            List of pending draft records with email info.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT d.*, e.sender, e.subject, e.body_text
                   FROM drafts d
                   JOIN emails e ON d.email_id = e.id
                   WHERE d.status = 'pending'
                   ORDER BY d.created_at DESC"""
            )
            return [dict(row) for row in cursor.fetchall()]
    
    # ==================== Utility Methods ====================
    
    def get_stats(self) -> Dict[str, int]:
        """Get database statistics.
        
        Returns:
            Dictionary with counts of emails, drafts by status.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total emails
            cursor.execute("SELECT COUNT(*) FROM emails")
            email_count = cursor.fetchone()[0]
            
            # Total drafts
            cursor.execute("SELECT COUNT(*) FROM drafts")
            draft_count = cursor.fetchone()[0]
            
            # Drafts by status
            cursor.execute(
                "SELECT status, COUNT(*) FROM drafts GROUP BY status"
            )
            status_counts = {row[0]: row[1] for row in cursor.fetchall()}
            
            return {
                "emails": email_count,
                "drafts": draft_count,
                "pending": status_counts.get("pending", 0),
                "approved": status_counts.get("approved", 0),
                "sent": status_counts.get("sent", 0),
                "rejected": status_counts.get("rejected", 0),
            }


# Convenience function for quick database access
def get_db(db_path: str = "data/jeeves.db") -> Database:
    """Get a Database instance.
    
    Args:
        db_path: Path to SQLite database file.
        
    Returns:
        Database instance.
    """
    return Database(db_path)
