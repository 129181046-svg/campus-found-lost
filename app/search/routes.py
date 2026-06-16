# app/search/routes.py

from flask import Blueprint, render_template, request, current_app

search_bp = Blueprint('search', __name__, url_prefix='/search')


@search_bp.route('/')
def results():
    db = current_app.db

    # ── Read query parameters ────────────────────────────────────────
    query    = request.args.get('q', '').strip()
    category = request.args.get('category', '')
    location = request.args.get('location', '')
    item_type = request.args.get('item_type', '')
    status   = request.args.get('status', 'open')

    # ── Build MongoDB filter ─────────────────────────────────────────
    filters = {}

    if query:
        filters['$text'] = {'$search': query}

    if category:
        filters['category'] = category

    if location:
        filters['location'] = location

    if item_type in ('lost', 'found'):
        filters['item_type'] = item_type

    if status:
        filters['status'] = status

    # ── Execute query ────────────────────────────────────────────────
    try:
        if query:
            # Text search — sort by relevance score
            items = list(db.items.find(
                filters,
                {'score': {'$meta': 'textScore'}}
            ).sort([('score', {'$meta': 'textScore'})]).limit(50))
        else:
            # No text query — sort by newest first
            items = list(db.items.find(filters).sort('created_at', -1).limit(50))
    except Exception as e:
        current_app.logger.error(f"Search error: {e}")
        items = []

    return render_template('search/results.html',
                           items=items,
                           query=query,
                           category=category,
                           location=location,
                           item_type=item_type,
                           status=status)