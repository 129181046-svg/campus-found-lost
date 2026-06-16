# app/notifications/db.py

from datetime import datetime, timezone
from flask import current_app
from bson import ObjectId


def create_notification(user_id, title, message, link, notif_type='info'):
    """Insert a notification document for a user."""
    try:
        current_app.db.notifications.insert_one({
            'user_id':    ObjectId(user_id) if not isinstance(user_id, ObjectId) else user_id,
            'title':      title,
            'message':    message,
            'link':       link,
            'type':       notif_type,   # 'match', 'claim', 'info'
            'is_read':    False,
            'created_at': datetime.now(timezone.utc),
        })
    except Exception as e:
        current_app.logger.error(f"create_notification error: {e}")


def get_user_notifications(user_id, limit=20):
    """Fetch recent notifications for a user, newest first."""
    try:
        return list(current_app.db.notifications.find(
            {'user_id': ObjectId(user_id)}
        ).sort('created_at', -1).limit(limit))
    except Exception:
        return []


def get_unread_count(user_id):
    try:
        return current_app.db.notifications.count_documents({
            'user_id': ObjectId(user_id),
            'is_read': False
        })
    except Exception:
        return 0


def mark_all_read(user_id):
    try:
        current_app.db.notifications.update_many(
            {'user_id': ObjectId(user_id), 'is_read': False},
            {'$set': {'is_read': True}}
        )
    except Exception:
        pass


def mark_one_read(notification_id):
    try:
        current_app.db.notifications.update_one(
            {'_id': ObjectId(notification_id)},
            {'$set': {'is_read': True}}
        )
    except Exception:
        pass