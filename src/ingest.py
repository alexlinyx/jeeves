"""Email ingestion from Gmail Takeout .mbox files."""
import argparse
import csv
import os
from datetime import datetime
from email import policy
from email.parser import BytesParser
from mailbox import mbox
from typing import List, Dict, Optional
import re


def parse_mbox(mbox_path: str, output_csv: str = "data/training_emails.csv", user_email: str = None, sent_only: bool = False) -> int:
    """Parse .mbox file and extract email data."""
    count = 0
    os.makedirs(os.path.dirname(output_csv) or '.', exist_ok=True)
    
    with open(output_csv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['thread_id', 'from', 'subject', 'body_text', 'sent_by_you', 'timestamp'])
        writer.writeheader()
        
        try:
            for msg in mbox(mbox_path):
                subject = extract_subject(msg)
                body = extract_body(msg)
                if not filter_useful_email(body, subject):
                    continue
                if sent_only and not is_sent_email(msg, user_email):
                    continue
                row = {
                    'thread_id': extract_thread_id(msg) or f"thread_{count}",
                    'from': msg.get('From', ''),
                    'subject': subject,
                    'body_text': clean_body(body),
                    'sent_by_you': 'True' if is_sent_email(msg, user_email) else 'False',
                    'timestamp': get_timestamp(msg) or ''
                }
                writer.writerow(row)
                count += 1
        except Exception as e:
            print(f"Error parsing mbox: {e}")
    
    return count


def extract_email_address(header_value: str) -> str:
    """Extract email address from From header."""
    if not header_value:
        return ''
    match = re.search(r'<(.+?)>|^(.+?)$', header_value)
    if match:
        return match.group(1) or match.group(2) or ''
    return header_value


def clean_body(body: str) -> str:
    """Clean email body text."""
    if not body:
        return ''
    lines = body.split('\n')
    cleaned_lines = [l for l in lines if not l.startswith('>')]
    body = '\n'.join(cleaned_lines)
    body = re.sub(r'\n--\s*\n.*', '', body, flags=re.DOTALL)
    body = re.sub(r'\n\n\n+', '\n\n', body)
    return body.strip()


def is_sent_email(email_message, user_email: str = None) -> bool:
    """Determine if email was sent by user."""
    labels = email_message.get('X-Gmail-Labels', '')
    if 'Sent' in labels:
        return True
    if user_email:
        from_addr = extract_email_address(email_message.get('From', ''))
        if from_addr.lower() == user_email.lower():
            return True
    return False


def get_timestamp(email_message) -> Optional[str]:
    """Extract timestamp from email."""
    date_str = email_message.get('Date')
    if not date_str:
        return None
    try:
        from email.utils import parsedate_to_datetime
        dt = parsedate_to_datetime(date_str)
        return dt.isoformat()
    except:
        return date_str


def extract_thread_id(email_message) -> Optional[str]:
    """Extract thread ID from email headers."""
    thread_top = email_message.get('X-Gmail-Thread-Top')
    if thread_top:
        return thread_top.split()[0] if thread_top else None
    refs = email_message.get('References', '')
    if refs:
        ref_ids = refs.split()
        return ref_ids[-1] if ref_ids else None
    return None


def extract_subject(email_message) -> str:
    """Extract subject line."""
    subject = email_message.get('Subject', '(No Subject)')
    try:
        from email.header import decode_header
        decoded = decode_header(subject)
        subject = ''.join(
            part.decode(encoding or 'utf-8') if isinstance(part, bytes) else part
            for part, encoding in decoded
        )
    except:
        pass
    return subject.strip()


def extract_body(email_message) -> str:
    """Extract body text from email."""
    body = ''
    html_body = ''
    
    def get_parts(parts):
        nonlocal body, html_body
        for part in parts:
            mt = part.get_content_type()
            payload = part.get_payload(decode=True)
            if payload:
                charset = part.get_content_charset() or 'utf-8'
                text = payload.decode(charset, errors='ignore')
                if mt == 'text/plain':
                    body += text
                elif mt == 'text/html':
                    html_body += text
            if part.is_multipart():
                get_parts(part.get_payload())
    
    payload = email_message.get_payload()
    if email_message.is_multipart():
        get_parts(payload)
    else:
        payload = email_message.get_payload(decode=True)
        if payload:
            ct = email_message.get_content_type()
            charset = email_message.get_content_charset() or 'utf-8'
            text = payload.decode(charset, errors='ignore')
            if ct == 'text/plain':
                body = text
            elif ct == 'text/html':
                html_body = text
    
    if body:
        return body
    if html_body:
        return re.sub(r'<[^>]+>', '', html_body)
    return ''


def filter_useful_email(body: str, subject: str) -> bool:
    """Filter out auto-generated emails."""
    auto_patterns = [
        r'auto-?generated', r'auto-?reply', r'out of office', r'ooo',
        r'delivery failed', r'undelivered', r'mailer-?daemon',
        r'noreply', r'no-?reply', r'don\'t reply', r'notification',
    ]
    text = (subject + ' ' + body).lower()
    for pattern in auto_patterns:
        if re.search(pattern, text):
            return False
    if len(body.strip()) < 50:
        return False
    return True


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Ingest emails from Gmail Takeout .mbox file")
    parser.add_argument("--mbox", required=True, help="Path to .mbox file")
    parser.add_argument("--output", default="data/training_emails.csv", help="Output CSV path")
    parser.add_argument("--user-email", help="Your email to detect sent emails")
    parser.add_argument("--sent-only", action="store_true", help="Only extract sent emails")
    args = parser.parse_args()
    count = parse_mbox(args.mbox, args.output, args.user_email, args.sent_only)
    print(f"Processed {count} emails -> {args.output}")


if __name__ == "__main__":
    main()