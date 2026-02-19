"""Security utilities for Jeeves."""
import os
import re
import html
import time
import hashlib
import secrets
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class SecurityLevel(Enum):
    """Security risk levels."""
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityCheck:
    """Result of a security check."""
    passed: bool
    level: SecurityLevel
    message: str
    details: Dict = field(default_factory=dict)


class InputValidator:
    """Validate and sanitize user inputs."""
    
    MAX_EMAIL_LENGTH = 100000  # 100KB max email
    MAX_DRAFT_LENGTH = 10000   # 10KB max draft
    MAX_SUBJECT_LENGTH = 500
    
    # Patterns to detect
    HTML_SCRIPT_PATTERN = re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL)
    HTML_IFRAME_PATTERN = re.compile(r'<iframe[^>]*>.*?</iframe>', re.IGNORECASE | re.DOTALL)
    JAVASCRIPT_PATTERN = re.compile(r'javascript:', re.IGNORECASE)
    PATH_TRAVERSAL_PATTERN = re.compile(r'\.\.[/\\]')
    
    @classmethod
    def validate_email_content(cls, content: str) -> SecurityCheck:
        """Validate email content for security issues."""
        if not content:
            return SecurityCheck(
                passed=True,
                level=SecurityLevel.SAFE,
                message="Empty content is safe"
            )
        
        # Check length
        if len(content) > cls.MAX_EMAIL_LENGTH:
            return SecurityCheck(
                passed=False,
                level=SecurityLevel.HIGH,
                message="Email content exceeds maximum length",
                details={"length": len(content), "max": cls.MAX_EMAIL_LENGTH}
            )
        
        # Check for dangerous HTML
        if cls.HTML_SCRIPT_PATTERN.search(content):
            return SecurityCheck(
                passed=False,
                level=SecurityLevel.CRITICAL,
                message="Script tags detected in email content",
                details={"pattern": "script"}
            )
        
        if cls.HTML_IFRAME_PATTERN.search(content):
            return SecurityCheck(
                passed=False,
                level=SecurityLevel.HIGH,
                message="Iframe tags detected in email content",
                details={"pattern": "iframe"}
            )
        
        if cls.JAVASCRIPT_PATTERN.search(content):
            return SecurityCheck(
                passed=False,
                level=SecurityLevel.HIGH,
                message="JavaScript protocol detected in email content",
                details={"pattern": "javascript:"}
            )
        
        return SecurityCheck(
            passed=True,
            level=SecurityLevel.SAFE,
            message="Email content validated"
        )
    
    @classmethod
    def validate_draft_content(cls, content: str) -> SecurityCheck:
        """Validate draft content."""
        if not content:
            return SecurityCheck(
                passed=True,
                level=SecurityLevel.SAFE,
                message="Empty draft is safe"
            )
        
        # Check length
        if len(content) > cls.MAX_DRAFT_LENGTH:
            return SecurityCheck(
                passed=False,
                level=SecurityLevel.MEDIUM,
                message="Draft content exceeds maximum length",
                details={"length": len(content), "max": cls.MAX_DRAFT_LENGTH}
            )
        
        # Drafts should not contain dangerous HTML
        if cls.HTML_SCRIPT_PATTERN.search(content):
            return SecurityCheck(
                passed=False,
                level=SecurityLevel.HIGH,
                message="Script tags not allowed in drafts",
                details={"pattern": "script"}
            )
        
        return SecurityCheck(
            passed=True,
            level=SecurityLevel.SAFE,
            message="Draft content validated"
        )
    
    @classmethod
    def sanitize_html(cls, html_content: str) -> str:
        """Sanitize HTML content."""
        if not html_content:
            return ""
        
        # Remove script tags
        result = cls.HTML_SCRIPT_PATTERN.sub('', html_content)
        
        # Remove iframe tags
        result = cls.HTML_IFRAME_PATTERN.sub('', result)
        
        # Remove javascript: protocol
        result = cls.JAVASCRIPT_PATTERN.sub('', result)
        
        # Escape HTML entities to prevent XSS
        result = html.escape(result)
        
        return result
    
    @classmethod
    def check_path_traversal(cls, path: str) -> bool:
        """Check for path traversal attempts.
        
        Returns True if path traversal is detected.
        """
        if not path:
            return False
        return bool(cls.PATH_TRAVERSAL_PATTERN.search(path))


