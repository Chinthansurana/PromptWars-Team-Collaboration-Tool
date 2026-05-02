"""AI feature API endpoints.

Provides AI-powered endpoints for task summarization,
smart suggestions, meeting notes generation, and
team sentiment analysis using Google Gemini.
"""

import logging

from flask import Blueprint, request

from app.services import firestore_service, gemini_service
from app.utils.security import (
    error_response,
    rate_limit,
    success_response,
    validate_json_content_type,
)

logger = logging.getLogger(__name__)

ai_bp = Blueprint("ai", __name__)


@ai_bp.route("/summarize", methods=["POST"])
@rate_limit
@validate_json_content_type
def summarize_tasks():
    """Generate an AI summary of all tasks in a project.

    Request Body:
        project_id (str): Project ID to summarize (required).

    Returns:
        AI-generated markdown summary.
    """
    data = request.get_json(silent=True)
    if not data or "project_id" not in data:
        return error_response("project_id is required")

    project_id = data["project_id"]

    try:
        project = firestore_service.get_project(project_id)
        if project is None:
            return error_response("Project not found", 404)

        tasks = firestore_service.list_tasks(project_id)
        summary = gemini_service.summarize_tasks(tasks, project.get("name", ""))
        return success_response({"summary": summary})
    except Exception as e:
        logger.error("Error summarizing tasks: %s", str(e))
        return error_response("Failed to generate summary", 500)


@ai_bp.route("/suggest-tasks", methods=["POST"])
@rate_limit
@validate_json_content_type
def suggest_tasks():
    """Generate AI-suggested tasks for a project.

    Request Body:
        project_id (str): Project ID (required).

    Returns:
        AI-generated task suggestions as JSON.
    """
    data = request.get_json(silent=True)
    if not data or "project_id" not in data:
        return error_response("project_id is required")

    project_id = data["project_id"]

    try:
        project = firestore_service.get_project(project_id)
        if project is None:
            return error_response("Project not found", 404)

        suggestions = gemini_service.suggest_tasks(
            project.get("name", ""),
            project.get("description", ""),
        )
        return success_response({"suggestions": suggestions})
    except Exception as e:
        logger.error("Error suggesting tasks: %s", str(e))
        return error_response("Failed to generate suggestions", 500)


@ai_bp.route("/meeting-notes", methods=["POST"])
@rate_limit
@validate_json_content_type
def meeting_notes():
    """Generate meeting notes from recent project messages.

    Request Body:
        project_id (str): Project ID (required).

    Returns:
        AI-generated markdown meeting notes.
    """
    data = request.get_json(silent=True)
    if not data or "project_id" not in data:
        return error_response("project_id is required")

    project_id = data["project_id"]

    try:
        project = firestore_service.get_project(project_id)
        if project is None:
            return error_response("Project not found", 404)

        messages = firestore_service.list_messages(project_id, limit=50)
        notes = gemini_service.generate_meeting_notes(
            messages, project.get("name", "")
        )
        return success_response({"notes": notes})
    except Exception as e:
        logger.error("Error generating meeting notes: %s", str(e))
        return error_response("Failed to generate meeting notes", 500)


@ai_bp.route("/sentiment", methods=["POST"])
@rate_limit
@validate_json_content_type
def analyze_sentiment():
    """Analyze team sentiment from recent project messages.

    Request Body:
        project_id (str): Project ID (required).

    Returns:
        AI-generated sentiment analysis.
    """
    data = request.get_json(silent=True)
    if not data or "project_id" not in data:
        return error_response("project_id is required")

    project_id = data["project_id"]

    try:
        project = firestore_service.get_project(project_id)
        if project is None:
            return error_response("Project not found", 404)

        messages = firestore_service.list_messages(project_id, limit=50)
        analysis = gemini_service.analyze_sentiment(messages)
        return success_response({"analysis": analysis})
    except Exception as e:
        logger.error("Error analyzing sentiment: %s", str(e))
        return error_response("Failed to analyze sentiment", 500)
