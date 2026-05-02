"""Application configuration management.

Provides environment-specific configuration classes with
secure defaults for production deployments.
"""

import os


class BaseConfig:
    """Base configuration with secure defaults."""

    # Application
    APP_NAME = "TeamFlow"
    SECRET_KEY = os.environ.get("SECRET_KEY", os.urandom(32).hex())
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

    # Google Cloud
    GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "")
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

    # Firestore
    FIRESTORE_DATABASE = os.environ.get("FIRESTORE_DATABASE", "(default)")

    # Rate limiting
    MAX_REQUESTS_PER_MINUTE = int(os.environ.get("MAX_REQUESTS_PER_MINUTE", "60"))


class ProductionConfig(BaseConfig):
    """Production configuration for Cloud Run."""

    DEBUG = False
    TESTING = False
    LOG_LEVEL = "WARNING"


class DevelopmentConfig(BaseConfig):
    """Development configuration with debug features."""

    DEBUG = True
    LOG_LEVEL = "DEBUG"


class TestingConfig(BaseConfig):
    """Testing configuration with mocked services."""

    TESTING = True
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    FIRESTORE_DATABASE = "test"


_configs = {
    "production": ProductionConfig,
    "development": DevelopmentConfig,
    "testing": TestingConfig,
}


def get_config(env_name: str) -> type:
    """Get configuration class by environment name.

    Args:
        env_name: Environment name ('production', 'development', 'testing').

    Returns:
        Configuration class for the specified environment.
    """
    return _configs.get(env_name, ProductionConfig)
