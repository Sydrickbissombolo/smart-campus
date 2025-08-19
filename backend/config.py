import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", 5000))

    # PostgreSQL expected in production
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///smartcampus.db")

    JWT_SECRET = os.getenv("JWT_SECRET", "dev_secret")
    JWT_EXPIRES_MIN = int(os.getenv("JWT_EXPIRES_MIN", 60 * 24))
    JWT_EXPIRES_DELTA = timedelta(minutes=JWT_EXPIRES_MIN)

    CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",")] 

    SMTP_HOST = os.getenv("SMTP_HOST", "localhost")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 1025))
    SMTP_USER = os.getenv("SMTP_USER")
    SMTP_PASS = os.getenv("SMTP_PASS")
    SMTP_FROM = os.getenv("SMTP_FROM", "Smart Campus <noreply@smartcampus.test>")

    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
    MAX_CONTENT_LENGTH_MB = int(os.getenv("MAX_CONTENT_LENGTH_MB", 10))
