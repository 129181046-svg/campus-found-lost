# app/auth/utils.py

from functools import wraps
from flask import session, redirect, url_for, flash
from flask import current_app
from bson import ObjectId


# -------------------------------------------------------------------------
# GET CURRENT USER
# -------------------------------------------------------------------------
def get_current_user():
    """
    Returns the full user document from MongoDB for the logged-in user.
    Returns None if no user is logged in or the session is invalid.

    Usage in any route:
        user = get_current_user()
        if user:
            print(user['name'])
    """
    user_id = session.get("user_id")
    if not user_id:
        return None
    try:
        # ObjectId converts the stored string ID back to MongoDB's format
        return current_app.db.users.find_one({"_id": ObjectId(user_id)})
    except Exception:
        # If the stored ID is malformed, treat as logged out
        return None


# -------------------------------------------------------------------------
# LOGIN REQUIRED DECORATOR
# -------------------------------------------------------------------------
def login_required(f):
    """
    Protects a route from unauthenticated access.

    Usage:
        @app.route('/items/report')
        @login_required
        def report_item():
            ...

    If the user is not logged in, they are redirected to the login page.
    After login, Flask redirects them back to the page they tried to visit
    via the 'next' parameter.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


# -------------------------------------------------------------------------
# SAVE USER TO SESSION
# -------------------------------------------------------------------------
def login_user(user):
    """
    Saves the user's ID and basic info to the Flask session.
    Called after successful login or registration.

    We store only the ID and name — not the password hash or phone number.
    Sensitive fields are never put in the session cookie.
    """
    session.permanent = True   # Respect PERMANENT_SESSION_LIFETIME (24h)
    session["user_id"]   = str(user["_id"])
    session["user_name"] = user["name"]
    session["user_email"]= user["email"]


# -------------------------------------------------------------------------
# CLEAR SESSION (LOGOUT)
# -------------------------------------------------------------------------
def logout_user():
    """
    Removes all user data from the session.
    Called by the logout route.
    """
    session.pop("user_id",    None)
    session.pop("user_name",  None)
    session.pop("user_email", None)