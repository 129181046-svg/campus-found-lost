# app/notifications/routes.py

from flask import Blueprint, render_template, redirect, url_for
from app.auth.utils import login_required, get_current_user
from .db import get_user_notifications, mark_all_read, mark_one_read

notifications_bp = Blueprint('notifications', __name__, url_prefix='/notifications')


@notifications_bp.route('/')
@login_required
def list_notifications():
    user = get_current_user()
    notifs = get_user_notifications(user['_id'])
    mark_all_read(user['_id'])
    return render_template('notifications/list.html', notifications=notifs)


@notifications_bp.route('/<notif_id>/open')
@login_required
def open_notification(notif_id):
    mark_one_read(notif_id)
    notifs = get_user_notifications(get_current_user()['_id'], limit=1)
    # Redirect handled by template links directly; this is a fallback
    return redirect(url_for('notifications.list_notifications'))