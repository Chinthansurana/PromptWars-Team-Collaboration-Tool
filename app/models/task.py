"""Task data model.

Represents a task within a project with status tracking,
priority levels, assignment, and tagging support.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

# Valid task statuses for Kanban workflow
VALID_STATUSES = ("todo", "in_progress", "review", "done")

# Valid priority levels
VALID_PRIORITIES = ("low", "medium", "high", "critical")


@dataclass
class Task:
    """A task within a team project.

    Attributes:
        id: Unique task identifier (Firestore document ID).
        project_id: ID of the parent project.
        title: Task title / summary.
        description: Detailed task description.
        status: Kanban status (todo, in_progress, review, done).
        priority: Priority level (low, medium, high, critical).
        assignee: Name of the assigned team member.
        due_date: Optional due date in ISO format.
        tags: List of categorization tags.
        created_at: Timestamp when task was created.
        updated_at: Timestamp when task was last modified.
    """

    title: str
    project_id: str = ""
    description: str = ""
    status: str = "todo"
    priority: str = "medium"
    assignee: str = ""
    due_date: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    id: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def __post_init__(self):
        """Validate and set defaults after initialization."""
        if self.status not in VALID_STATUSES:
            raise ValueError(f"Invalid status: {self.status}. Must be one of {VALID_STATUSES}")
        if self.priority not in VALID_PRIORITIES:
            raise ValueError(f"Invalid priority: {self.priority}. Must be one of {VALID_PRIORITIES}")
        now = datetime.now(timezone.utc).isoformat()
        if self.created_at is None:
            self.created_at = now
        if self.updated_at is None:
            self.updated_at = now

    def to_dict(self) -> dict:
        """Convert task to Firestore-compatible dictionary.

        Returns:
            Dictionary representation of the task.
        """
        data = {
            "title": self.title,
            "project_id": self.project_id,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "assignee": self.assignee,
            "due_date": self.due_date,
            "tags": self.tags,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        if self.id:
            data["id"] = self.id
        return data

    @classmethod
    def from_dict(cls, data: dict, doc_id: str | None = None) -> "Task":
        """Create a Task instance from a Firestore document.

        Args:
            data: Firestore document data.
            doc_id: Firestore document ID.

        Returns:
            Task instance.
        """
        return cls(
            id=doc_id or data.get("id"),
            project_id=data.get("project_id", ""),
            title=data.get("title", ""),
            description=data.get("description", ""),
            status=data.get("status", "todo"),
            priority=data.get("priority", "medium"),
            assignee=data.get("assignee", ""),
            due_date=data.get("due_date"),
            tags=data.get("tags", []),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
