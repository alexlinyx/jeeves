"""E2E test configuration and fixtures."""
import pytest
import json
import os
from unittest.mock import Mock, MagicMock, patch
from typing import Dict, List

# Sample emails for testing
SAMPLE_EMAILS = [
    {
        "id": "email_001",
        "thread_id": "thread_001",
        "from": "colleague@company.com",
        "to": "me@example.com",
        "subject": "Project Update Request",
        "body_text": "Hey, can you give me an update on the project status?",
        "date": "2024-01-15T10:00:00Z"
    },
    {
        "id": "email_002",
        "thread_id": "thread_002",
        "from": "client@external.com",
        "to": "me@example.com",
        "subject": "Meeting Tomorrow",
        "body_text": "I'd like to schedule a meeting tomorrow at 2pm. Does that work?",
        "date": "2024-01-15T11:00:00Z"
    },
    {
        "id": "email_003",
        "thread_id": "thread_003",
        "from": "noreply@newsletter.com",
        "to": "me@example.com",
        "subject": "Your Weekly Newsletter",
        "body_text": "Here are this week's top stories...",
        "date": "2024-01-15T12:00:00Z"
    },
    {
        "id": "email_004",
        "thread_id": "thread_004",
        "from": "spam@unknown.com",
        "to": "me@example.com",
        "subject": "CONGRATULATIONS YOU WON!!!",
        "body_text": "Click here to claim your prize...",
        "date": "2024-01-15T13:00:00Z"
    },
    {
        "id": "email_005",
        "thread_id": "thread_005",
        "from": "bank@financial.com",
        "to": "me@example.com",
        "subject": "Wire Transfer Confirmation",
        "body_text": "Please confirm the wire transfer of $50,000...",
        "date": "2024-01-15T14:00:00Z"
    },
    {
        "id": "email_006",
        "thread_id": "thread_006",
        "from": "boss@company.com",
        "to": "me@example.com",
        "subject": "URGENT: Client complaint",
        "body_text": "We need to address this client issue ASAP. Please call me immediately.",
        "date": "2024-01-15T15:00:00Z"
    },
    {
        "id": "email_007",
        "thread_id": "thread_007",
        "from": "friend@social.com",
        "to": "me@example.com",
        "subject": "Weekend plans?",
        "body_text": "Hey! Want to grab coffee this weekend?",
        "date": "2024-01-15T16:00:00Z"
    }
]


@pytest.fixture
def sample_emails():
    """Sample email fixtures for testing."""
    return SAMPLE_EMAILS.copy()


@pytest.fixture
def sample_email():
    """Single sample email for simpler tests."""
    return SAMPLE_EMAILS[0].copy()


@pytest.fixture
def mock_gmail_client(sample_emails):
    """Mock Gmail client for testing."""
    mock_client = MagicMock()
    
    # Mock list_emails
    mock_client.list_emails.return_value = sample_emails
    
    # Mock get_email
    def get_email_by_id(email_id):
        for email in sample_emails:
            if email['id'] == email_id:
                return email
        return None
    mock_client.get_email.side_effect = get_email_by_id
    
    # Mock create_draft
    mock_client.create_draft.return_value = "draft_001"
    
    # Mock send_draft
    mock_client.send_draft.return_value = True
    
    # Mock list_drafts
    mock_client.list_drafts.return_value = [
        {'id': 'draft_001', 'message_id': 'msg_001'}
    ]
    
    return mock_client


@pytest.fixture
def mock_llm():
    """Mock LLM for deterministic testing."""
    mock = MagicMock()
    
    # Define responses based on tone
    responses = {
        'casual': "Hey! Yeah, the project is going well. We're on track for the deadline.",
        'formal': "Dear colleague, I am writing to provide you with an update on the project status. We are currently on schedule.",
        'concise': "Project is on track.",
        'match_style': "Sure, here's the update: we're making good progress."
    }
    
    def generate_response(prompt, tone='casual', **kwargs):
        return responses.get(tone, responses['casual'])
    
    mock.generate_response.side_effect = generate_response
    mock.generate.return_value = "Generated response text"
    
    return mock


@pytest.fixture
def mock_rag():
    """Mock RAG pipeline for testing."""
    mock = MagicMock()
    
    # Mock context retrieval
    mock.get_context.return_value = "Relevant context from previous emails about project timeline."
    
    # Mock indexing
    mock.index_email.return_value = True
    
    # Mock search
    mock.search.return_value = [
        {"text": "Previous discussion about project", "score": 0.9}
    ]
    
    return mock


@pytest.fixture
def mock_response_generator(mock_llm, mock_rag):
    """Mock Response Generator for testing."""
    mock = MagicMock()
    
    def generate(email, tone='casual'):
        context = mock_rag.get_context(email['id'])
        return mock_llm.generate_response(
            prompt=f"Email from {email['from']}: {email['body_text']}",
            tone=tone
        )
    
    mock.generate.side_effect = generate
    mock.get_suggested_tone.return_value = 'casual'
    
    return mock


