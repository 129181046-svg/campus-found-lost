# app/auth/routes.py

from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask import current_app
from app.extensions import bcrypt
from app.auth.forms import RegistrationForm, LoginForm
from app.auth.utils import login_user, logout_user, get_current_user
from datetime import datetime, timezone

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


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