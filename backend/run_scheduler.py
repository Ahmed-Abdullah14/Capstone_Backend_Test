import asyncio
from datetime import datetime, timezone
from semantic_kernel import Kernel
from app.agents.scheduler_agent import SchedulerAgent


# ──────────────────────────────────────────────
#  Test data — update these if testing a different business
# ──────────────────────────────────────────────
BUSINESS_ID = "54eb934a-83b3-4ca4-9caf-8b3575e5d3ff"
CONTENT_CALENDAR_ID = "0fabf794-50b9-438c-af89-b4f3f5c91409"

# Public test image (square aspect ratio for Instagram)
TEST_IMAGE_URL = "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=1080&q=80"

# IMPORTANT: Meta blocks most third-party sample video sites.
# Upload a short .mp4 to Supabase Storage and paste the public URL here.
TEST_VIDEO_URL = "https://wrtchdarqkbjalijviyg.supabase.co/storage/v1/object/public/test/test.mov"  # e.g. "https://your-project.supabase.co/storage/v1/object/public/test-media/clip.mp4"


async def test_schedule_image():
    """Test 1: Schedule an IMAGE post and verify it lands in Supabase."""
    agent = SchedulerAgent(kernel=Kernel())

    print("\n" + "=" * 60)
    print("TEST 1: Schedule an IMAGE post")
    print("=" * 60)

    result = await agent.run(
        action="schedule",
        business_id=BUSINESS_ID,
        content_calendar_id=CONTENT_CALENDAR_ID,
        caption="Testing image scheduling via run_scheduler.py",
        hashtags=["lumeniq", "test", "coffeepost"],
        scheduled_at=datetime.now(timezone.utc).isoformat(),
        media_type="IMAGE",
        image_url=TEST_IMAGE_URL,
    )

    print(f"  Success:          {result.success}")
    print(f"  Message:          {result.message}")
    print(f"  Calendar Post ID: {result.calendar_post_id}")

    if not result.success:
        print(f"\n  ERROR: {result.message}")
        return None

    print("\n  >>> Check Supabase: calendar_posts should have a new row with status='scheduled'")
    print("  >>> n8n will pick this up and post it to Instagram automatically")
    return result.calendar_post_id


async def test_schedule_reel():
    """Test 2: Schedule a REEL post."""
    agent = SchedulerAgent(kernel=Kernel())

    print("\n" + "=" * 60)
    print("TEST 2: Schedule a REEL post")
    print("=" * 60)

    result = await agent.run(
        action="schedule",
        business_id=BUSINESS_ID,
        content_calendar_id=CONTENT_CALENDAR_ID,
        caption="Testing reel scheduling via run_scheduler.py",
        hashtags=["lumeniq", "test", "reeltest"],
        scheduled_at=datetime.now(timezone.utc).isoformat(),
        media_type="REELS",
        reel_video_url=TEST_VIDEO_URL,
    )

    print(f"  Success:          {result.success}")
    print(f"  Message:          {result.message}")
    print(f"  Calendar Post ID: {result.calendar_post_id}")

    if not result.success:
        print(f"\n  ERROR: {result.message}")
    return result.calendar_post_id


async def test_reschedule(post_id: str):
    """Test 3: Reschedule an existing post to a new time."""
    agent = SchedulerAgent(kernel=Kernel())

    print("\n" + "=" * 60)
    print(f"TEST 3: Reschedule post {post_id}")
    print("=" * 60)

    new_time = "2026-04-15T14:00:00+00:00"
    result = await agent.run(
        action="reschedule",
        business_id=BUSINESS_ID,
        post_id=post_id,
        scheduled_at=new_time,
    )

    print(f"  Success:          {result.success}")
    print(f"  Message:          {result.message}")
    print(f"  Calendar Post ID: {result.calendar_post_id}")

    if not result.success:
        print(f"\n  ERROR: {result.message}")


async def test_cancel(post_id: str):
    """Test 4: Cancel an existing post (sets status to draft)."""
    agent = SchedulerAgent(kernel=Kernel())

    print("\n" + "=" * 60)
    print(f"TEST 4: Cancel post {post_id}")
    print("=" * 60)

    result = await agent.run(
        action="cancel",
        business_id=BUSINESS_ID,
        post_id=post_id,
    )

    print(f"  Success:          {result.success}")
    print(f"  Message:          {result.message}")
    print(f"  Calendar Post ID: {result.calendar_post_id}")

    if not result.success:
        print(f"\n  ERROR: {result.message}")


async def main():
    print("=" * 60)
    print("  SCHEDULER AGENT TEST SUITE")
    print("=" * 60)
    print(f"  Business ID:          {BUSINESS_ID}")
    print(f"  Content Calendar ID:  {CONTENT_CALENDAR_ID}")
    print()

    print("Which test do you want to run?")
    print("  1) Schedule an IMAGE post (n8n will post it!)")
    print("  2) Schedule a REEL post (n8n will post it!)")
    print("  3) Reschedule an existing post")
    print("  4) Cancel an existing post")
    print("  5) Run all tests (schedule image, reschedule it, then cancel it)")
    print()

    choice = input("Enter choice (1-5): ").strip()

    if choice == "1":
        await test_schedule_image()

    elif choice == "2":
        await test_schedule_reel()

    elif choice == "3":
        post_id = input("Enter the calendar_post_id to reschedule: ").strip()
        await test_reschedule(post_id)

    elif choice == "4":
        post_id = input("Enter the calendar_post_id to cancel: ").strip()
        await test_cancel(post_id)

    elif choice == "5":
        post_id = await test_schedule_image()
        if post_id:
            await test_reschedule(post_id)
            await test_cancel(post_id)

    else:
        print("Invalid choice.")

    print("\n" + "=" * 60)
    print("  DONE")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