@pytest.fixture
def mock_confidence_scorer():
    """Mock Confidence Scorer for testing."""
    mock = MagicMock()
    
    def score_email(email, response):
        # Simple scoring logic for testing
        body_lower = email.get('body_text', '').lower()
        
        # Financial emails get low confidence
        if 'financial' in body_lower or 'wire' in body_lower or '$' in body_lower:
            return 0.3
        
        # Urgent emails get low confidence
        if 'urgent' in body_lower or 'asap' in body_lower or 'immediately' in body_lower:
            return 0.4
        
        # Simple requests get high confidence
        if '?' in email.get('subject', '') or '?' in body_lower:
            return 0.9
        
        return 0.7
    
    mock.score_email.side_effect = score_email
    mock.should_auto_send.return_value = False
    
    def set_auto_send(value):
        mock.should_auto_send.return_value = value
    
    mock.set_auto_send = set_auto_send
    
    return mock


@pytest.fixture
def mock_filter():
    """Mock Email Filter for testing."""
    mock = MagicMock()
    
    def should_process(email):
        """Determine if email should be processed."""
        sender = email.get('from', '').lower()
        subject = email.get('subject', '').lower()
        body = email.get('body_text', '').lower()
        
        # Filter noreply
        if 'noreply' in sender or 'no-reply' in sender:
            return False, 'noreply_sender'
        
        # Filter promotional
        promotional_keywords = ['newsletter', 'promo', 'deal', 'offer', 'subscribe']
        if any(kw in subject for kw in promotional_keywords):
            return False, 'promotional'
        
        # Filter spam
        spam_keywords = ['won', 'prize', 'winner', 'congratulations', 'click here']
        if any(kw in body for kw in spam_keywords):
            return False, 'spam'
        
        return True, None
    
    mock.should_process.side_effect = should_process
    
    return mock


@pytest.fixture
def test_db(tmp_path):
    """Temporary database for testing."""
    db_path = tmp_path / "test_jeeves.db"
    
    # Create a simple class as mock database
    class TestDatabase:
        def __init__(self):
            self.drafts = {}
            self.processed_emails = set()
            self.settings = {}
        
        def save_draft(self, draft_id, email_id, content, tone):
            self.drafts[draft_id] = {
                'email_id': email_id,
                'content': content,
                'tone': tone,
                'status': 'pending'
            }
        
        def get_draft(self, draft_id):
            return self.drafts.get(draft_id)
        
        def update_draft_status(self, draft_id, status):
            if draft_id in self.drafts:
                self.drafts[draft_id]['status'] = status
        
        def mark_email_processed(self, email_id):
            self.processed_emails.add(email_id)
        
        def is_email_processed(self, email_id):
            return email_id in self.processed_emails
    
    return TestDatabase()


@pytest.fixture
def e2e_pipeline(mock_gmail_client, mock_llm, mock_rag, mock_response_generator, 
                 mock_confidence_scorer, mock_filter, test_db):
    """Complete E2E pipeline with mocked components."""
    
    class E2EPipeline:
        """E2E Pipeline for testing full flows."""
        
        def __init__(self):
            self.gmail = mock_gmail_client
            self.llm = mock_llm
            self.rag = mock_rag
            self.response_generator = mock_response_generator
            self.confidence = mock_confidence_scorer
            self.filter = mock_filter
            self.db = test_db
            self.sent_emails = []
            self.drafts_created = []
        
        def process_email(self, email, tone='casual'):
            """Process a single email through the full pipeline."""
            # Step 1: Filter
            should_process, filter_reason = self.filter.should_process(email)
            if not should_process:
                return {'status': 'filtered', 'reason': filter_reason}
            
            # Step 2: Check if already processed
            if self.db.is_email_processed(email['id']):
                return {'status': 'skipped', 'reason': 'already_processed'}
            
            # Step 3: Get context from RAG
            context = self.rag.get_context(email['id'])
            
            # Step 4: Generate response
            response = self.response_generator.generate(email, tone)
            
            # Step 5: Score confidence
            confidence = self.confidence.score_email(email, response)
            auto_send = confidence >= 0.8
            
            # Step 6: Create draft
            draft_id = self.gmail.create_draft(
                thread_id=email['thread_id'],
                to=email['from'],
                subject=f"Re: {email['subject']}",
                body=response
            )
            self.drafts_created.append(draft_id)
            
            # Step 7: Save to database
            self.db.save_draft(draft_id, email['id'], response, tone)
            
            return {
                'status': 'draft_created',
                'draft_id': draft_id,
                'response': response,
                'confidence': confidence,
                'auto_send': auto_send
            }
        
        def approve_draft(self, draft_id):
            """Approve and send a draft."""
            self.gmail.send_draft(draft_id)
            self.db.update_draft_status(draft_id, 'sent')
            self.sent_emails.append(draft_id)
            return True
        
        def reject_draft(self, draft_id):
            """Reject a draft."""
            self.db.update_draft_status(draft_id, 'rejected')
            return True
        
        def edit_draft(self, draft_id, new_content):
            """Edit a draft."""
            draft = self.db.get_draft(draft_id)
            if draft:
                draft['content'] = new_content
                self.db.drafts[draft_id] = draft
            return draft
    
    return E2EPipeline()


@pytest.fixture
def email_fixtures_path():
    """Path to email fixtures directory."""
    return os.path.join(os.path.dirname(__file__), 'fixtures', 'emails')


@pytest.fixture
def load_email_fixture(email_fixtures_path):
    """Helper to load email fixtures from JSON files."""
    def _load(fixture_name):
        fixture_file = os.path.join(email_fixtures_path, f"{fixture_name}.json")
        if os.path.exists(fixture_file):
            with open(fixture_file, 'r') as f:
                return json.load(f)
        return None
    return _load
