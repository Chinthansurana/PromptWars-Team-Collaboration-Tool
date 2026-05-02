"""Message data model.

Represents a chat message within a project for team communication.
Supports system messages and AI-generated messages.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


# Message types
VALID_TYPES = ("chat", "system", "ai")


@dataclass
class Message:
    """A message in a project chat channel.

    Attributes:
        id: Unique message identifier (Firestore document ID).
        project_id: ID of the parent project.
        sender: Name of the message sender.
        content: Message text content.
        msg_type: Message type (chat, system, ai).
        timestamp: When the message was sent.
    """

    content: str
    project_id: str = ""
    sender: str = "System"
    msg_type: str = "chat"
    id: Optional[str] = None
    timestamp: Optional[str] = None

    def __post_init__(self):
        """Validate and set defaults after initialization."""
        if self.msg_type not in VALID_TYPES:
            raise ValueError(f"Invalid type: {self.msg_type}. Must be one of {VALID_TYPES}")
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        """Convert message to Firestore-compatible dictionary.

        Returns:
            Dictionary representation of the message.
        """
        data = {
            "project_id": self.project_id,
            "sender": self.sender,
            "content": self.content,
            "msg_type": self.msg_type,
            "timestamp": self.timestamp,
        }
        if self.id:
            data["id"] = self.id
        return data

    @classmethod
    def from_dict(cls, data: dict, doc_id: str | None = None) -> "Message":
        """Create a Message instance from a Firestore document.

        Args:
            data: Firestore document data.
            doc_id: Firestore document ID.

        Returns:
            Message instance.
        """
        return cls(
            id=doc_id or data.get("id"),
            project_id=data.get("project_id", ""),
            sender=data.get("sender", "System"),
            content=data.get("content", ""),
            msg_type=data.get("msg_type", "chat"),
            timestamp=data.get("timestamp"),
        )
