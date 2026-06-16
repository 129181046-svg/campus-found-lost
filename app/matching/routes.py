# app/matching/routes.py

from flask import Blueprint, render_template, current_app
from bson import ObjectId
from app.auth.utils import login_required, get_current_user

matching_bp = Blueprint('matching', __name__, url_prefix='/matches')


@matching_bp.route('/')
@login_required
def my_matches():
    user = get_current_user()
    uid = ObjectId(user['_id'])
    db = current_app.db

    matches = list(db.matches.find({
        '$or': [{'lost_user_id': uid}, {'found_user_id': uid}]
    }, sort=[('score', -1)]))

    for m in matches:
        m['lost_item']  = db.items.find_one({'_id': m['lost_item_id']})
        m['found_item'] = db.items.find_one({'_id': m['found_item_id']})

    return render_template('matches/matches.html', matches=matches)