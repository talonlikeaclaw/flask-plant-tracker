import os
from dotenv import load_dotenv

# Load environment variables from .env is exists
load_dotenv()


class Config:
    # Secret key for session management and CSRF protection
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key"

    # Database configuration
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL") or "sqlite:///plant_tracker.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
