# app/auth/routes.py

from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask import current_app
from app.extensions import bcrypt
from app.auth.forms import RegistrationForm, LoginForm
from app.auth.utils import login_user, logout_user, get_current_user
from datetime import datetime, timezone
from authlib.integrations.flask_client import OAuth

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

oauth = OAuth()
google = None

def init_oauth(app):
    global google
    oauth.init_app(app)
    google = oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'},
    )
# -------------------------------------------------------------------------
# REGISTER
# -------------------------------------------------------------------------
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("main.home"))

    form = RegistrationForm()

    if form.validate_on_submit():
        password_hash = bcrypt.generate_password_hash(
            form.password.data
        ).decode("utf-8")

        user_doc = {
            "name":          form.name.data.strip(),
            "roll_no":       form.roll_no.data.strip().upper(),
            "department":    form.department.data,
            "email":         form.email.data.strip().lower(),
            "phone":         form.phone.data.strip(),
            "password_hash": password_hash,
            "is_verified":   True,
            "created_at":    datetime.now(timezone.utc),
            "last_login":    None,
        }

        try:
            result  = current_app.db.users.insert_one(user_doc)
            new_user = current_app.db.users.find_one({"_id": result.inserted_id})

            if new_user is None:
                flash("Registration failed. Please try again.", "danger")
                return render_template("auth/register.html", form=form)

            login_user(new_user)
            flash(f"Welcome to Campus Lost & Found, {new_user['name']}!", "success")
            return redirect(url_for("main.home"))

        except Exception as e:
            flash("Database error. Please try again in a moment.", "danger")
            current_app.logger.error(f"Register error: {e}")
            return render_template("auth/register.html", form=form)

    return render_template("auth/register.html", form=form)


# -------------------------------------------------------------------------
# LOGIN
# -------------------------------------------------------------------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("main.home"))

    form = LoginForm()

    if form.validate_on_submit():
        try:
            user = current_app.db.users.find_one(
                {"email": form.email.data.strip().lower()}
            )
        except Exception as e:
            flash("Database error. Please try again in a moment.", "danger")
            current_app.logger.error(f"Login DB error: {e}")
            return render_template("auth/login.html", form=form)

        if user and bcrypt.check_password_hash(
            user["password_hash"], form.password.data
        ):
            if not user['email'].endswith('@sastra.ac.in'):
                flash('Only SASTRA University email addresses (@sastra.ac.in) are allowed.', 'danger')
                return render_template("auth/login.html", form=form)
            try:
                current_app.db.users.update_one(
                    {"_id": user["_id"]},
                    {"$set": {"last_login": datetime.now(timezone.utc)}}
                )
            except Exception:
                pass  # Non-critical — don't block login if this fails

            login_user(user)
            flash(f"Welcome back, {user['name']}!", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.home"))

        else:
            flash("Invalid email or password. Please try again.", "danger")

    return render_template("auth/login.html", form=form)


# -------------------------------------------------------------------------
# LOGOUT
# -------------------------------------------------------------------------
@auth_bp.route("/logout")
def logout():
    name = session.get("user_name", "User")
    logout_user()
    flash(f"You have been logged out, {name}. See you soon!", "info")
    return redirect(url_for("auth.login"))

@auth_bp.route('/google/login')
def google_login():
    redirect_uri = url_for('auth.google_callback', _external=True)
    return google.authorize_redirect(redirect_uri)


@auth_bp.route('/google/callback')
def google_callback():
    token = google.authorize_access_token()
    user_info = token.get('userinfo')

    if not user_info:
        flash('Google login failed. Please try again.', 'danger')
        return redirect(url_for('auth.login'))

    email     = user_info['email']
    if not email.endswith('@sastra.ac.in'):
        flash('Only SASTRA University email addresses (@sastra.ac.in) are allowed to register.', 'danger')
        return redirect(url_for('auth.login'))

    name      = user_info.get('name', email.split('@')[0])
    google_id = user_info['sub']
    picture   = user_info.get('picture', '')

    db   = current_app.db
    user = db.users.find_one({'$or': [
        {'google_id': google_id},
        {'email': email}
    ]})

    if user:
        if not user.get('google_id'):
            db.users.update_one(
                {'_id': user['_id']},
                {'$set': {'google_id': google_id, 'picture': picture}}
            )
        login_user(user)
        flash(f'Welcome back, {user["name"]}!', 'success')
        return redirect(url_for('items.explore'))

    else:
        from datetime import datetime, timezone
        new_user = {
            'name':       name,
            'email':      email,
            'google_id':  google_id,
            'picture':    picture,
            'password':   None,
            'roll_no':    '',
            'department': '',
            'phone':      '',
            'is_admin':   False,
            'created_at': datetime.now(timezone.utc),
        }
        result = db.users.insert_one(new_user)
        new_user['_id'] = result.inserted_id
        login_user(new_user)
        flash(f'Welcome to Campus Lost & Found, {name}!', 'success')
        return redirect(url_for('items.explore'))