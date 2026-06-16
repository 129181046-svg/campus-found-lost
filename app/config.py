# app/config.py

import os
from dotenv import load_dotenv

# Load the .env file into the system environment.
# This must happen before any os.getenv() calls below.
load_dotenv()


class Config:
    # -------------------------------------------------------------------------
    # CORE FLASK SETTINGS
    # -------------------------------------------------------------------------

    # SECRET_KEY signs Flask session cookies cryptographically.
    # If this is weak or missing, sessions can be forged by attackers.
    # os.getenv() reads from .env — never hardcode this value here.
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-before-deploy")
    WTF_CSRF_ENABLED    = True
    # Disable Flask-SQLAlchemy event system. We don't use SQLAlchemy,
    # but this silences a warning if the setting is not explicitly set.
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # -------------------------------------------------------------------------
    # MONGODB SETTINGS
    # -------------------------------------------------------------------------

    # Full MongoDB Atlas connection string from .env
    MONGO_URI = os.getenv("MONGO_URI")

    # -------------------------------------------------------------------------
    # SESSION SETTINGS
    # -------------------------------------------------------------------------

    # Sessions expire after 24 hours of inactivity.
    # Without this, a logged-in session lives forever.
    PERMANENT_SESSION_LIFETIME = 86400  # seconds (60 * 60 * 24)

    # -------------------------------------------------------------------------
    # FILE UPLOAD SETTINGS
    # -------------------------------------------------------------------------

    # Maximum upload size: 5 MB. Cloudinary will handle the actual storage,
    # but Flask still receives the file in memory first — cap it here.
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB in bytes

    # Only these file extensions are accepted for item photos.
    # Validated in the items module — defined here so it's easy to change.
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

    # -------------------------------------------------------------------------
    # CLOUDINARY SETTINGS
    # -------------------------------------------------------------------------

    CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY    = os.getenv("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

    # -------------------------------------------------------------------------
    # EMAIL (GMAIL SMTP) SETTINGS
    # -------------------------------------------------------------------------

    MAIL_SERVER   = "smtp.gmail.com"
    MAIL_PORT     = 587
    MAIL_USE_TLS  = True
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")  # your Gmail address
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")  # Gmail App Password (not your login password)
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_USERNAME")

    TWILIO_ACCOUNT_SID    = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN     = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_WHATSAPP_FROM  = os.getenv('TWILIO_WHATSAPP_FROM')
    
    
class DevelopmentConfig(Config):
    # -------------------------------------------------------------------------
    # DEVELOPMENT OVERRIDES
    # -------------------------------------------------------------------------

    # Debug mode: Flask shows a detailed error page in the browser
    # and auto-reloads when you save a file.
    # NEVER set this True in production — it exposes your source code.
    DEBUG = True

    # Makes MongoDB queries print to the terminal during development.
    # Helps you see exactly what queries are running.
    MONGO_ECHO = True


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE   = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
     # Production uses SRV URI with proper certificates via certifi
    MONGO_URI = os.getenv("MONGO_URI_PROD") or os.getenv("MONGO_URI")

config_map = {
    "development": DevelopmentConfig,
    "production":  ProductionConfig,
}