from app.agents.base_agent import Agent
from app.db.scheduler_queries import create_scheduled_post, reschedule_post, cancel_post
from app.schemas.agent_results import SchedulerResult

class SchedulerAgent(Agent):
    def __init__(self, kernel):
        super().__init__(kernel=kernel, name="scheduler_agent")

    async def run(self, action: str, **kwargs) -> SchedulerResult:
        """
        Routes the user's scheduling intent to the correct database function.
        Python only writes to the DB — n8n handles the actual Instagram posting.

        Supported actions: 'schedule', 'reschedule', 'cancel'

        Required kwargs per action:
            schedule:   business_id, content_calendar_id, caption, hashtags, scheduled_at,
                        media_type ("REELS" or "IMAGE"), video_url (for reels), image_url (for images)
            reschedule: business_id, post_id, scheduled_at
            cancel:     business_id, post_id
        """
        try:
            if action == "schedule":
                post = create_scheduled_post(
                    business_id=kwargs.get("business_id"),
                    content_calendar_id=kwargs.get("content_calendar_id"),
                    caption=kwargs.get("caption"),
                    hashtags=kwargs.get("hashtags", []),
                    scheduled_at=kwargs.get("scheduled_at"),
                    media_type=kwargs.get("media_type", "REELS"),
                    video_url=kwargs.get("video_url"),
                    image_url=kwargs.get("image_url")
                )
                return SchedulerResult(
                    business_id=kwargs.get("business_id"),
                    success=True,
                    message=f"Post scheduled for {kwargs.get('scheduled_at')}.",
                    calendar_post_id=post[0]["id"]
                )

            elif action == "reschedule":
                post = reschedule_post(
                    post_id=kwargs.get("post_id"),
                    new_scheduled_at=kwargs.get("scheduled_at")
                )
                return SchedulerResult(
                    business_id=kwargs.get("business_id", ""),
                    success=True,
                    message=f"Post rescheduled to {kwargs.get('scheduled_at')}.",
                    calendar_post_id=post[0]["id"]
                )

            elif action == "cancel":
                post = cancel_post(
                    post_id=kwargs.get("post_id")
                )
                return SchedulerResult(
                    business_id=kwargs.get("business_id", ""),
                    success=True,
                    message="Post canceled.",
                    calendar_post_id=post[0]["id"]
                )

            else:
                return SchedulerResult(
                    business_id=kwargs.get("business_id", ""),
                    success=False,
                    message=f"Unknown action: {action}"
                )

        except Exception as e:
            return SchedulerResult(
                business_id=kwargs.get("business_id", ""),
                success=False,
                message=str(e)
            )