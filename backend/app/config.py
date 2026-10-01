"""
AgriSmart AI — Configuration
==============================
Environment-based configuration classes.
Loaded by the application factory.
All secrets must be provided via environment variables / .env file.
"""

import os
from datetime import timedelta
from dotenv import load_dotenv
from pathlib import Path
from dotenv import load_dotenv



ENV_FILE = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(ENV_FILE, override=True)
load_dotenv()


class BaseConfig:
    """Base configuration shared by all environments."""

    # Flask
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "agrismart-dev-secret-key-change-in-prod-2026")

    # JWT
    JWT_SECRET_KEY: str = os.environ.get("JWT_SECRET_KEY", "agrismart-jwt-dev-secret-change-in-prod-2026")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        minutes=int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", 43200))
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        days=int(os.environ.get("JWT_REFRESH_TOKEN_EXPIRES_DAYS", 90))
    )
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"

    # Database
    db_url_env = os.environ.get("DATABASE_URL")
    if not db_url_env or "instance/agri_smart_ai.db" in db_url_env:
        instance_dir = Path(__file__).resolve().parents[1] / "instance"
        instance_dir.mkdir(parents=True, exist_ok=True)
        db_path = instance_dir / "agri_smart_ai.db"
        db_url_env = f"sqlite:///{db_path.as_posix()}"
    elif db_url_env.startswith("postgres://"):
        db_url_env = db_url_env.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI: str = db_url_env
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    if db_url_env.startswith("sqlite"):
        SQLALCHEMY_ENGINE_OPTIONS = {}
    else:
        SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_recycle": 280,
            "pool_pre_ping": True,
            "pool_size": 5,
            "max_overflow": 10,
        }

    # File upload
    UPLOAD_FOLDER: str = os.environ.get("UPLOAD_FOLDER", "./uploads")
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH_MB", 10)) * 1024 * 1024
    ALLOWED_UPLOAD_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "tiff", "tif"}

    # CORS & Web Frontend URL
    FRONTEND_URL: str = os.environ.get("FRONTEND_URL", "https://hydroponic-frontend-seven.vercel.app")

    # Email Configuration (Brevo REST API / HTTPS port 443)
    BREVO_API_KEY: str = os.environ.get("BREVO_API_KEY", "")
    MAIL_FROM_EMAIL: str = os.environ.get("MAIL_FROM_EMAIL", "hydroponiccrop@gmail.com")
    MAIL_FROM_NAME: str = os.environ.get("MAIL_FROM_NAME", "AgriSmart AI")
    MAIL_SERVER: str = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT: int = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS: bool = os.environ.get("MAIL_USE_TLS", "true").lower() in ("true", "1", "yes")
    MAIL_USE_SSL: bool = os.environ.get("MAIL_USE_SSL", "false").lower() in ("true", "1", "yes")
    MAIL_USERNAME: str = os.environ.get("MAIL_USERNAME", os.environ.get("SMTP_USER", "hydroponiccrop@gmail.com"))
    MAIL_PASSWORD: str = os.environ.get("MAIL_PASSWORD", os.environ.get("SMTP_PASS", os.environ.get("GMAIL_APP_PASSWORD", "")))
    MAIL_DEFAULT_SENDER: str = os.environ.get("MAIL_DEFAULT_SENDER", "AgriSmart AI <hydroponiccrop@gmail.com>")

    # Weather API (Open-Meteo — no API key needed for free tier)
    WEATHER_API_BASE_URL: str = os.environ.get(
        "WEATHER_API_BASE_URL", "https://api.open-meteo.com"
    )
    WEATHER_CACHE_TTL_SECONDS: int = int(os.environ.get("WEATHER_CACHE_TTL_SECONDS", 3600))

    # Geocoding (OSM Nominatim)
    GEOCODING_API_BASE_URL: str = os.environ.get(
        "GEOCODING_API_BASE_URL", "https://nominatim.openstreetmap.org"
    )
    GEOCODING_USER_AGENT: str = os.environ.get(
        "GEOCODING_USER_AGENT", "AgriSmartAI/1.0 (contact@example.com)"
    )

    # Rate limiting
    RATELIMIT_DEFAULT: str = os.environ.get("RATELIMIT_DEFAULT", "10000 per day;2000 per hour")
    RATELIMIT_STORAGE_URI: str = "memory://"

    # Application version
    APP_VERSION = "1.0.0"
    APP_NAME = "AgriSmart AI"


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = False
    SQLALCHEMY_ECHO = False  # Set True to see SQL statements
    RATELIMIT_ENABLED = False


class TestingConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_ENGINE_OPTIONS = {}  # SQLite doesn't support pool_size/max_overflow
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    WTF_CSRF_ENABLED = False
    RATELIMIT_ENABLED = False


class ProductionConfig(BaseConfig):
    DEBUG = False
    TESTING = False
    # In production, SECRET_KEY and JWT_SECRET_KEY must be set in environment
    # HTTPS is enforced at the reverse proxy / Render platform level


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
