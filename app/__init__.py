"""TeamFlow application factory.

Creates and configures the Flask application with all blueprints,
services, and security middleware.
"""

import logging
import os

from flask import Flask

from app.config import get_config


def create_app(config_name: str | None = None) -> Flask:
    """Create and configure the Flask application.

    Args:
        config_name: Configuration environment name. Defaults to
                     FLASK_ENV environment variable or 'production'.

    Returns:
        Configured Flask application instance.
    """
    app = Flask(
        __name__,
        static_folder="../static",
        template_folder="../templates",
    )

    # Load configuration
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "production")
    app.config.from_object(get_config(config_name))

    # Configure structured logging for Cloud Logging
    _configure_logging(app)

    # Register security headers middleware
    _register_security_headers(app)

    # Register blueprints
    _register_blueprints(app)

    # Health check endpoint
    @app.route("/health")
    def health():
        """Health check endpoint for Cloud Run."""
        return {"status": "healthy", "service": "teamflow"}, 200

    app.logger.info("TeamFlow application initialized (env=%s)", config_name)
    return app


def _configure_logging(app: Flask) -> None:
    """Configure structured JSON logging for Google Cloud Logging."""
    log_level = app.config.get("LOG_LEVEL", "INFO")
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def _register_security_headers(app: Flask) -> None:
    """Add security headers to all responses."""

    @app.after_request
    def add_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self'"
        )
        response.headers["Content-Security-Policy"] = csp
        return response


def _register_blueprints(app: Flask) -> None:
    """Register all API blueprints."""
    from app.routes.projects import projects_bp
    from app.routes.tasks import tasks_bp
    from app.routes.messages import messages_bp
    from app.routes.ai import ai_bp
    from app.routes.views import views_bp

    app.register_blueprint(projects_bp, url_prefix="/api")
    app.register_blueprint(tasks_bp, url_prefix="/api")
    app.register_blueprint(messages_bp, url_prefix="/api")
    app.register_blueprint(ai_bp, url_prefix="/api/ai")
    app.register_blueprint(views_bp)
