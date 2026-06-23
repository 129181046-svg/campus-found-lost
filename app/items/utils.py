# app/items/utils.py

import cloudinary
import cloudinary.uploader
from flask import current_app


def configure_cloudinary():
    cloudinary.config(
        cloud_name = current_app.config["CLOUDINARY_CLOUD_NAME"],
        api_key    = current_app.config["CLOUDINARY_API_KEY"],
        api_secret = current_app.config["CLOUDINARY_API_SECRET"],
        secure     = True
    )


def upload_item_photo(file_stream):
    # Reconfigure on every upload to ensure credentials are fresh
    configure_cloudinary()
    try:
        result = cloudinary.uploader.upload(
            file_stream,
            folder         = "campus_laf/items",
            transformation = [
                {"width": 800, "crop": "limit"},
                {"fetch_format": "webp"},
            ],
            resource_type  = "image",
        )
        return {
            "url":       result["secure_url"],
            "public_id": result["public_id"],
        }
    except Exception as e:
        current_app.logger.error(f"Cloudinary upload failed: {e}")
        return None


def delete_item_photo(public_id):
    if not public_id:
        return True
    try:
        result = cloudinary.uploader.destroy(public_id)
        return result.get("result") == "ok"
    except Exception as e:
        current_app.logger.error(f"Cloudinary deletion failed: {e}")
        return False


def parse_tags(tags_string):
    if not tags_string:
        return []
    tags = [t.strip().lower() for t in tags_string.split(",")]
    tags = [t for t in tags if t]
    return tags[:10]