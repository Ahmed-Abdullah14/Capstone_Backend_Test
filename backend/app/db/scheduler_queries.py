from app.db.supabase_client import supabase


def create_scheduled_post(business_id: str, content_calendar_id: str, caption: str, hashtags: list, scheduled_at: str, media_type: str = "REELS", video_url: str = None, image_url: str = None):
    """
    Inserts a new post into calendar_posts for n8n to pick up and publish later.
    
    media_type: "REELS" for video reels, "IMAGE" for image posts
    video_url: required if media_type is "REELS"
    image_url: required if media_type is "IMAGE"
    """
    # Build the media payload based on media type
    if media_type == "REELS":
        if not video_url:
            raise ValueError("video_url is required for REELS")
        media_payload = {
            "media_type": "REELS",
            "video_url": video_url
        }
    elif media_type == "IMAGE":
        if not image_url:
            raise ValueError("image_url is required for IMAGE posts")
        media_payload = {
            "media_type": "IMAGE",
            "image_url": image_url
        }
    else:
        raise ValueError(f"Unsupported media_type: {media_type}. Must be 'REELS' or 'IMAGE'.")

    data = {
        "business_id": business_id,
        "content_calendar_id": content_calendar_id,
        "caption": caption,
        "media": media_payload,
        "hashtags": hashtags,
        "scheduled_at": scheduled_at,
        "status": "scheduled"       # n8n watches for this status
    }

    response = supabase.table("calendar_posts").insert(data).execute()
    return response.data


def reschedule_post(post_id: str, new_scheduled_at: str):
    """Changes the scheduled time and resets status back to 'scheduled' so n8n picks it up again."""
    data = {
        "scheduled_at": new_scheduled_at,
        "status": "scheduled"       # Reset in case it previously failed
    }
    response = supabase.table("calendar_posts").update(data).eq("id", post_id).execute()
    return response.data


def cancel_post(post_id: str):
    """Sets post status to 'draft' so n8n ignores it. (Our enum doesn't have 'canceled', so draft effectively hides it.)"""
    data = {
        "status": "draft"
    }
    response = supabase.table("calendar_posts").update(data).eq("id", post_id).execute()
    return response.data
