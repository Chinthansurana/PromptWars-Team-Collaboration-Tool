"""Input validation utilities.

Provides validation functions for API request data to ensure
data integrity and prevent malformed input from reaching the database.
"""

import re
from typing import Optional

import bleach


# Maximum field lengths
MAX_NAME_LENGTH = 200
MAX_DESCRIPTION_LENGTH = 5000
MAX_MESSAGE_LENGTH = 2000
MAX_TAG_LENGTH = 50
MAX_TAGS_COUNT = 20
MAX_MEMBERS_COUNT = 50


def sanitize_string(value: str, max_length: int = MAX_NAME_LENGTH) -> str:
    """Sanitize a string input by stripping HTML and limiting length.

    Args:
        value: Raw input string.
        max_length: Maximum allowed length.

    Returns:
        Sanitized string.
    """
    if not isinstance(value, str):
        return ""
    # Strip HTML tags
    cleaned = bleach.clean(value, tags=[], strip=True)
    # Trim whitespace and limit length
    return cleaned.strip()[:max_length]


def validate_project_data(data: dict) -> tuple[Optional[dict], Optional[str]]:
    """Validate project creation/update data.

    Args:
        data: Raw request data.

    Returns:
        Tuple of (validated_data, error_message).
        If valid, error_message is None. If invalid, validated_data is None.
    """
    if not data:
        return None, "Request body is required"

    name = data.get("name", "").strip()
    if not name:
        return None, "Project name is required"

    validated = {
        "name": sanitize_string(name, MAX_NAME_LENGTH),
        "description": sanitize_string(
            data.get("description", ""), MAX_DESCRIPTION_LENGTH
        ),
        "status": data.get("status", "active"),
    }

    # Validate status
    from app.models.project import VALID_STATUSES
    if validated["status"] not in VALID_STATUSES:
        return None, f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}"

    # Validate members
    members = data.get("members", [])
    if isinstance(members, list):
        validated["members"] = [
            sanitize_string(m, MAX_NAME_LENGTH)
            for m in members[:MAX_MEMBERS_COUNT]
            if isinstance(m, str) and m.strip()
        ]
    else:
        validated["members"] = []

    return validated, None


def validate_task_data(data: dict, project_id: str = "") -> tuple[Optional[dict], Optional[str]]:
    """Validate task creation/update data.

    Args:
        data: Raw request data.
        project_id: Parent project ID.

    Returns:
        Tuple of (validated_data, error_message).
    """
    if not data:
        return None, "Request body is required"

    title = data.get("title", "").strip()
    if not title:
        return None, "Task title is required"

    validated = {
        "title": sanitize_string(title, MAX_NAME_LENGTH),
        "description": sanitize_string(
            data.get("description", ""), MAX_DESCRIPTION_LENGTH
        ),
        "status": data.get("status", "todo"),
        "priority": data.get("priority", "medium"),
        "assignee": sanitize_string(data.get("assignee", ""), MAX_NAME_LENGTH),
        "due_date": data.get("due_date"),
    }

    if project_id:
        validated["project_id"] = project_id

    # Validate status
    from app.models.task import VALID_STATUSES
    if validated["status"] not in VALID_STATUSES:
        return None, f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}"

    # Validate priority
    from app.models.task import VALID_PRIORITIES
    if validated["priority"] not in VALID_PRIORITIES:
        return None, f"Invalid priority. Must be one of: {', '.join(VALID_PRIORITIES)}"

    # Validate due_date format if provided
    if validated["due_date"]:
        if not re.match(r"^\d{4}-\d{2}-\d{2}", str(validated["due_date"])):
            return None, "Invalid due_date format. Use YYYY-MM-DD"

    # Validate tags
    tags = data.get("tags", [])
    if isinstance(tags, list):
        validated["tags"] = [
            sanitize_string(t, MAX_TAG_LENGTH)
            for t in tags[:MAX_TAGS_COUNT]
            if isinstance(t, str) and t.strip()
        ]
    else:
        validated["tags"] = []

    return validated, None


def validate_message_data(data: dict, project_id: str = "") -> tuple[Optional[dict], Optional[str]]:
    """Validate message creation data.

    Args:
        data: Raw request data.
        project_id: Parent project ID.

    Returns:
        Tuple of (validated_data, error_message).
    """
    if not data:
        return None, "Request body is required"

    content = data.get("content", "").strip()
    if not content:
        return None, "Message content is required"

    validated = {
        "content": sanitize_string(content, MAX_MESSAGE_LENGTH),
        "sender": sanitize_string(data.get("sender", "Anonymous"), MAX_NAME_LENGTH),
        "msg_type": data.get("msg_type", "chat"),
    }

    if project_id:
        validated["project_id"] = project_id

    # Validate type
    from app.models.message import VALID_TYPES
    if validated["msg_type"] not in VALID_TYPES:
        return None, f"Invalid message type. Must be one of: {', '.join(VALID_TYPES)}"

    return validated, None
