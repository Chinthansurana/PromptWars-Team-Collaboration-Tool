"""User data model.

Represents a team member with authentication and role information.
Users can be assigned to projects and tasks.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

# Valid user roles
VALID_ROLES = ("admin", "editor", "member")


@dataclass
class User:
    """A team member in the collaboration platform.

    Attributes:
        id: Unique user identifier (Firestore document ID).
        name: Display name of the user.
        email: Email address (unique identifier).
        role: User role (admin, editor, member).
        created_at: Timestamp when user was created.
        updated_at: Timestamp when user was last modified.
    """

    name: str
    email: str
    role: str = "member"
    id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def __post_init__(self):
        """Validate and set defaults after initialization."""
        if self.role not in VALID_ROLES:
            raise ValueError(f"Invalid role: {self.role}. Must be one of {VALID_ROLES}")
        now = datetime.now(timezone.utc).isoformat()
        if self.created_at is None:
            self.created_at = now
        if self.updated_at is None:
            self.updated_at = now

    def to_dict(self) -> dict:
        """Convert user to Firestore-compatible dictionary.

        Returns:
            Dictionary representation of the user.
        """
        data = {
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        if self.id:
            data["id"] = self.id
        return data

    @classmethod
    def from_dict(cls, data: dict, doc_id: str | None = None) -> "User":
        """Create a User instance from a Firestore document.

        Args:
            data: Firestore document data.
            doc_id: Firestore document ID.

        Returns:
            User instance.
        """
        return cls(
            id=doc_id or data.get("id"),
            name=data.get("name", ""),
            email=data.get("email", ""),
            role=data.get("role", "member"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
