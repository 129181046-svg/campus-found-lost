# app/items/utils.py

import cloudinary
import cloudinary.uploader
from flask import current_app


# -------------------------------------------------------------------------
# CONFIGURE CLOUDINARY
# -------------------------------------------------------------------------
def configure_cloudinary():
    """
    Reads Cloudinary credentials from Flask app config and
    initialises the Cloudinary SDK.
    Called once inside create_app() after config is loaded.
    """
    cloudinary.config(
        cloud_name = current_app.config["CLOUDINARY_CLOUD_NAME"],
        api_key    = current_app.config["CLOUDINARY_API_KEY"],
        api_secret = current_app.config["CLOUDINARY_API_SECRET"],
        secure     = True  # Always use HTTPS URLs
    )


# -------------------------------------------------------------------------
# UPLOAD IMAGE TO CLOUDINARY
# -------------------------------------------------------------------------
def upload_item_photo(file_stream):
    """
    Uploads an image file to Cloudinary with transformations.

    Transformations applied automatically:
    - Resize to max 800px width (maintains aspect ratio)
    - Convert to WebP format (smaller file size, same quality)
    - Strip EXIF data (removes GPS coordinates — privacy protection)
    - Store in 'campus_laf/items' folder in Cloudinary

    Returns a dict with:
        url        — the CDN URL to store in MongoDB
        public_id  — needed later to delete the image

    Returns None if upload fails.
    """
    try:
        result = cloudinary.uploader.upload(
            file_stream,
            folder          = "campus_laf/items",
            transformation  = [
                {"width": 800, "crop": "limit"},  # Max 800px, no upscaling
                {"fetch_format": "webp"},          # Convert to WebP
                {"flags": "strip_exif"},           # Remove GPS metadata
            ],resource_type = "image",
        )
        return {
            "url":       result["secure_url"],
            "public_id": result["public_id"],
        }
    except Exception as e:
        current_app.logger.error(f"Cloudinary upload failed: {e}")
        return None


# -------------------------------------------------------------------------
# DELETE IMAGE FROM CLOUDINARY
# -------------------------------------------------------------------------
def delete_item_photo(public_id):
    """
    Deletes an image from Cloudinary by its public_id.
    Called when a user deletes their item report.

    Without this, deleted items leave orphaned images in Cloudinary
    consuming storage forever.

    Returns True if deletion succeeded, False otherwise.
    """
    if not public_id:
        return True  # Nothing to delete
    try:
        result = cloudinary.uploader.destroy(public_id)
        return result.get("result") == "ok"
    except Exception as e:
        current_app.logger.error(f"Cloudinary deletion failed: {e}")
        return False


# -------------------------------------------------------------------------
# PARSE TAGS
# -------------------------------------------------------------------------
def parse_tags(tags_string):
    """
    Converts a comma-separated tag string into a clean list.

    Input:  "  Black , Leather,  wallet  "
    Output: ["black", "leather", "wallet"]

    - Strips whitespace from each tag
    - Lowercases everything for consistent matching
    - Removes empty strings
    - Limits to 10 tags maximum
    """
    if not tags_string:
        return []
    tags = [t.strip().lower() for t in tags_string.split(",")]
    tags = [t for t in tags if t]  # Remove empty strings
    return tags[:10]               # Cap at 10 tags