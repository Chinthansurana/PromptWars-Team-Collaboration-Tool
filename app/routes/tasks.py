"""Task CRUD API endpoints.

Provides RESTful endpoints for managing tasks within projects
including Kanban board operations and status updates.
"""

import logging

from app.services import firestore_service
from app.utils.security import (error_response, rate_limit, success_response,
                                validate_json_content_type)
from app.utils.validators import validate_task_data
from flask import Blueprint, request

logger = logging.getLogger(__name__)

tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.route("/projects/<project_id>/tasks", methods=["GET"])
@rate_limit
def list_tasks(project_id: str):
    """List all tasks for a project.

    Args:
        project_id: Parent project ID.

    Returns:
        JSON array of task objects.
    """
    try:
        # Verify project exists
        project = firestore_service.get_project(project_id)
        if project is None:
            return error_response("Project not found", 404)

        tasks = firestore_service.list_tasks(project_id)
        return success_response(tasks)
    except Exception as e:
        logger.error("Error listing tasks for project %s: %s", project_id, str(e))
        return error_response("Failed to list tasks", 500)


@tasks_bp.route("/projects/<project_id>/tasks", methods=["POST"])
@rate_limit
@validate_json_content_type
def create_task(project_id: str):
    """Create a new task in a project.

    Args:
        project_id: Parent project ID.

    Request Body:
        title (str): Task title (required).
        description (str): Task description.
        priority (str): Priority level.
        assignee (str): Assigned team member.
        due_date (str): Due date in YYYY-MM-DD format.
        tags (list[str]): Task tags.

    Returns:
        Created task object with generated ID.
    """
    # Verify project exists
    try:
        project = firestore_service.get_project(project_id)
        if project is None:
            return error_response("Project not found", 404)
    except Exception as e:
        logger.error("Error verifying project %s: %s", project_id, str(e))
        return error_response("Failed to verify project", 500)

    data = request.get_json(silent=True)
    validated, error = validate_task_data(data, project_id)
    if error:
        return error_response(error)

    try:
        task = firestore_service.create_task(validated)
        return success_response(task, 201, "Task created successfully")
    except Exception as e:
        logger.error("Error creating task: %s", str(e))
        return error_response("Failed to create task", 500)


@tasks_bp.route("/tasks/<task_id>", methods=["GET"])
@rate_limit
def get_task(task_id: str):
    """Get a task by ID.

    Args:
        task_id: Firestore document ID.

    Returns:
        Task object or 404 error.
    """
    try:
        task = firestore_service.get_task(task_id)
        if task is None:
            return error_response("Task not found", 404)
        return success_response(task)
    except Exception as e:
        logger.error("Error getting task %s: %s", task_id, str(e))
        return error_response("Failed to get task", 500)


@tasks_bp.route("/tasks/<task_id>", methods=["PUT"])
@rate_limit
@validate_json_content_type
def update_task(task_id: str):
    """Update a task.

    Args:
        task_id: Firestore document ID.

    Request Body:
        Any task fields to update.

    Returns:
        Updated task object or 404 error.
    """
    data = request.get_json(silent=True)

    # For updates, title is optional (may only update status)
    if data and "title" not in data:
        # Get existing task to preserve title
        existing = firestore_service.get_task(task_id)
        if existing:
            data["title"] = existing.get("title", "Untitled")

    validated, error = validate_task_data(data)
    if error:
        return error_response(error)

    try:
        task = firestore_service.update_task(task_id, validated)
        if task is None:
            return error_response("Task not found", 404)
        return success_response(task, message="Task updated successfully")
    except Exception as e:
        logger.error("Error updating task %s: %s", task_id, str(e))
        return error_response("Failed to update task", 500)


@tasks_bp.route("/tasks/<task_id>/status", methods=["PATCH"])
@rate_limit
@validate_json_content_type
def update_task_status(task_id: str):
    """Quick status update for a task (e.g., drag-and-drop on Kanban board).

    Args:
        task_id: Firestore document ID.

    Request Body:
        status (str): New task status (required).

    Returns:
        Updated task object or error.
    """
    data = request.get_json(silent=True)
    if not data or "status" not in data:
        return error_response("Status field is required")

    from app.models.task import VALID_STATUSES
    status = data["status"]
    if status not in VALID_STATUSES:
        return error_response(f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}")

    try:
        task = firestore_service.update_task(task_id, {"status": status})
        if task is None:
            return error_response("Task not found", 404)
        return success_response(task, message="Task status updated")
    except Exception as e:
        logger.error("Error updating task status %s: %s", task_id, str(e))
        return error_response("Failed to update task status", 500)


@tasks_bp.route("/tasks/<task_id>", methods=["DELETE"])
@rate_limit
def delete_task(task_id: str):
    """Delete a task.

    Args:
        task_id: Firestore document ID.

    Returns:
        Success message or 404 error.
    """
    try:
        deleted = firestore_service.delete_task(task_id)
        if not deleted:
            return error_response("Task not found", 404)
        return success_response(None, message="Task deleted successfully")
    except Exception as e:
        logger.error("Error deleting task %s: %s", task_id, str(e))
        return error_response("Failed to delete task", 500)