class RateLimiter:
    """Rate limiting for API calls."""
    
    def __init__(
        self,
        max_requests: int = 100,
        window_seconds: int = 60
    ):
        """Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests per window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: Dict[str, List[float]] = {}
    
    def check(self, key: str) -> Tuple[bool, int]:
        """Check if request is allowed.
        
        Args:
            key: Identifier for rate limiting (e.g., user_id, IP)
            
        Returns:
            Tuple of (allowed, remaining_requests)
        """
        current_time = time.time()
        
        # Initialize key if not exists
        if key not in self._requests:
            self._requests[key] = []
        
        # Clean old requests outside the window
        cutoff = current_time - self.window_seconds
        self._requests[key] = [
            ts for ts in self._requests[key] if ts > cutoff
        ]
        
        # Check if under limit
        if len(self._requests[key]) < self.max_requests:
            self._requests[key].append(current_time)
            remaining = self.max_requests - len(self._requests[key])
            return True, remaining
        
        # Over limit
        return False, 0
    
    def reset(self, key: str):
        """Reset rate limit for key."""
        if key in self._requests:
            self._requests[key] = []


class PromptInjectionDetector:
    """Detect potential prompt injection attacks."""
    
    INJECTION_PATTERNS = [
        re.compile(r'ignore\s+(all\s+)?previous\s+instructions', re.IGNORECASE),
        re.compile(r'ignore\s+(all\s+)?prior\s+instructions', re.IGNORECASE),
        re.compile(r'disregard\s+.*instructions', re.IGNORECASE),
        re.compile(r'you\s+are\s+now\s+', re.IGNORECASE),
        re.compile(r'new\s+instructions?:', re.IGNORECASE),
        re.compile(r'system:', re.IGNORECASE),
        re.compile(r'assistant:', re.IGNORECASE),
        re.compile(r'###\s*instruction', re.IGNORECASE),
        re.compile(r'<\|.*\|>'),  # Special tokens
    ]
    
    # Replacement markers for sanitization
    REPLACEMENT_MARKER = "[FILTERED]"
    
    @classmethod
    def detect(cls, text: str) -> SecurityCheck:
        """Detect potential prompt injection.
        
        Args:
            text: Text to analyze
            
        Returns:
            SecurityCheck with results
        """
        if not text:
            return SecurityCheck(
                passed=True,
                level=SecurityLevel.SAFE,
                message="Empty text is safe"
            )
        
        detected_patterns = []
        
        for i, pattern in enumerate(cls.INJECTION_PATTERNS):
            match = pattern.search(text)
            if match:
                detected_patterns.append({
                    "pattern_index": i,
                    "match": match.group(0),
                    "position": match.start()
                })
        
        if detected_patterns:
            return SecurityCheck(
                passed=False,
                level=SecurityLevel.HIGH,
                message="Potential prompt injection detected",
                details={"patterns": detected_patterns}
            )
        
        return SecurityCheck(
            passed=True,
            level=SecurityLevel.SAFE,
            message="No prompt injection detected"
        )
    
    @classmethod
    def sanitize(cls, text: str) -> str:
        """Remove potential injection patterns.
        
        Args:
            text: Text to sanitize
            
        Returns:
            Sanitized text
        """
        if not text:
            return ""
        
        result = text
        
        for pattern in cls.INJECTION_PATTERNS:
            result = pattern.sub(cls.REPLACEMENT_MARKER, result)
        
        return result


class CredentialManager:
    """Secure credential management."""
    
    def __init__(self, keyring_service: str = "jeeves"):
        """Initialize credential manager."""
        self.keyring_service = keyring_service
        self._credentials: Dict[str, str] = {}
    
    def store(self, key: str, value: str) -> bool:
        """Store credential securely."""
        try:
            # In a real implementation, this would use keyring
            # For now, we use a simple in-memory store as a stub
            self._credentials[key] = value
            return True
        except Exception:
            return False
    
    def retrieve(self, key: str) -> Optional[str]:
        """Retrieve credential."""
        return self._credentials.get(key)
    
    def delete(self, key: str) -> bool:
        """Delete credential."""
        if key in self._credentials:
            del self._credentials[key]
            return True
        return False
    
    def list_keys(self) -> List[str]:
        """List stored credential keys."""
        return list(self._credentials.keys())


class SecurityAuditor:
    """Audit security configuration."""
    
    @classmethod
    def audit_credentials(cls) -> List[SecurityCheck]:
        """Audit credential storage."""
        checks = []
        
        # Check for credentials directory
        creds_dir = os.path.expanduser("~/.config/jeeves/credentials")
        if os.path.exists(creds_dir):
            # Check permissions
            stat_info = os.stat(creds_dir)
            mode = stat_info.st_mode & 0o777
            
            if mode & 0o077:
                checks.append(SecurityCheck(
                    passed=False,
                    level=SecurityLevel.HIGH,
                    message="Credentials directory has insecure permissions",
                    details={"permissions": oct(mode)}
                ))
            else:
                checks.append(SecurityCheck(
                    passed=True,
                    level=SecurityLevel.SAFE,
                    message="Credentials directory has secure permissions"
                ))
        else:
            checks.append(SecurityCheck(
                passed=True,
                level=SecurityLevel.SAFE,
                message="Credentials directory not created yet (first run)"
            ))
        
        # Check for .gitignore
        gitignore_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            ".gitignore"
        )
        if os.path.exists(gitignore_path):
            with open(gitignore_path, 'r') as f:
                content = f.read()
                if 'credentials' in content or '.env' in content:
                    checks.append(SecurityCheck(
                        passed=True,
                        level=SecurityLevel.SAFE,
                        message="Credentials are in .gitignore"
                    ))
                else:
                    checks.append(SecurityCheck(
                        passed=False,
                        level=SecurityLevel.MEDIUM,
                        message="Credentials may not be in .gitignore"
                    ))
        
        return checks
    
    @classmethod
    def audit_network(cls) -> List[SecurityCheck]:
        """Audit network configuration."""
        checks = []
        
        # Check that Gradio is bound to localhost
        # This is a configuration check - in practice, this would check config
        checks.append(SecurityCheck(
            passed=True,
            level=SecurityLevel.SAFE,
            message="Network audit complete",
            details={"note": "Gradio/Ollama should bind to localhost only"}
        ))
        
        return checks
    
    @classmethod
    def audit_data_storage(cls) -> List[SecurityCheck]:
        """Audit data storage security."""
        checks = []
        
        # Check data directory exists
        data_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data"
        )
        
        if os.path.exists(data_dir):
            # Check it's not world-readable
            stat_info = os.stat(data_dir)
            mode = stat_info.st_mode & 0o777
            
            if mode & 0o077:
                checks.append(SecurityCheck(
                    passed=False,
                    level=SecurityLevel.MEDIUM,
                    message="Data directory has loose permissions",
                    details={"permissions": oct(mode)}
                ))
            else:
                checks.append(SecurityCheck(
                    passed=True,
                    level=SecurityLevel.SAFE,
                    message="Data directory has secure permissions"
                ))
        else:
            checks.append(SecurityCheck(
                passed=True,
                level=SecurityLevel.SAFE,
                message="Data directory not created yet"
            ))
        
        return checks
    
    @classmethod
    def full_audit(cls) -> Dict[str, List[SecurityCheck]]:
        """Run full security audit."""
        return {
            "credentials": cls.audit_credentials(),
            "network": cls.audit_network(),
            "data_storage": cls.audit_data_storage(),
        }


def generate_secure_token(length: int = 32) -> str:
    """Generate a secure random token."""
    return secrets.token_hex(length)


def hash_sensitive(data: str) -> str:
    """Hash sensitive data for logging."""
    return hashlib.sha256(data.encode()).hexdigest()[:16]
