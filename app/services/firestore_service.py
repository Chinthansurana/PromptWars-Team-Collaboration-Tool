"""Firestore database service.

Provides CRUD operations for projects, tasks, and messages
using Google Cloud Firestore as the backend database.
Implements connection pooling, caching, and efficient queries.
"""

import logging
import time
from datetime import datetime, timezone
from typing import Any, Optional

from google.cloud import firestore

logger = logging.getLogger(__name__)

# Module-level client (lazy-initialized, singleton pattern)
_db: Optional[firestore.Client] = None

# Simple in-memory cache with TTL
_cache: dict[str, tuple[float, Any]] = {}
CACHE_TTL = 30  # seconds


def get_db() -> firestore.Client:
    """Get or create the Firestore client (singleton).

    Uses connection pooling via the google-cloud-firestore SDK.

    Returns:
        Firestore client instance.
    """
    global _db
    if _db is None:
        _db = firestore.Client()
        logger.info("Firestore client initialized with connection pooling")
    return _db


def set_db(client: Any) -> None:
    """Override the Firestore client (used for testing).

    Args:
        client: Mock or test Firestore client.
    """
    global _db
    _db = client


def _cache_get(key: str) -> Optional[Any]:
    """Get a value from the in-memory cache if not expired.

    Args:
        key: Cache key.

    Returns:
        Cached value or None if expired/missing.
    """
    if key in _cache:
        timestamp, value = _cache[key]
        if time.time() - timestamp < CACHE_TTL:
            return value
        del _cache[key]
    return None


def _cache_set(key: str, value: Any) -> None:
    """Set a value in the in-memory cache.

    Args:
        key: Cache key.
        value: Value to cache.
    """
    _cache[key] = (time.time(), value)


def _cache_invalidate(prefix: str) -> None:
    """Invalidate all cache entries matching a prefix.

    Args:
        prefix: Key prefix to match.
    """
    keys_to_delete = [k for k in _cache if k.startswith(prefix)]
    for k in keys_to_delete:
        del _cache[k]


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------

def list_projects() -> list[dict]:
    """List all projects ordered by creation date.

    Returns:
        List of project dictionaries sorted newest first.
    """
    cached = _cache_get("projects:list")
    if cached is not None:
        return cached

    db = get_db()
    docs = db.collection("projects").order_by(
        "created_at", direction=firestore.Query.DESCENDING
    ).stream()
    results = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        results.append(data)
    _cache_set("projects:list", results)
    return results


def get_project(project_id: str) -> Optional[dict]:
    """Get a single project by ID.

    Args:
        project_id: Firestore document ID.

    Returns:
        Project dictionary or None if not found.
    """
    cached = _cache_get(f"projects:{project_id}")
    if cached is not None:
        return cached

    db = get_db()
    doc = db.collection("projects").document(project_id).get()
    if doc.exists:
        data = doc.to_dict()
        data["id"] = doc.id
        _cache_set(f"projects:{project_id}", data)
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
    _cache_invalidate("projects:")
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
    _cache_invalidate("projects:")
    logger.info("Updated project: %s", project_id)
    return updated


def delete_project(project_id: str) -> bool:
    """Delete a project and all its tasks and messages.

    Uses batch operations for efficient cascading deletes.

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

    # Batch delete associated tasks and messages for efficiency
    batch = db.batch()
    tasks = db.collection("tasks").where(
        filter=firestore.FieldFilter("project_id", "==", project_id)
    ).stream()
    for task in tasks:
        batch.delete(task.reference)

    messages = db.collection("messages").where(
        filter=firestore.FieldFilter("project_id", "==", project_id)
    ).stream()
    for msg in messages:
        batch.delete(msg.reference)

    batch.delete(doc_ref)
    batch.commit()
    _cache_invalidate("projects:")
    _cache_invalidate("tasks:")
    _cache_invalidate("messages:")
    logger.info("Deleted project and associated data: %s", project_id)
    return True


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------

def list_tasks(project_id: str) -> list[dict]:
    """List all tasks for a project.

    Sorted by created_at in Python to avoid requiring composite indexes.

    Args:
        project_id: Parent project ID.

    Returns:
        List of task dictionaries sorted newest first.
    """
    cached = _cache_get(f"tasks:{project_id}")
    if cached is not None:
        return cached

    db = get_db()
    docs = db.collection("tasks").where(
        filter=firestore.FieldFilter("project_id", "==", project_id)
    ).stream()
    results = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        results.append(data)
    # Sort in Python to avoid composite index requirement
    results.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    _cache_set(f"tasks:{project_id}", results)
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
    _cache_invalidate("tasks:")
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
    _cache_invalidate("tasks:")
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
    _cache_invalidate("tasks:")
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
        List of message dictionaries in chronological order.
    """
    cached = _cache_get(f"messages:{project_id}:{limit}")
    if cached is not None:
        return cached

    db = get_db()
    docs = db.collection("messages").where(
        filter=firestore.FieldFilter("project_id", "==", project_id)
    ).stream()
    results = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        results.append(data)
    # Sort by timestamp in Python, take latest N
    results.sort(key=lambda x: x.get("timestamp", ""))
    results = results[-limit:]
    _cache_set(f"messages:{project_id}:{limit}", results)
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
    _cache_invalidate("messages:")
    return data
