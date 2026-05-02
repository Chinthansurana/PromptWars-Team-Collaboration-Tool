"""User CRUD API endpoints.

Provides RESTful endpoints for managing team users
including creation, listing, updating, and deletion.
"""

import logging

from app.services import firestore_service
from app.utils.security import (error_response, rate_limit, success_response,
                                validate_json_content_type)
from app.utils.validators import validate_user_data
from flask import Blueprint, request

logger = logging.getLogger(__name__)

users_bp = Blueprint("users", __name__)


@users_bp.route("/users", methods=["GET"])
@rate_limit
def list_users():
    """List all users.

    Returns:
        JSON array of user objects.
    """
    try:
        users = firestore_service.list_users()
        return success_response(users)
    except Exception as e:
        logger.error("Error listing users: %s", str(e))
        return error_response("Failed to list users", 500)


@users_bp.route("/users", methods=["POST"])
@rate_limit
@validate_json_content_type
def create_user():
    """Create a new user (onboarding).

    Request Body:
        name (str): User name (required).
        email (str): User email (required, unique).
        role (str): User role (admin, editor, member).

    Returns:
        Created user object with generated ID.
    """
    data = request.get_json(silent=True)
    validated, error = validate_user_data(data)
    if error:
        return error_response(error)

    # Check if email already exists
    existing = firestore_service.get_user_by_email(validated["email"])
    if existing:
        return error_response("User with this email already exists", 409)

    try:
        user = firestore_service.create_user(validated)
        return success_response(user, 201, "User created successfully")
    except Exception as e:
        logger.error("Error creating user: %s", str(e))
        return error_response("Failed to create user", 500)


@users_bp.route("/users/<user_id>", methods=["GET"])
@rate_limit
def get_user(user_id: str):
    """Get a user by ID.

    Args:
        user_id: Firestore document ID.

    Returns:
        User object or 404 error.
    """
    try:
        user = firestore_service.get_user(user_id)
        if user is None:
            return error_response("User not found", 404)
        return success_response(user)
    except Exception as e:
        logger.error("Error getting user %s: %s", user_id, str(e))
        return error_response("Failed to get user", 500)


@users_bp.route("/users/<user_id>", methods=["PUT"])
@rate_limit
@validate_json_content_type
def update_user(user_id: str):
    """Update a user.

    Args:
        user_id: Firestore document ID.

    Request Body:
        Any user fields to update.

    Returns:
        Updated user object or 404 error.
    """
    data = request.get_json(silent=True)
    validated, error = validate_user_data(data, is_update=True)
    if error:
        return error_response(error)

    # If email is being updated, check for uniqueness
    if "email" in validated:
        existing = firestore_service.get_user_by_email(validated["email"])
        if existing and existing.get("id") != user_id:
            return error_response("User with this email already exists", 409)

    try:
        user = firestore_service.update_user(user_id, validated)
        if user is None:
            return error_response("User not found", 404)
        return success_response(user, message="User updated successfully")
    except Exception as e:
        logger.error("Error updating user %s: %s", user_id, str(e))
        return error_response("Failed to update user", 500)


@users_bp.route("/users/<user_id>", methods=["DELETE"])
@rate_limit
def delete_user(user_id: str):
    """Delete a user.

    Args:
        user_id: Firestore document ID.

    Returns:
        Success message or 404 error.
    """
    try:
        deleted = firestore_service.delete_user(user_id)
        if not deleted:
            return error_response("User not found", 404)
        return success_response(None, message="User deleted successfully")
    except Exception as e:
        logger.error("Error deleting user %s: %s", user_id, str(e))
        return error_response("Failed to delete user", 500)
