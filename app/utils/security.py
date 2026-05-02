"""Security utilities.

Provides security-related functions including rate limiting,
request validation, and secure response helpers.
"""

import functools
import logging
import time
from collections import defaultdict

from flask import jsonify, request

logger = logging.getLogger(__name__)

# Simple in-memory rate limiter (per-IP)
_request_counts: dict[str, list[float]] = defaultdict(list)
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX = 60  # requests per window


def rate_limit(func):
    """Rate limiting decorator for API endpoints.

    Limits requests to RATE_LIMIT_MAX per RATE_LIMIT_WINDOW seconds per IP.

    Args:
        func: The route function to protect.

    Returns:
        Wrapped function with rate limiting.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        client_ip = request.remote_addr or "unknown"
        now = time.time()

        # Clean old entries
        _request_counts[client_ip] = [
            t for t in _request_counts[client_ip]
            if now - t < RATE_LIMIT_WINDOW
        ]

        if len(_request_counts[client_ip]) >= RATE_LIMIT_MAX:
            logger.warning("Rate limit exceeded for IP: %s", client_ip)
            return jsonify({
                "error": "Rate limit exceeded. Please try again later.",
                "retry_after": RATE_LIMIT_WINDOW,
            }), 429

        _request_counts[client_ip].append(now)
        return func(*args, **kwargs)

    return wrapper


def validate_json_content_type(func):
    """Validate that POST/PUT/PATCH requests have JSON content type.

    Args:
        func: The route function to protect.

    Returns:
        Wrapped function with content-type validation.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if request.method in ("POST", "PUT", "PATCH"):
            if not request.is_json:
                return jsonify({
                    "error": "Content-Type must be application/json"
                }), 415
        return func(*args, **kwargs)

    return wrapper


def error_response(message: str, status_code: int = 400) -> tuple:
    """Create a standardized error response.

    Args:
        message: Error message.
        status_code: HTTP status code.

    Returns:
        Tuple of (response, status_code).
    """
    return jsonify({"error": message}), status_code


def success_response(data, status_code: int = 200, message: str = "") -> tuple:
    """Create a standardized success response.

    Args:
        data: Response data.
        status_code: HTTP status code.
        message: Optional success message.

    Returns:
        Tuple of (response, status_code).
    """
    response = {"data": data}
    if message:
        response["message"] = message
    return jsonify(response), status_code
