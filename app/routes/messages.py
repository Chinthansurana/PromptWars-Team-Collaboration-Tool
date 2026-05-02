"""Message API endpoints.

Provides endpoints for team chat functionality within projects.
"""

import logging

from app.services import firestore_service
from app.utils.security import (error_response, rate_limit, success_response,
                                validate_json_content_type)
from app.utils.validators import validate_message_data
from flask import Blueprint, request

logger = logging.getLogger(__name__)

messages_bp = Blueprint("messages", __name__)


@messages_bp.route("/projects/<project_id>/messages", methods=["GET"])
@rate_limit
def list_messages(project_id: str):
    """Get recent messages for a project.

    Args:
        project_id: Parent project ID.

    Query Params:
        limit (int): Maximum messages to return (default: 50).

    Returns:
        JSON array of message objects in chronological order.
    """
    try:
        # Verify project exists
        project = firestore_service.get_project(project_id)
        if project is None:
            return error_response("Project not found", 404)

        limit = request.args.get("limit", 50, type=int)
        limit = min(limit, 100)  # Cap at 100
        messages = firestore_service.list_messages(project_id, limit)
        return success_response(messages)
    except Exception as e:
        logger.error("Error listing messages for project %s: %s", project_id, str(e))
        return error_response("Failed to list messages", 500)


@messages_bp.route("/projects/<project_id>/messages", methods=["POST"])
@rate_limit
@validate_json_content_type
def create_message(project_id: str):
    """Send a message in a project chat.

    Args:
        project_id: Parent project ID.

    Request Body:
        content (str): Message text (required).
        sender (str): Sender name (default: "Anonymous").

    Returns:
        Created message object.
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
    validated, error = validate_message_data(data, project_id)
    if error:
        return error_response(error)

    try:
        message = firestore_service.create_message(validated)
        return success_response(message, 201, "Message sent")
    except Exception as e:
        logger.error("Error creating message: %s", str(e))
        return error_response("Failed to send message", 500)
