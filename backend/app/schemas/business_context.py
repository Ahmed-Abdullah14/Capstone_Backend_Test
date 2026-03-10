from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# We are using pydantic models rather than passing dictionaries for better data validation 

class BusinessContext(BaseModel):
    user_id: str        # who is logged in (the LumenIQ account)
    business_id: str    # which business we're working on (one user can have many)

    # Collected during onboarding (required) 
    # TODO_: once Supabase is connected, change these to required fields (remove Optional + None default)
    # These are only Optional now because chainlit_app.py creates an empty BusinessContext
    # before loading from DB. Once repo.get_business_context() is wired up properly,
    # these will always be populated from the frontend onboarding form.
    business_name: Optional[str] = None
    business_type: Optional[str] = None
    location: Optional[str] = None
    target_customers: Optional[str] = None

    # Collected during onboarding (optional) 
    instagram_handle: Optional[str] = None
    website: Optional[str] = None

    # Pipeline state flags (router uses these to skip completed steps) 
    has_hashtags: bool = False           # business profiler has not run yet
    has_competitors: bool = False        # competitor analysis has not found accounts yet
    competitor_count: int = 0
    has_top_posts: bool = False          # competitor posts have not been scraped + ranked
    has_trend_summary: bool = False      # trend analysis is not complete
    has_content_plan: bool = False       # content generator has not run yet

    # Freshness timestamps (for re-run efficiency) 
    hashtags_last_updated: Optional[datetime] = None
    posts_last_scraped: Optional[datetime] = None
    trends_last_updated: Optional[datetime] = None
