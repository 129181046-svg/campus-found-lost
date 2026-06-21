# app/items/routes.py

from flask import (
    Blueprint, render_template, redirect,
    url_for, flash, request, current_app
)
from app.auth.utils import login_required, get_current_user
from app.items.forms import ItemReportForm
from app.items.utils import upload_item_photo, delete_item_photo, parse_tags
from bson import ObjectId
from datetime import datetime, timezone


# -------------------------------------------------------------------------
# BLUEPRINT DEFINITION
# -------------------------------------------------------------------------
items_bp = Blueprint("items", __name__, url_prefix="/items")


# -------------------------------------------------------------------------
# REPORT ITEM — Lost or Found
# -------------------------------------------------------------------------
@items_bp.route("/report", methods=["GET", "POST"])
@login_required
def report():
    form = ItemReportForm()

    if form.validate_on_submit():
        # ── Handle photo upload ──────────────────────────────────────────
        photo_url       = None
        photo_public_id = None

        if form.photo.data:
            upload_result = upload_item_photo(form.photo.data)
            if upload_result:
                photo_url       = upload_result["url"]
                photo_public_id = upload_result["public_id"]
            else:
                flash("Photo upload failed. Item saved without photo.", "warning")

        # ── Parse tags ───────────────────────────────────────────────────
        tags = parse_tags(form.tags.data)

        # ── Get current user ─────────────────────────────────────────────
        user = get_current_user()

        # ── Build item document ──────────────────────────────────────────
        item_doc = {
        "item_type":            form.item_type.data,
        "reported_by":          user["_id"],
        "reporter_name":        user["name"],
        "reporter_email":       user["email"],
        "reporter_phone":       user.get("phone", ""),
        "user_id":              user["_id"],
        "user_name":            user["name"],
        "item_name":            form.item_name.data.strip(),
        "category":             form.category.data,
        "location":             form.location.data,
        "room_number":          form.room_number.data.strip() if form.room_number.data else "",  # ← ADD
        "date_occurred":        datetime.combine(
                                    form.date_occurred.data,
                                    datetime.min.time()
                                ) if form.date_occurred.data else None,
        "description":          form.description.data.strip(),
        "photo_url":            photo_url,
        "cloudinary_public_id": photo_public_id,
        "tags":                 tags,
        "status":               "open",
        "created_at":           datetime.now(timezone.utc),
    }
        
        

        # ── Save to MongoDB ──────────────────────────────────────────────
        result = current_app.db.items.insert_one(item_doc)

        # ── Trigger matching engine ──────────────────────────────────────
        try:
            from app.matching.engine import run_matching
            run_matching(str(result.inserted_id))
        except Exception as e:
            print(f"Matching engine error: {e}")

            flash(
            f"Your {form.item_type.data} item report has been submitted successfully!",
            "success"
        )
    # CHANGED: redirect to explore instead of own item detail
        return redirect(url_for("items.explore"))   

    return render_template("items/report.html", form=form)


# -------------------------------------------------------------------------
# ITEM DETAIL PAGE
# -------------------------------------------------------------------------
@items_bp.route("/<item_id>")
def detail(item_id):
    try:
        oid = ObjectId(item_id)
    except Exception:
        flash("Invalid item ID.", "danger")
        return redirect(url_for("main.home"))

    item = current_app.db.items.find_one({"_id": oid})

    if not item:
        flash("Item not found.", "danger")
        return redirect(url_for("main.home"))

    current_user = get_current_user()
    is_owner = (
        current_user is not None and
        str(item["reported_by"]) == str(current_user["_id"])
    )

    return render_template("items/detail.html",
                           item=item,
                           is_owner=is_owner,
                           current_user=current_user)


# -------------------------------------------------------------------------
# MY ITEMS — Dashboard
# -------------------------------------------------------------------------
@items_bp.route("/my-items")
@login_required
def my_items():
    user = get_current_user()

    items = list(current_app.db.items.find(
        {"reported_by": user["_id"]}
    ).sort("created_at", -1))

    return render_template("items/my_items.html",
                           items=items,
                           user=user)


