from datetime import datetime, timezone
from app.agents.base_agent import Agent
from app.db.scheduler_queries import (
    create_scheduled_post,
    reschedule_post,
    cancel_post,
    get_latest_content_idea,
    get_latest_scheduled_post,
)
from app.schemas.agent_results import SchedulerResult


class SchedulerAgent(Agent):
    def __init__(self, kernel):
        super().__init__(kernel=kernel, name="scheduler_agent")

    async def run(self, **kwargs) -> SchedulerResult:
        """
        Routes the user's scheduling intent to the correct database function.
        Python only writes to the DB — n8n handles the actual Instagram posting.

        Supported actions passed via kwargs['action']: 'schedule', 'reschedule', 'cancel'

        Can be called two ways:
          1. Explicitly (from run_scheduler.py / tests) — pass all fields as kwargs
          2. From manager_agent — pass context + action only; missing fields are
             auto-fetched from the DB (latest content_idea / calendar_post)
        """
        context = kwargs.get("context")
        action: str = kwargs.get("action") or ""

        # Extract business_id from context if not passed directly
        business_id: str = kwargs.get("business_id") or (context.business_id if context else "")

        try:
            if action == "schedule":
                caption      = kwargs.get("caption")
                hashtags     = kwargs.get("hashtags")
                scheduled_at = kwargs.get("scheduled_at")
                media_type   = kwargs.get("media_type")
                image_url    = kwargs.get("image_url")
                reel_video_url = kwargs.get("reel_video_url")

                # Auto-fetch caption/hashtags/image from latest content idea if not passed
                if not caption or not hashtags:
                    idea = get_latest_content_idea(business_id)
                    if not idea:
                        return SchedulerResult(
                            business_id=business_id,
                            success=False,
                            message="No content idea found. Please generate content first before scheduling.",
                        )
                    caption  = caption  or idea.get("caption") or ""
                    hashtags = hashtags or idea.get("hashtags") or []

                    # Pull image_url from assets if not explicitly provided
                    if not image_url and not reel_video_url:
                        assets = idea.get("assets") or {}
                        image_url = assets.get("image_url")

                # Default to now if no scheduled time provided
                if not scheduled_at:
                    scheduled_at = datetime.now(timezone.utc).isoformat()

                # Infer media_type from whichever URL is present
                if not media_type:
                    media_type = "IMAGE" if image_url else "REELS"

                post = create_scheduled_post(
                    business_id=business_id,
                    caption=caption,
                    hashtags=hashtags,
                    scheduled_at=scheduled_at,
                    media_type=media_type,
                    reel_video_url=reel_video_url,
                    image_url=image_url,
                )
                return SchedulerResult(
                    business_id=business_id,
                    success=True,
                    message=f"Post scheduled for {scheduled_at}.",
                    calendar_post_id=post[0]["id"],
                )

            elif action == "reschedule":
                post_id      = kwargs.get("post_id")
                scheduled_at = kwargs.get("scheduled_at")

                # Auto-fetch the most recent scheduled post if post_id not passed
                if not post_id:
                    latest = get_latest_scheduled_post(business_id)
                    if not latest:
                        return SchedulerResult(
                            business_id=business_id,
                            success=False,
                            message="No scheduled post found to reschedule.",
                        )
                    post_id = latest["id"]

                if not scheduled_at:
                    scheduled_at = datetime.now(timezone.utc).isoformat()

                post = reschedule_post(
                    post_id=post_id,
                    new_scheduled_at=scheduled_at,
                )
                return SchedulerResult(
                    business_id=business_id,
                    success=True,
                    message=f"Post rescheduled to {scheduled_at}.",
                    calendar_post_id=post[0]["id"],
                )

            elif action == "cancel":
                post_id = kwargs.get("post_id")

                # Auto-fetch the most recent scheduled post if post_id not passed
                if not post_id:
                    latest = get_latest_scheduled_post(business_id)
                    if not latest:
                        return SchedulerResult(
                            business_id=business_id,
                            success=False,
                            message="No scheduled post found to cancel.",
                        )
                    post_id = latest["id"]

                post = cancel_post(post_id=post_id)
                return SchedulerResult(
                    business_id=business_id,
                    success=True,
                    message="Post canceled.",
                    calendar_post_id=post[0]["id"],
                )

            else:
                return SchedulerResult(
                    business_id=business_id,
                    success=False,
                    message=f"Unknown action: '{action}'. Must be 'schedule', 'reschedule', or 'cancel'.",
                )

        except Exception as e:
            return SchedulerResult(
                business_id=business_id,
                success=False,
                message=str(e),
            )
