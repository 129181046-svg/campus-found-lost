# app/__init__.py

import os
import certifi
from flask import Flask, app, render_template
from pymongo import MongoClient
from flask_wtf.csrf import CSRFProtect, generate_csrf

from app.auth.routes import init_oauth
from .config import config_map
from .extensions import bcrypt, talisman, mail
from .items.utils import configure_cloudinary
mongo_client = None
db = None


def create_app():
    global mongo_client, db

    app = Flask(__name__)
    @app.context_processor
    def inject_notification_count():
        from flask import session
        from bson import ObjectId
        if session.get('user_id'):
            try:
                count = app.db.notifications.count_documents({
                    'user_id': ObjectId(session['user_id']),
                    'is_read': False
                })
                return dict(unread_count=count)
            except Exception:
                return dict(unread_count=0)
        return dict(unread_count=0)    

    
    # ── 1. LOAD CONFIG ───────────────────────────────────────────────
    env = os.getenv("FLASK_ENV", "development")
    app.config.from_object(config_map[env])

    # ── 2. CONNECT TO MONGODB ────────────────────────────────────────
    import certifi
    from urllib.parse import urlparse, urlencode, urlunparse, parse_qs

    uri = app.config["MONGO_URI"]

    # In production, use certifi certificates
    # In development, tlsInsecure=true is already in the URI
    if os.getenv("FLASK_ENV") == "production":
        mongo_client = MongoClient(
            uri,
            tlsCAFile=certifi.where()
        )
    else:
        mongo_client = MongoClient(uri)

    db = mongo_client.get_default_database()
    app.db = db
    # ── 3. INIT EXTENSIONS ───────────────────────────────────────────
    bcrypt.init_app(app)
    mail.init_app(app)
    CSRFProtect(app)

    # ── SECURITY HEADERS ─────────────────────────────────────────────
    is_production = os.getenv("FLASK_ENV") == "production"

    talisman.init_app(
        app,
        force_https=is_production,   # Redirect HTTP to HTTPS on Render
        strict_transport_security=is_production,
        session_cookie_secure=is_production,
        content_security_policy={
            "default-src": "'self'",
            "script-src": [
                "'self'",
                "cdn.jsdelivr.net",
                "'unsafe-inline'",   # Needed for Bootstrap JS
            ],
            "style-src": [
                "'self'",
                "cdn.jsdelivr.net",
                "'unsafe-inline'",   # Needed for Bootstrap CSS
            ],
            "img-src": [
                "'self'",
                "res.cloudinary.com",  # Cloudinary images
                "data:",
            ],
            "font-src": [
                "'self'",
                "cdn.jsdelivr.net",
            ],
        },
        referrer_policy="strict-origin-when-cross-origin",
        feature_policy={
            "geolocation": "'none'",
            "microphone":  "'none'",
            "camera":      "'none'",
        },
    )
    
    # ── 4. INJECT csrf_token() INTO ALL TEMPLATES ───────────────────
    @app.context_processor
    def inject_csrf():
        return dict(csrf_token=generate_csrf)

    # ── 5. CONFIGURE CLOUDINARY ──────────────────────────────────────
    with app.app_context():
        configure_cloudinary()

    # ── 6. REGISTER BLUEPRINTS ───────────────────────────────────────
    from .main.routes import main_bp
    app.register_blueprint(main_bp)

    from .auth.routes import auth_bp
    app.register_blueprint(auth_bp)

    from .items.routes import items_bp
    app.register_blueprint(items_bp)

    from .matching.routes import matching_bp
    app.register_blueprint(matching_bp)
    
    from .claims.routes import claims_bp
    app.register_blueprint(claims_bp)
    
    from .search.routes import search_bp
    app.register_blueprint(search_bp)
    
    from .admin.routes import admin_bp
    app.register_blueprint(admin_bp)
    
    from .notifications.routes import notifications_bp
    app.register_blueprint(notifications_bp)
    
    from .auth.routes import init_oauth
    init_oauth(app)

    # ── 7. HEALTH CHECK ──────────────────────────────────────────────
    @app.route("/ping")
    def ping():
        try:
            app.db.command("ping")
            return {"status": "ok", "db": "connected"}, 200
        except Exception as e:
            return {"status": "error", "db": str(e)}, 500
    # ── ERROR HANDLERS ───────────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500



    return app

    