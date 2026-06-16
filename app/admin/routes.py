# app/admin/routes.py

from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from bson import ObjectId
from app.admin.utils import admin_required
from app.items.utils import delete_item_photo

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/')
@admin_required
def dashboard():
    db = current_app.db

    stats = {
        'total_users':   db.users.count_documents({}),
        'total_items':   db.items.count_documents({}),
        'lost_items':    db.items.count_documents({'item_type': 'lost'}),
        'found_items':   db.items.count_documents({'item_type': 'found'}),
        'open_items':    db.items.count_documents({'status': 'open'}),
        'claimed_items': db.items.count_documents({'status': 'claimed'}),
        'returned_items':db.items.count_documents({'status': 'returned'}),
        'total_claims':  db.claims.count_documents({}),
        'total_matches': db.matches.count_documents({}),
    }

    # Recovery rate
    if stats['total_items'] > 0:
        stats['recovery_rate'] = round(
            stats['returned_items'] / stats['total_items'] * 100, 1
        )
    else:
        stats['recovery_rate'] = 0

    return render_template('admin/dashboard.html', stats=stats)


@admin_bp.route('/users')
@admin_required
def users():
    db    = current_app.db
    users = list(db.users.find({}).sort('created_at', -1))
    for u in users:
        u['item_count']  = db.items.count_documents({'reported_by': u['_id']})
        u['claim_count'] = db.claims.count_documents({'claimer_id': u['_id']})
    return render_template('admin/users.html', users=users)


@admin_bp.route('/items')
@admin_required
def items():
    db    = current_app.db
    items = list(db.items.find({}).sort('created_at', -1))
    return render_template('admin/items.html', items=items)


@admin_bp.route('/items/<item_id>/delete', methods=['POST'])
@admin_required
def delete_item(item_id):
    db   = current_app.db
    item = db.items.find_one({'_id': ObjectId(item_id)})
    if item:
        if item.get('cloudinary_public_id'):
            delete_item_photo(item['cloudinary_public_id'])
        db.matches.delete_many({'$or': [
            {'lost_item_id': item['_id']},
            {'found_item_id': item['_id']}
        ]})
        db.claims.delete_many({'item_id': item['_id']})
        db.items.delete_one({'_id': item['_id']})
        flash('Item deleted by admin.', 'success')
    return redirect(url_for('admin.items'))


@admin_bp.route('/users/<user_id>/toggle-admin', methods=['POST'])
@admin_required
def toggle_admin(user_id):
    db   = current_app.db
    user = db.users.find_one({'_id': ObjectId(user_id)})
    if user:
        new_status = not user.get('is_admin', False)
        db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'is_admin': new_status}}
        )
        flash(f"Admin status {'granted' if new_status else 'revoked'}.", 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/analytics')
@admin_required
def analytics():
    db = current_app.db

    # Status breakdown
    status_data = {
        'open':     db.items.count_documents({'status': 'open'}),
        'claimed':  db.items.count_documents({'status': 'claimed'}),
        'returned': db.items.count_documents({'status': 'returned'}),
    }

    # Lost vs Found
    type_data = {
        'lost':  db.items.count_documents({'item_type': 'lost'}),
        'found': db.items.count_documents({'item_type': 'found'}),
    }

    # Category breakdown — MongoDB aggregation
    category_pipeline = [
        {'$group': {'_id': '$category', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}}
    ]
    category_data = list(db.items.aggregate(category_pipeline))

    # Items over time (last 14 days)
    from datetime import datetime, timezone, timedelta
    time_pipeline = [
        {'$match': {
            'created_at': {'$gte': datetime.now(timezone.utc) - timedelta(days=14)}
        }},
        {'$group': {
            '_id': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$created_at'}},
            'count': {'$sum': 1}
        }},
        {'$sort': {'_id': 1}}
    ]
    time_data = list(db.items.aggregate(time_pipeline))

    # Recovery rate
    total_items    = db.items.count_documents({})
    returned_items = db.items.count_documents({'status': 'returned'})
    recovery_rate  = round(returned_items / total_items * 100, 1) if total_items > 0 else 0

    return render_template('admin/analytics.html',
        status_data=status_data,
        type_data=type_data,
        category_data=category_data,
        time_data=time_data,
        recovery_rate=recovery_rate,
    )