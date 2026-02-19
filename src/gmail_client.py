"""Gmail client for Jeeves email operations."""
import os
import json
from typing import List, Dict, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


class GmailClient:
    """Gmail API wrapper for Jeeves email operations."""
    
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.compose',
        'https://www.googleapis.com/auth/gmail.send'
    ]
    
    def __init__(self, creds_path: str = None, token_path: str = "data/gmail_token.json"):
        """Initialize Gmail client.
        
        Args:
            creds_path: Path to OAuth credentials.json (from Google Cloud Console)
            token_path: Path to store/load refresh token
        """
        self.creds_path = creds_path or os.environ.get('GMAIL_CREDENTIALS_PATH', 'data/credentials.json')
        self.token_path = token_path
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate using OAuth 2.0."""
        from google.auth.transport.requests import Request
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_path):
            with open(self.token_path, 'r') as f:
                creds = Credentials.from_authorized_user_info(json.load(f), self.SCOPES)
        
        # If no valid credentials, run OAuth flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            elif os.path.exists(self.creds_path):
                flow = InstalledAppFlow.from_client_secrets_file(self.creds_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
                # Save token for future use
                with open(self.token_path, 'w') as f:
                    f.write(creds.to_json())
        
        self.service = build('gmail', 'v1', credentials=creds)
    
    def list_emails(self, limit: int = 100) -> List[Dict]:
        """Fetch recent emails.
        
        Args:
            limit: Maximum number of emails to fetch
            
        Returns:
            List of email dicts with: id, thread_id, subject, from, date, snippet
        """
        results = self.service.users().messages().list(
            userId='me', maxResults=limit
        ).execute()
        
        messages = results.get('messages', [])
        emails = []
        
        for msg in messages:
            email = self.get_email(msg['id'])
            if email:
                emails.append(email)
        
        return emails
    
    def get_email(self, message_id: str) -> Dict:
        """Fetch a specific email by message ID.
        
        Args:
            message_id: Gmail message ID
            
        Returns:
            Email dict with: id, thread_id, subject, from, to, date, body_text, body_html
        """
        import base64
        
        msg = self.service.users().messages().get(
            userId='me', id=message_id, format='full'
        ).execute()
        
        headers = msg.get('payload', {}).get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
        from_addr = next((h['value'] for h in headers if h['name'] == 'From'), '')
        to_addr = next((h['value'] for h in headers if h['name'] == 'To'), '')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
        
        # Extract body
        body_text = ''
        body_html = ''
        parts = msg.get('payload', {}).get('parts', [])
        
        def get_body(parts):
            text = ''
            html = ''
            for part in parts:
                if part.get('mimeType') == 'text/plain':
                    text = part.get('body', {}).get('data', '')
                elif part.get('mimeType') == 'text/html':
                    html = part.get('body', {}).get('data', '')
                if part.get('parts'):
                    t, h = get_body(part['parts'])
                    text = text or t
                    html = html or h
            return text, html
        
        body_text, body_html = get_body(parts)
        
        if body_text:
            body_text = base64.urlsafe_b64decode(body_text).decode('utf-8')
        if body_html:
            body_html = base64.urlsafe_b64decode(body_html).decode('utf-8')
        
        return {
            'id': msg['id'],
            'thread_id': msg['threadId'],
            'subject': subject,
            'from': from_addr,
            'to': to_addr,
            'date': date,
            'snippet': msg.get('snippet', ''),
            'body_text': body_text,
            'body_html': body_html
        }
    
    def create_draft(self, thread_id: str, to: str, subject: str, body: str) -> str:
        """Create a draft reply.
        
        Args:
            thread_id: Gmail thread ID
            to: Recipient email address
            subject: Email subject
            body: Draft body content
            
        Returns:
            Draft ID
        """
        import base64
        
        message = f"To: {to}\nSubject: {subject}\n\n{body}"
        encoded_message = base64.urlsafe_b64encode(message.encode('utf-8')).decode('utf-8')
        
        draft = {
            'message': {
                'threadId': thread_id,
                'raw': encoded_message
            }
        }
        
        result = self.service.users().drafts().create(
            userId='me', body=draft
        ).execute()
        
        return result['id']
    
    def send_draft(self, draft_id: str) -> bool:
        """Send a draft.
        
        Args:
            draft_id: Gmail draft ID
            
        Returns:
            True if successful
        """
        # First get the draft
        draft = self.service.users().drafts().get(
            userId='me', id=draft_id
        ).execute()
        
        # Send the message
        import base64
        message = draft['message']['raw']
        
        self.service.users().messages().send(
            userId='me', body={'raw': message}
        ).execute()
        
        return True
    
    def list_drafts(self, limit: int = 10) -> List[Dict]:
        """List drafts.
        
        Args:
            limit: Maximum number of drafts to fetch
            
        Returns:
            List of draft dicts
        """
        results = self.service.users().drafts().list(
            userId='me', maxResults=limit
        ).execute()
        
        drafts = results.get('drafts', [])
        return [{'id': d['id'], 'message_id': d['message']['id']} for d in drafts]