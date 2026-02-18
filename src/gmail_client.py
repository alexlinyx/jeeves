"""Gmail client for Jeeves email operations."""
import os
import json
import base64
from typing import List, Dict, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request


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
                os.makedirs(os.path.dirname(self.token_path), exist_ok=True)
                with open(self.token_path, 'w') as f:
                    f.write(creds.to_json())
        
        if creds:
            self.service = build('gmail', 'v1', credentials=creds)
    
    def list_emails(self, limit: int = 100) -> List[Dict]:
        """Fetch recent emails."""
        if not self.service:
            raise RuntimeError("Not authenticated")
        
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
        """Fetch a specific email by message ID."""
        if not self.service:
            raise RuntimeError("Not authenticated")
        
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
        
        def extract_body(parts):
            text, html = '', ''
            for part in parts:
                mt = part.get('mimeType', '')
                if mt == 'text/plain':
                    data = part.get('body', {}).get('data', '')
                    if data:
                        text = base64.urlsafe_b64decode(data).decode('utf-8')
                elif mt == 'text/html':
                    data = part.get('body', {}).get('data', '')
                    if data:
                        html = base64.urlsafe_b64decode(data).decode('utf-8')
                if part.get('parts'):
                    t, h = extract_body(part['parts'])
                    text = text or t
                    html = html or h
            return text, html
        
        parts = msg.get('payload', {}).get('parts', [])
        body_text, body_html = extract_body(parts)
        
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
        """Create a draft reply."""
        if not self.service:
            raise RuntimeError("Not authenticated")
        
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
        """Send a draft."""
        if not self.service:
            raise RuntimeError("Not authenticated")
        
        draft = self.service.users().drafts().get(
            userId='me', id=draft_id
        ).execute()
        
        message = draft['message']['raw']
        self.service.users().messages().send(
            userId='me', body={'raw': message}
        ).execute()
        
        return True
    
    def list_drafts(self, limit: int = 10) -> List[Dict]:
        """List drafts."""
        if not self.service:
            raise RuntimeError("Not authenticated")
        
        results = self.service.users().drafts().list(
            userId='me', maxResults=limit
        ).execute()
        
        drafts = results.get('drafts', [])
        return [{'id': d['id'], 'message_id': d['message']['id']} for d in drafts]
