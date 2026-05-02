"""Project CRUD API endpoints.

Provides RESTful endpoints for managing team projects
including creation, listing, updating, and deletion.
"""

import logging

from app.services import firestore_service
from app.utils.security import (error_response, rate_limit, success_response,
                                validate_json_content_type)
from app.utils.validators import validate_project_data
from flask import Blueprint, request

logger = logging.getLogger(__name__)

projects_bp = Blueprint("projects", __name__)


@projects_bp.route("/projects", methods=["GET"])
@rate_limit
def list_projects():
    """List all projects.

    Returns:
        JSON array of project objects.
    """
    try:
        projects = firestore_service.list_projects()
        return success_response(projects)
    except Exception as e:
        logger.error("Error listing projects: %s", str(e))
        return error_response("Failed to list projects", 500)


@projects_bp.route("/projects", methods=["POST"])
@rate_limit
@validate_json_content_type
def create_project():
    """Create a new project.

    Request Body:
        name (str): Project name (required).
        description (str): Project description.
        members (list[str]): Team member names.

    Returns:
        Created project object with generated ID.
    """
    data = request.get_json(silent=True)
    validated, error = validate_project_data(data)
    if error:
        return error_response(error)

    try:
        project = firestore_service.create_project(validated)
        return success_response(project, 201, "Project created successfully")
    except Exception as e:
        logger.error("Error creating project: %s", str(e))
        return error_response("Failed to create project", 500)


@projects_bp.route("/projects/<project_id>", methods=["GET"])
@rate_limit
def get_project(project_id: str):
    """Get a project by ID.

    Args:
        project_id: Firestore document ID.

    Returns:
        Project object or 404 error.
    """
    try:
        project = firestore_service.get_project(project_id)
        if project is None:
            return error_response("Project not found", 404)
        return success_response(project)
    except Exception as e:
        logger.error("Error getting project %s: %s", project_id, str(e))
        return error_response("Failed to get project", 500)


@projects_bp.route("/projects/<project_id>", methods=["PUT"])
@rate_limit
@validate_json_content_type
def update_project(project_id: str):
    """Update a project.

    Args:
        project_id: Firestore document ID.

    Request Body:
        Any project fields to update.

    Returns:
        Updated project object or 404 error.
    """
    data = request.get_json(silent=True)
    validated, error = validate_project_data(data)
    if error:
        return error_response(error)

    try:
        project = firestore_service.update_project(project_id, validated)
        if project is None:
            return error_response("Project not found", 404)
        return success_response(project, message="Project updated successfully")
    except Exception as e:
        logger.error("Error updating project %s: %s", project_id, str(e))
        return error_response("Failed to update project", 500)


@projects_bp.route("/projects/<project_id>", methods=["DELETE"])
@rate_limit
def delete_project(project_id: str):
    """Delete a project and all associated data.

    Args:
        project_id: Firestore document ID.

    Returns:
        Success message or 404 error.
    """
    try:
        deleted = firestore_service.delete_project(project_id)
        if not deleted:
            return error_response("Project not found", 404)
        return success_response(None, message="Project deleted successfully")
    except Exception as e:
        logger.error("Error deleting project %s: %s", project_id, str(e))
        return error_response("Failed to delete project", 500)
