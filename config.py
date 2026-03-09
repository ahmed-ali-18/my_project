import os
from datetime import timedelta
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Uploads
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

    # AI model path
    MODEL_PATH = os.path.join(BASE_DIR, "ai", "model.joblib")

    # Complaint delay threshold in minutes (demo: 2 minutes)
    _delay_min = os.environ.get("DELAY_THRESHOLD_MINUTES", "2")
    DELAY_THRESHOLD_MINUTES = int(_delay_min) if str(_delay_min).isdigit() else 2

    REMEMBER_COOKIE_DURATION = timedelta(days=7)


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(BASE_DIR, "dev.db"),
    )


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

