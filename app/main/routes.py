# app/main/routes.py

from flask import Blueprint, render_template, current_app
from app.auth.utils import get_current_user

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def home():
    db = current_app.db
    stats = {
        'total_items':   db.items.count_documents({}),
        'total_users':   db.users.count_documents({}),
        'returned_items':db.items.count_documents({'status': 'returned'}),
    }
    return render_template('main/home.html', stats=stats)