"""Email watcher service for Jeeves."""
import os
import signal
import time
import logging
import re
from typing import Optional, Callable, List, Dict, Any
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class EmailWatcher:
    """Background service that polls Gmail for new emails."""
    
    DEFAULT_POLL_INTERVAL = 300  # 5 minutes
    DEFAULT_BATCH_SIZE = 10
    
    def __init__(
        self,
        gmail_client=None,
        response_generator=None,
        db=None,
        notifier=None,
        poll_interval: int = None,
        batch_size: int = None,
        on_new_email: Callable = None
    ):
        """Initialize email watcher.
        
        Args:
            gmail_client: GmailClient instance
            response_generator: ResponseGenerator instance
            db: Database instance
            notifier: Notifier instance (optional)
            poll_interval: Seconds between polls (default: 300)
            batch_size: Max emails to process per poll (default: 10)
            on_new_email: Callback for new email processing
        """
        self.gmail_client = gmail_client
        self.response_generator = response_generator
        self.db = db
        self.notifier = notifier
        self.poll_interval = poll_interval or int(os.environ.get('POLL_INTERVAL', self.DEFAULT_POLL_INTERVAL))
        self.batch_size = batch_size or int(os.environ.get('BATCH_SIZE', self.DEFAULT_BATCH_SIZE))
        self.on_new_email = on_new_email
        self._running = False
        self._last_check = None
        self._processed_count = 0
        self._draft_created_count = 0
        self._error_count = 0
        
        # For signal handling
        self._signal_received = None
    
    def start(self):
        """Start the watcher loop."""
        self._running = True
        self._setup_signal_handlers()
        logger.info(f"Starting email watcher with poll interval: {self.poll_interval}s")
        
        while self._running:
            try:
                self.poll()
            except Exception as e:
                logger.error(f"Error during poll: {e}")
                self._error_count += 1
            
            # Sleep in small increments to allow quick shutdown
            for _ in range(self.poll_interval):
                if not self._running:
                    break
                time.sleep(1)
        
        logger.info("Email watcher stopped")
    
    def stop(self):
        """Stop the watcher loop."""
        self._running = False
        self._signal_received = None
        logger.info("Stopping email watcher...")
    
    def poll(self) -> list:
        """Poll for new emails.
        
        Returns:
            List of new email dicts
        """
        self._last_check = datetime.now(timezone.utc)
        
        if not self.gmail_client:
            logger.warning("No gmail_client configured, skipping poll")
            return []
        
        try:
            # Fetch unread emails
            emails = self.gmail_client.get_unread_emails(max_results=self.batch_size)
            
            processed_emails = []
            for email in emails:
                if self.should_process(email):
                    result = self.process_email(email)
                    if result:
                        processed_emails.append(result)
            
            logger.info(f"Poll complete: {len(emails)} checked, {len(processed_emails)} processed")
            return processed_emails
            
        except Exception as e:
            logger.error(f"Error polling emails: {e}")
            self._error_count += 1
            return []
    
    def process_email(self, email: dict) -> Optional[dict]:
        """Process a single email.
        
        Args:
            email: Email dict from GmailClient
            
        Returns:
            Draft dict if draft was created, None otherwise
        """
        self._processed_count += 1
        
        try:
            # Use callback if provided
            if self.on_new_email:
                result = self.on_new_email(email)
                if result:
                    self._draft_created_count += 1
                return result
            
            # Use response generator if available
            if self.response_generator:
                draft = self.response_generator.generate_response(email)
                if draft:
                    self._draft_created_count += 1
                return draft
            
            logger.warning(f"No handler configured for email: {email.get('id', 'unknown')}")
            return None
            
        except Exception as e:
            logger.error(f"Error processing email {email.get('id', 'unknown')}: {e}")
            self._error_count += 1
            return None
    
    def should_process(self, email: dict) -> bool:
        """Determine if email should be processed.
        
        Filters out:
        - Already processed emails
        - Spam
        - Promotional emails
        - Sent emails
        - Automated/no-reply emails
        
        Args:
            email: Email dict
            
        Returns:
            True if email should be processed
        """
        # Check if already processed (has been seen before)
        if self.db:
            email_id = email.get('id')
            if self.db.is_processed(email_id):
                return False
        
        # Filter out spam
        labels = email.get('labelIds', [])
        if 'SPAM' in labels or 'TRASH' in labels:
            return False
        
        # Filter out sent emails
        if 'SENT' in labels or 'OUTBOX' in labels:
            return False
        
        # Filter out promotional emails
        if is_promotional_email(email):
            return False
        
        # Filter out automated emails
        if is_automated_email(email):
            return False
        
        return True
    
    def _setup_signal_handlers(self):
        """Set up graceful shutdown handlers."""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            self._signal_received = signum
            self.stop()
        
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
    
    def get_status(self) -> dict:
        """Get watcher status.
        
        Returns:
            Dict with running status, last check time, stats
        """
        return {
            'running': self._running,
            'last_check': self._last_check.isoformat() if self._last_check else None,
            'poll_interval': self.poll_interval,
            'batch_size': self.batch_size,
            'processed_count': self._processed_count,
            'draft_created_count': self._draft_created_count,
            'error_count': self._error_count,
            'signal_received': self._signal_received
        }


