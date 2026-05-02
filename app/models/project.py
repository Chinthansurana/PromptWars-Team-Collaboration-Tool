"""Project data model.

Represents a team project with members, status tracking,
and metadata for collaboration workflows.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

# Valid project statuses
VALID_STATUSES = ("active", "archived", "completed")


@dataclass
class Project:
    """A team collaboration project.

    Attributes:
        id: Unique project identifier (Firestore document ID).
        name: Project display name.
        description: Detailed project description.
        status: Current status (active, archived, completed).
        members: List of team member names.
        created_at: Timestamp when project was created.
        updated_at: Timestamp when project was last modified.
    """

    name: str
    description: str = ""
    status: str = "active"
    members: list[str] = field(default_factory=list)
    id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def __post_init__(self):
        """Validate and set defaults after initialization."""
        if self.status not in VALID_STATUSES:
            raise ValueError(f"Invalid status: {self.status}. Must be one of {VALID_STATUSES}")
        now = datetime.now(timezone.utc).isoformat()
        if self.created_at is None:
            self.created_at = now
        if self.updated_at is None:
            self.updated_at = now

    def to_dict(self) -> dict:
        """Convert project to Firestore-compatible dictionary.

        Returns:
            Dictionary representation of the project.
        """
        data = {
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "members": self.members,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        if self.id:
            data["id"] = self.id
        return data

    @classmethod
    def from_dict(cls, data: dict, doc_id: str | None = None) -> "Project":
        """Create a Project instance from a Firestore document.

        Args:
            data: Firestore document data.
            doc_id: Firestore document ID.

        Returns:
            Project instance.
        """
        return cls(
            id=doc_id or data.get("id"),
            name=data.get("name", ""),
            description=data.get("description", ""),
            status=data.get("status", "active"),
            members=data.get("members", []),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