# -------------------------------------------------------------------------
# DELETE ITEM
# -------------------------------------------------------------------------
@items_bp.route("/<item_id>/delete", methods=["POST"])
@login_required
def delete(item_id):
    try:
        oid = ObjectId(item_id)
    except Exception:
        flash("Invalid item ID.", "danger")
        return redirect(url_for("items.my_items"))

    item = current_app.db.items.find_one({"_id": oid})

    if not item:
        flash("Item not found.", "danger")
        return redirect(url_for("items.my_items"))

    user = get_current_user()
    if str(item["reported_by"]) != str(user["_id"]):
        flash("You can only delete your own items.", "danger")
        return redirect(url_for("items.my_items"))

    # ── Delete photo from Cloudinary ─────────────────────────────────────
    if item.get("cloudinary_public_id"):
        delete_item_photo(item["cloudinary_public_id"])

    # ── Delete related matches ───────────────────────────────────────────
    current_app.db.matches.delete_many({
        "$or": [
            {"lost_item_id":  oid},
            {"found_item_id": oid},
        ]
    })

    # ── Delete item document ─────────────────────────────────────────────
    current_app.db.items.delete_one({"_id": oid})

    flash("Item report deleted successfully.", "success")
    return redirect(url_for("items.my_items"))


# -------------------------------------------------------------------------
# EDIT ITEM
# -------------------------------------------------------------------------
@items_bp.route("/<item_id>/edit", methods=["GET", "POST"])
@login_required
def edit(item_id):
    try:
        oid = ObjectId(item_id)
    except Exception:
        flash("Invalid item ID.", "danger")
        return redirect(url_for("items.my_items"))

    item = current_app.db.items.find_one({"_id": oid})

    if not item:
        flash("Item not found.", "danger")
        return redirect(url_for("items.my_items"))

    user = get_current_user()
    if str(item["reported_by"]) != str(user["_id"]):
        flash("You can only edit your own items.", "danger")
        return redirect(url_for("items.my_items"))

    form = ItemReportForm()

    if form.validate_on_submit():
        photo_url       = item.get("photo_url")
        photo_public_id = item.get("cloudinary_public_id")

        if form.photo.data:
            if photo_public_id:
                delete_item_photo(photo_public_id)
            upload_result = upload_item_photo(form.photo.data)
            if upload_result:
                photo_url       = upload_result["url"]
                photo_public_id = upload_result["public_id"]
            else:
                flash("Photo upload failed. Keeping existing photo.", "warning")

        tags = parse_tags(form.tags.data)

        current_app.db.items.update_one(
            {"_id": oid},
            {"$set": {
                "item_type":            form.item_type.data,
                "item_name":            form.item_name.data.strip(),
                "category":             form.category.data,
                "location":             form.location.data,
                "date_occurred":        datetime.combine(
                                            form.date_occurred.data,
                                            datetime.min.time()
                                        ) if form.date_occurred.data else None,
                "description":          form.description.data.strip(),
                "photo_url":            photo_url,
                "cloudinary_public_id": photo_public_id,
                "tags":                 tags,
                "updated_at":           datetime.now(timezone.utc),
            }}
        )

        flash("Item updated successfully.", "success")
        return redirect(url_for("items.detail", item_id=item_id))

    elif request.method == "GET":
        form.item_type.data   = item["item_type"]
        form.item_name.data   = item["item_name"]
        form.category.data    = item["category"]
        form.location.data    = item["location"]
        form.room_number.data = item.get("room_number", "")
        form.date_occurred.data = item.get("date_occurred").date() if item.get("date_occurred") else None
        form.description.data = item["description"]
        form.tags.data        = ", ".join(item.get("tags", []))

    return render_template("items/report.html",
                           form=form,
                           editing=True,
                           item=item)
@items_bp.route('/explore')
@login_required
def explore():
    db   = current_app.db
    user = get_current_user()

    # Show all OPEN items from OTHER users, newest first
    items = list(db.items.find({
        'status': 'open',
        'reported_by': {'$ne': user['_id']}
    }).sort('created_at', -1).limit(50))

    return render_template('items/explore.html', items=items)