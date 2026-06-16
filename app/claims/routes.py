# app/claims/routes.py

from flask import Blueprint, render_template, redirect, url_for, flash, current_app, request
from bson import ObjectId
from datetime import datetime, timezone
from app.auth.utils import login_required, get_current_user
from app.notifications.db import create_notification
from app.notifications.email import send_claim_submitted, send_claim_approved, send_claim_rejected
from .forms import ClaimForm

claims_bp = Blueprint('claims', __name__, url_prefix='/claims')


# ── Submit a claim on a found item ───────────────────────────────────────
@claims_bp.route('/submit/<item_id>', methods=['GET', 'POST'])
@login_required
def submit(item_id):
    try:
        oid = ObjectId(item_id)
    except Exception:
        flash('Invalid item.', 'danger')
        return redirect(url_for('main.home'))

    db   = current_app.db
    item = db.items.find_one({'_id': oid})

    if not item:
        flash('Item not found.', 'danger')
        return redirect(url_for('main.home'))

    # Only non-owners can claim a found item
    user = get_current_user()
    if str(item.get('reported_by')) == str(user['_id']):
        flash('You cannot claim your own item.', 'warning')
        return redirect(url_for('items.detail', item_id=item_id))

    # Prevent duplicate claims
    existing = db.claims.find_one({
        'item_id':    oid,
        'claimer_id': user['_id'],
    })
    if existing:
        flash('You have already submitted a claim for this item.', 'info')
        return redirect(url_for('items.detail', item_id=item_id))

    form = ClaimForm()

    if form.validate_on_submit():
        claim_doc = {
            'item_id':        oid,
            'item_name':      item['item_name'],
            'finder_id':      item['reported_by'],
            'finder_name':    item.get('reporter_name', ''),
            'claimer_id':     user['_id'],
            'claimer_name':   user['name'],
            'claimer_email':  user['email'],
            'color':          form.color.data.strip(),
            'brand':          form.brand.data.strip(),
            'unique_marks':   form.unique_marks.data.strip(),
            'extra_info':     form.extra_info.data.strip(),
            'status':         'pending',
            'created_at':     datetime.now(timezone.utc),
        }
        db.claims.insert_one(claim_doc)

        # Update item status to 'claimed'
        db.items.update_one(
            {'_id': oid},
            {'$set': {'status': 'claimed'}}
        )

        # ── Email the finder ──────────────────────────────────────────
        incoming_url = request.host_url.rstrip('/') + url_for('claims.incoming')
        send_claim_submitted(
            finder_email = item.get('reporter_email', ''),
            finder_name  = item.get('reporter_name', ''),
            claimer_name = user['name'],
            item_name    = item['item_name'],
            incoming_url = incoming_url,
        )

        # ── In-app notification to the finder ─────────────────────────
        create_notification(
            user_id    = item['reported_by'],
            title      = "New Claim Received",
            message    = f"{user['name']} claimed your item '{item['item_name']}'.",
            link       = url_for('claims.incoming'),
            notif_type = 'claim',
        )

        flash('Your claim has been submitted! The finder will review it.', 'success')
        return redirect(url_for('items.detail', item_id=item_id))

    return render_template('claims/submit.html', form=form, item=item)


# ── My Claims — items I have claimed ─────────────────────────────────────
@claims_bp.route('/my-claims')
@login_required
def my_claims():
    user   = get_current_user()
    db     = current_app.db
    claims = list(db.claims.find(
        {'claimer_id': user['_id']}
    ).sort('created_at', -1))

    for c in claims:
        c['item'] = db.items.find_one({'_id': c['item_id']})

    return render_template('claims/my_claims.html', claims=claims)


# ── Incoming Claims — claims on items I found ─────────────────────────────
@claims_bp.route('/incoming')
@login_required
def incoming():
    user   = get_current_user()
    db     = current_app.db
    claims = list(db.claims.find(
        {'finder_id': user['_id']}
    ).sort('created_at', -1))

    for c in claims:
        c['item'] = db.items.find_one({'_id': c['item_id']})

    return render_template('claims/incoming.html', claims=claims)


# ── Approve a claim ───────────────────────────────────────────────────────
@claims_bp.route('/<claim_id>/approve', methods=['POST'])
@login_required
def approve(claim_id):
    db    = current_app.db
    user  = get_current_user()

    try:
        claim = db.claims.find_one({'_id': ObjectId(claim_id)})
    except Exception:
        flash('Invalid claim.', 'danger')
        return redirect(url_for('claims.incoming'))

    if not claim or str(claim['finder_id']) != str(user['_id']):
        flash('Not authorised.', 'danger')
        return redirect(url_for('claims.incoming'))

    db.claims.update_one(
        {'_id': ObjectId(claim_id)},
        {'$set': {'status': 'approved',
                  'resolved_at': datetime.now(timezone.utc)}}
    )
    db.items.update_one(
        {'_id': claim['item_id']},
        {'$set': {'status': 'returned'}}
    )

    # ── Email the claimant ─────────────────────────────────────────────
    send_claim_approved(
        claimer_email = claim['claimer_email'],
        claimer_name  = claim['claimer_name'],
        item_name     = claim['item_name'],
        finder_name   = user['name'],
        finder_email  = user['email'],
    )

    # ── In-app notification to the claimant ────────────────────────────
    create_notification(
        user_id    = claim['claimer_id'],
        title      = "Claim Approved!",
        message    = f"Your claim on '{claim['item_name']}' was approved by {user['name']}. Contact them to collect it.",
        link       = url_for('claims.my_claims'),
        notif_type = 'claim',
    )

    flash('Claim approved! Mark the item as returned to the owner.', 'success')
    return redirect(url_for('claims.incoming'))


# ── Reject a claim ────────────────────────────────────────────────────────
@claims_bp.route('/<claim_id>/reject', methods=['POST'])
@login_required
def reject(claim_id):
    db   = current_app.db
    user = get_current_user()

    try:
        claim = db.claims.find_one({'_id': ObjectId(claim_id)})
    except Exception:
        flash('Invalid claim.', 'danger')
        return redirect(url_for('claims.incoming'))

    if not claim or str(claim['finder_id']) != str(user['_id']):
        flash('Not authorised.', 'danger')
        return redirect(url_for('claims.incoming'))

    db.claims.update_one(
        {'_id': ObjectId(claim_id)},
        {'$set': {'status': 'rejected',
                  'resolved_at': datetime.now(timezone.utc)}}
    )
    db.items.update_one(
        {'_id': claim['item_id']},
        {'$set': {'status': 'open'}}
    )

    # ── Email the claimant ─────────────────────────────────────────────
    send_claim_rejected(
        claimer_email = claim['claimer_email'],
        claimer_name  = claim['claimer_name'],
        item_name     = claim['item_name'],
    )

    # ── In-app notification to the claimant ────────────────────────────
    create_notification(
        user_id    = claim['claimer_id'],
        title      = "Claim Not Approved",
        message    = f"Your claim on '{claim['item_name']}' was not approved. The item is open again.",
        link       = url_for('claims.my_claims'),
        notif_type = 'claim',
    )

    flash('Claim rejected. Item is open again.', 'info')
    return redirect(url_for('claims.incoming'))