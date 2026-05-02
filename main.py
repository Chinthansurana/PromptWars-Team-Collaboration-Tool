"""TeamFlow — Team Collaboration Tool.

Entry point for the Flask application.
Designed for Google Cloud Run deployment.
"""

import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="[IP_ADDRESS]", port=port, debug=os.environ.get("FLASK_DEBUG", "false").lower() == "true")
