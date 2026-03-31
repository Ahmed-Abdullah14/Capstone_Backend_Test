from typing import Optional
from datetime import datetime
from app.db.supabase_client import supabase
from app.schemas.business_context import check_utc


def create_scheduled_post(
    business_id: str,
    caption: str,
    hashtags: list,
    scheduled_at: str,  # ISO 8601 string — will be normalized to UTC
    media_type: str = "REELS",
    reel_video_url: Optional[str] = None,
    image_url: Optional[str] = None,
) -> list:
    """
    Inserts a new post into calendar_posts for n8n to pick up and publish later.

    media_type: "REELS" for video reels, "IMAGE" for image posts
    reel_video_url: required if media_type is "REELS"
    image_url:      required if media_type is "IMAGE"

    n8n determines media type by checking which key exists:
        { "reel_video_url": "..." }  ->  Reel
        { "url": "..." }            ->  Image
    """
    # Normalize to UTC so n8n (which runs on UTC) fires at the right time
    utc_scheduled_at = check_utc(datetime.fromisoformat(scheduled_at)).isoformat()

    if media_type == "REELS":
        if not reel_video_url:
            raise ValueError("reel_video_url is required for REELS")
        media_payload = {"reel_video_url": reel_video_url}
    elif media_type == "IMAGE":
        if not image_url:
            raise ValueError("image_url is required for IMAGE posts")
        media_payload = {"url": image_url}
    else:
        raise ValueError(f"Unsupported media_type: '{media_type}'. Must be 'REELS' or 'IMAGE'.")

    data = {
        "business_id": business_id,
        "caption": caption,
        "media": media_payload,
        "hashtags": hashtags,
        "scheduled_at": utc_scheduled_at,
        "status": "scheduled",  # n8n watches for this status
    }

    response = supabase.table("calendar_posts").insert(data).execute()
    return response.data


def reschedule_post(post_id: str, new_scheduled_at: str) -> list:
    """Changes the scheduled time and resets status to 'scheduled' so n8n picks it up again."""
    utc_scheduled_at = check_utc(datetime.fromisoformat(new_scheduled_at)).isoformat()
    data = {
        "scheduled_at": utc_scheduled_at,
        "status": "scheduled",  # Reset in case it previously failed
    }
    response = (
        supabase.table("calendar_posts")
        .update(data)
        .eq("id", post_id)
        .select()           # Ensures the updated row is returned
        .execute()
    )
    return response.data


def cancel_post(post_id: str) -> list:
    """Sets post status to 'draft' so n8n ignores it. (Enum has no 'canceled', so draft hides it.)"""
    response = (
        supabase.table("calendar_posts")
        .update({"status": "draft"})
        .eq("id", post_id)
        .select()           # Ensures the updated row is returned
        .execute()
    )
    return response.data
