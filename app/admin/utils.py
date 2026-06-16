# app/admin/utils.py

from functools import wraps
from flask import session, redirect, url_for, flash
from flask import current_app
from bson import ObjectId


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            flash('Please log in.', 'warning')
            return redirect(url_for('auth.login'))
        user = current_app.db.users.find_one({'_id': ObjectId(user_id)})
        if not user or not user.get('is_admin'):
            flash('Admin access required.', 'danger')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function