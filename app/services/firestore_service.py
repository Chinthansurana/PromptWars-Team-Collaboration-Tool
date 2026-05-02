"""Firestore database service.

Provides CRUD operations for projects, tasks, and messages
using Google Cloud Firestore as the backend database.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from google.cloud import firestore

logger = logging.getLogger(__name__)

# Module-level client (lazy-initialized)
_db: Optional[firestore.Client] = None


def get_db() -> firestore.Client:
    """Get or create the Firestore client (singleton).

    Returns:
        Firestore client instance.
    """
    global _db
    if _db is None:
        _db = firestore.Client()
        logger.info("Firestore client initialized")
    return _db


def set_db(client) -> None:
    """Override the Firestore client (used for testing).

    Args:
        client: Mock or test Firestore client.
    """
    global _db
    _db = client


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------

def list_projects() -> list[dict]:
    """List all projects ordered by creation date.

    Returns:
        List of project dictionaries.
    """
    db = get_db()
    docs = db.collection("projects").order_by(
        "created_at", direction=firestore.Query.DESCENDING
    ).stream()
    results = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        results.append(data)
    return results


def get_project(project_id: str) -> Optional[dict]:
    """Get a single project by ID.

    Args:
        project_id: Firestore document ID.

    Returns:
        Project dictionary or None if not found.
    """
    db = get_db()
    doc = db.collection("projects").document(project_id).get()
    if doc.exists:
        data = doc.to_dict()
        data["id"] = doc.id
        return data
    return None


def create_project(data: dict) -> dict:
    """Create a new project.

    Args:
        data: Project data dictionary.

    Returns:
        Created project dictionary with generated ID.
    """
    db = get_db()
    now = datetime.now(timezone.utc).isoformat()
    data["created_at"] = now
    data["updated_at"] = now
    doc_ref = db.collection("projects").document()
    doc_ref.set(data)
    data["id"] = doc_ref.id
    logger.info("Created project: %s", doc_ref.id)
    return data


def update_project(project_id: str, data: dict) -> Optional[dict]:
    """Update an existing project.

    Args:
        project_id: Firestore document ID.
        data: Fields to update.

    Returns:
        Updated project dictionary or None if not found.
    """
    db = get_db()
    doc_ref = db.collection("projects").document(project_id)
    doc = doc_ref.get()
    if not doc.exists:
        return None
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    doc_ref.update(data)
    updated = doc_ref.get().to_dict()
    updated["id"] = project_id
    logger.info("Updated project: %s", project_id)
    return updated


def delete_project(project_id: str) -> bool:
    """Delete a project and all its tasks and messages.

    Args:
        project_id: Firestore document ID.

    Returns:
        True if deleted, False if not found.
    """
    db = get_db()
    doc_ref = db.collection("projects").document(project_id)
    doc = doc_ref.get()
    if not doc.exists:
        return False

    # Delete associated tasks
    tasks = db.collection("tasks").where("project_id", "==", project_id).stream()
    for task in tasks:
        task.reference.delete()

    # Delete associated messages
    messages = db.collection("messages").where("project_id", "==", project_id).stream()
    for msg in messages:
        msg.reference.delete()

    doc_ref.delete()
    logger.info("Deleted project and associated data: %s", project_id)
    return True


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------

def list_tasks(project_id: str) -> list[dict]:
    """List all tasks for a project.

    Args:
        project_id: Parent project ID.

    Returns:
        List of task dictionaries.
    """
    db = get_db()
    docs = db.collection("tasks").where(
        "project_id", "==", project_id
    ).order_by("created_at", direction=firestore.Query.DESCENDING).stream()
    results = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        results.append(data)
    return results


def get_task(task_id: str) -> Optional[dict]:
    """Get a single task by ID.

    Args:
        task_id: Firestore document ID.

    Returns:
        Task dictionary or None if not found.
    """
    db = get_db()
    doc = db.collection("tasks").document(task_id).get()
    if doc.exists:
        data = doc.to_dict()
        data["id"] = doc.id
        return data
    return None


def create_task(data: dict) -> dict:
    """Create a new task.

    Args:
        data: Task data dictionary.

    Returns:
        Created task dictionary with generated ID.
    """
    db = get_db()
    now = datetime.now(timezone.utc).isoformat()
    data["created_at"] = now
    data["updated_at"] = now
    doc_ref = db.collection("tasks").document()
    doc_ref.set(data)
    data["id"] = doc_ref.id
    logger.info("Created task: %s", doc_ref.id)
    return data


def update_task(task_id: str, data: dict) -> Optional[dict]:
    """Update an existing task.

    Args:
        task_id: Firestore document ID.
        data: Fields to update.

    Returns:
        Updated task dictionary or None if not found.
    """
    db = get_db()
    doc_ref = db.collection("tasks").document(task_id)
    doc = doc_ref.get()
    if not doc.exists:
        return None
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    doc_ref.update(data)
    updated = doc_ref.get().to_dict()
    updated["id"] = task_id
    logger.info("Updated task: %s", task_id)
    return updated


def delete_task(task_id: str) -> bool:
    """Delete a task.

    Args:
        task_id: Firestore document ID.

    Returns:
        True if deleted, False if not found.
    """
    db = get_db()
    doc_ref = db.collection("tasks").document(task_id)
    doc = doc_ref.get()
    if not doc.exists:
        return False
    doc_ref.delete()
    logger.info("Deleted task: %s", task_id)
    return True


# ---------------------------------------------------------------------------
# Messages
# ---------------------------------------------------------------------------

def list_messages(project_id: str, limit: int = 50) -> list[dict]:
    """List recent messages for a project.

    Args:
        project_id: Parent project ID.
        limit: Maximum number of messages to return.

    Returns:
        List of message dictionaries, oldest first.
    """
    db = get_db()
    docs = db.collection("messages").where(
        "project_id", "==", project_id
    ).order_by("timestamp", direction=firestore.Query.DESCENDING).limit(limit).stream()
    results = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        results.append(data)
    # Return in chronological order
    results.reverse()
    return results


def create_message(data: dict) -> dict:
    """Create a new message.

    Args:
        data: Message data dictionary.

    Returns:
        Created message dictionary with generated ID.
    """
    db = get_db()
    if "timestamp" not in data:
        data["timestamp"] = datetime.now(timezone.utc).isoformat()
    doc_ref = db.collection("messages").document()
    doc_ref.set(data)
    data["id"] = doc_ref.id
    return data