# Email filtering utilities

def is_automated_email(email: dict) -> bool:
    """Check if email is from automated system.
    
    Args:
        email: Email dict
        
    Returns:
        True if email appears to be automated
    """
    # Check sender email address
    sender = email.get('from', '') or email.get('sender', '')
    sender_lower = sender.lower()
    
    # Check sender domain
    domain = extract_sender_domain(email)
    domain_lower = domain.lower() if domain else ''
    
    # Check against skip domains
    for skip_domain in SKIP_DOMAINS:
        if skip_domain in domain_lower:
            return True
    
    # Check for common automated patterns in sender
    automated_patterns = [
        r'^noreply@',
        r'^no-reply@',
        r'^donotreply@',
        r'^do-not-reply@',
        r'^notifications?@',
        r'^alerts?@',
        r'^automated@',
        r'^automation@',
        r'^bot@',
        r'^system@',
    ]
    
    for pattern in automated_patterns:
        if re.search(pattern, sender_lower):
            return True
    
    # Check subject for automated patterns
    subject = email.get('subject', '') or ''
    subject_lower = subject.lower()
    
    for pattern in SKIP_PATTERNS:
        if pattern in subject_lower:
            return True
    
    return False


def is_promotional_email(email: dict) -> bool:
    """Check if email is promotional/marketing.
    
    Args:
        email: Email dict
        
    Returns:
        True if email appears to be promotional
    """
    # Check subject and snippet for promotional keywords
    subject = (email.get('subject', '') or '').lower()
    snippet = (email.get('snippet', '') or '').lower()
    text = subject + ' ' + snippet
    
    for pattern in SKIP_PATTERNS:
        if pattern in text:
            return True
    
    # Check label IDs for category
    label_ids = email.get('labelIds', [])
    if 'CATEGORY_PROMOTIONS' in label_ids:
        return True
    
    return False


def extract_sender_domain(email: dict) -> str:
    """Extract domain from sender email address.
    
    Args:
        email: Email dict
        
    Returns:
        Domain string or empty string if not found
    """
    sender = email.get('from', '') or email.get('sender', '')
    
    # Extract email address using regex
    match = re.search(r'@([a-zA-Z0-9.-]+)', sender)
    if match:
        return match.group(1)
    
    return ''


# Domain patterns to filter out
SKIP_DOMAINS = [
    'noreply', 'no-reply', 'donotreply', 'do-not-reply',
    'notifications', 'notification', 'alerts', 'alert',
    'automated', 'automation', 'bot', 'system'
]

SKIP_PATTERNS = [
    'unsubscribe', 'opt-out', 'opt out',
    'marketing', 'newsletter', 'promotion',
    'auto-generated', 'auto generated', 'automated'
]


def run_watcher():
    """CLI entry point to run the watcher."""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Get configuration from environment
    poll_interval = int(os.environ.get('POLL_INTERVAL', EmailWatcher.DEFAULT_POLL_INTERVAL))
    batch_size = int(os.environ.get('BATCH_SIZE', EmailWatcher.DEFAULT_BATCH_SIZE))
    
    logger.info(f"Starting email watcher (poll_interval={poll_interval}, batch_size={batch_size})")
    
    # Create watcher (dependencies will be None, can be injected later)
    watcher = EmailWatcher(
        poll_interval=poll_interval,
        batch_size=batch_size
    )
    
    try:
        watcher.start()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
        watcher.stop()


if __name__ == '__main__':
    run_watcher()
