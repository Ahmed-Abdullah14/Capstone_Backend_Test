from app.db.supabase_client import supabase
from app.schemas.business_context import BusinessContext

# This file will have all DB functions related to the business profiler agent 

class BusinessProfilerQueries:

    # DB Function to fetch business context
    def get_business_context(self, user_id, business_id):
        # Mocked data right now to get business context, once DB is connected it should get this from DB
        return BusinessContext(
            user_id=user_id,
            business_id=business_id,
            business_name="Downtown Calgary Cafe",
            business_type="Local Cafe Shop",
            location="Calgary, Alberta",
            target_customers="Students and young professionals",
            instagram_handle="downtown_cafe"
        )
    
    # Future functions could include save and get hashtags for this agent