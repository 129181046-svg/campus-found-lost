from rapidfuzz import fuzz
from datetime import datetime, timezone
from bson import ObjectId
from flask import current_app


SCORE_THRESHOLD = 55


def _date_score(d1, d2):
    if not d1 or not d2:
        return 0
    diff = abs((d1 - d2).days)
    if diff == 0:  return 100
    if diff <= 1:  return 85
    if diff <= 3:  return 65
    if diff <= 7:  return 45
    if diff <= 14: return 25
    return 0


def _compute_score(lost, found):
    name_score     = fuzz.token_sort_ratio(lost['item_name'], found['item_name'])
    location_score = fuzz.token_sort_ratio(lost['location'],  found['location'])
    category_score = 100 if lost['category'] == found['category'] else 0
    date_score     = _date_score(lost.get('date_occurred'), found.get('date_occurred'))
    return round(0.60 * name_score + 0.20 * location_score +
                 0.10 * category_score + 0.10 * date_score, 1)


def run_matching(new_item_id: str):
    db = current_app.db
    new_item = db.items.find_one({'_id': ObjectId(new_item_id)})
    if not new_item:
        return

    opposite_type = 'found' if new_item['item_type'] == 'lost' else 'lost'
    candidates = db.items.find({
        'item_type': opposite_type,
        'status': 'open',
        '_id': {'$ne': ObjectId(new_item_id)},
    })

    for candidate in candidates:
        lost, found = (new_item, candidate) if new_item['item_type'] == 'lost' else (candidate, new_item)

        score = _compute_score(lost, found)
        if score < SCORE_THRESHOLD:
            continue

        existing = db.matches.find_one({
            'lost_item_id':  lost['_id'],
            'found_item_id': found['_id'],
        })
        if existing:
            continue

        db.matches.insert_one({
            'lost_item_id':  lost['_id'],
            'found_item_id': found['_id'],
            'lost_user_id':  lost.get('user_id') or lost.get('reported_by'),
            'found_user_id': found.get('user_id') or found.get('reported_by'),
            'score':         score,
            'status':        'pending',
            'created_at':    datetime.now(timezone.utc),
        })

        # ── Send email notification for high-confidence matches ──────
        if score >= 80:
            _notify_high_confidence_match(lost, found, score)



        
def _notify_high_confidence_match(lost_item, found_item, score):
    try:
        from flask import url_for
        from app.notifications.email import send_match_notification
        from app.notifications.db import create_notification

        found_url = url_for('items.detail', item_id=str(found_item['_id']), _external=False)
        lost_url  = url_for('items.detail', item_id=str(lost_item['_id']),  _external=False)

        # Email — lost reporter
        send_match_notification(
            recipient_email = lost_item.get('reporter_email', ''),
            recipient_name  = lost_item.get('reporter_name', ''),
            my_item=lost_item, other_item=found_item, score=score,
            view_url=url_for('items.detail', item_id=str(found_item['_id']), _external=True),
        )

        # Email — found reporter
        send_match_notification(
            recipient_email = found_item.get('reporter_email', ''),
            recipient_name  = found_item.get('reporter_name', ''),
            my_item=found_item, other_item=lost_item, score=score,
            view_url=url_for('items.detail', item_id=str(lost_item['_id']), _external=True),
        )

        # In-app — lost reporter
        create_notification(
            user_id  = lost_item.get('user_id') or lost_item.get('reported_by'),
            title    = f"{score}% Match Found!",
            message  = f"Your lost '{lost_item['item_name']}' may match a found item by {found_item.get('reporter_name','')}.",
            link     = found_url,
            notif_type = 'match',
        )

        # In-app — found reporter
        create_notification(
            user_id  = found_item.get('user_id') or found_item.get('reported_by'),
            title    = f"{score}% Match Found!",
            message  = f"Your found '{found_item['item_name']}' may match a lost item by {lost_item.get('reporter_name','')}.",
            link     = lost_url,
            notif_type = 'match',
        )

    except Exception as e:
        current_app.logger.error(f"Match notification error: {e}")