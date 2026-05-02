"""View routes for serving the frontend SPA.

Serves the main index.html template for all non-API routes,
enabling client-side routing.
"""

from flask import Blueprint, render_template

views_bp = Blueprint("views", __name__)


@views_bp.route("/")
def index():
    """Serve the main single-page application.

    Returns:
        Rendered index.html template.
    """
    return render_template("index.html")
