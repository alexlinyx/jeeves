"""Notification system using ntfy.sh for sending push notifications."""
import requests
from typing import Optional


class Notifier:
    """Send notifications via ntfy.sh service."""
    
    DEFAULT_TOPIC = "jeeves-drafts"
    DEFAULT_URL = "https://ntfy.sh"
    
    # Priority mappings
    PRIORITIES = {
        "low": 1,
        "default": 3,
        "high": 4,
        "urgent": 5,
    }
    
    def __init__(
        self,
        topic: str = None,
        base_url: str = None,
        default_priority: str = "default",
    ):
        """Initialize notifier with optional custom topic and URL."""
        self.topic = topic or self.DEFAULT_TOPIC
        self.base_url = base_url or self.DEFAULT_URL
        self.default_priority = default_priority
    
    def send(
        self,
        title: str,
        message: str,
        priority: str = "default",
        tags: Optional[list] = None,
    ) -> requests.Response:
        """Send a notification via ntfy.sh.
        
        Args:
            title: Notification title
            message: Notification body message
            priority: Priority level (low, default, high, urgent)
            tags: Optional list of tags/emojis for the notification
            
        Returns:
            Response object from the HTTP request
        """
        url = f"{self.base_url}/{self.topic}"
        
        # Map priority string to integer
        priority_value = self.PRIORITIES.get(priority, self.PRIORITIES["default"])
        
        # Build tags string if provided
        tags_str = ",".join(tags) if tags else None
        
        data = {
            "topic": self.topic,
            "message": message,
            "priority": priority_value,
        }
        
        if title:
            data["title"] = title
            
        if tags_str:
            data["tags"] = tags_str
        
        response = requests.post(url, data=data)
        response.raise_for_status()
        return response
    
    def notify_draft_ready(
        self,
        subject: str,
        sender: str,
        preview: str,
        draft_id: str,
    ) -> requests.Response:
        """Notify that a draft is ready for review.
        
        Args:
            subject: Email subject line
            sender: Original sender email
            preview: Preview of the draft content
            draft_id: Unique identifier for the draft
            
        Returns:
            Response object from the HTTP request
        """
        title = "📝 Draft Ready for Review"
        message = f"Subject: {subject}\nFrom: {sender}\nPreview: {preview}\nDraft ID: {draft_id}"
        tags = ["email", "draft", "pencil"]
        
        return self.send(title=title, message=message, priority="default", tags=tags)
    
    def notify_draft_sent(
        self,
        subject: str,
        recipient: str,
    ) -> requests.Response:
        """Notify that a draft has been sent.
        
        Args:
            subject: Email subject line
            recipient: Recipient email address
            
        Returns:
            Response object from the HTTP request
        """
        title = "✅ Draft Sent Successfully"
        message = f"Subject: {subject}\nTo: {recipient}"
        tags = ["email", "sent", "white_check_mark"]
        
        return self.send(title=title, message=message, priority="default", tags=tags)
    
    def notify_error(
        self,
        error_message: str,
    ) -> requests.Response:
        """Notify about an error that occurred.
        
        Args:
            error_message: Description of the error
            
        Returns:
            Response object from the HTTP request
        """
        title = "❌ Error Occurred"
        message = error_message
        tags = ["error", "warning", "x"]
        
        return self.send(title=title, message=message, priority="high", tags=tags)
    
    @property
    def topic(self) -> str:
        """Get the current topic."""
        return self._topic
    
    @topic.setter
    def topic(self, value: str):
        """Set the topic."""
        self._topic = value
    
    @property
    def base_url(self) -> str:
        """Get the base URL."""
        return self._base_url
    
    @base_url.setter
    def base_url(self, value: str):
        """Set the base URL."""
        self._base_url = value


# Convenience functions
def notify_draft_ready(subject: str, sender: str, preview: str, draft_id: str, **kwargs) -> requests.Response:
    """Quick function to notify draft ready."""
    notifier = Notifier(**kwargs)
    return notifier.notify_draft_ready(subject, sender, preview, draft_id)


def notify_draft_sent(subject: str, recipient: str, **kwargs) -> requests.Response:
    """Quick function to notify draft sent."""
    notifier = Notifier(**kwargs)
    return notifier.notify_draft_sent(subject, recipient)


def notify_error(error_message: str, **kwargs) -> requests.Response:
    """Quick function to notify error."""
    notifier = Notifier(**kwargs)
    return notifier.notify_error(error_message)


def send(title: str, message: str, priority: str = "default", **kwargs) -> requests.Response:
    """Quick function to send a notification."""
    notifier = Notifier(**kwargs)
    return notifier.send(title, message, priority)
