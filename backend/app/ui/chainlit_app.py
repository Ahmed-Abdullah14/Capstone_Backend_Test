import chainlit as cl
from semantic_kernel.contents import ChatHistory
from semantic_kernel.agents import ChatHistoryAgentThread
from app.kernel_config import kernel_init
from app.agents.manager_agent import ManagerAgent
from app.schemas.business_context import BusinessContext
from app.schemas.user_request import UserRequest
from app.db.business_profiler_queries import BusinessProfilerQueries


kernel = kernel_init()
manager = ManagerAgent(kernel)
business_profiler_queries = BusinessProfilerQueries()


@cl.on_chat_start
async def on_chat_start():
    
    thread = ChatHistoryAgentThread(chat_history=ChatHistory())
    cl.user_session.set("thread", thread)

    user_id = "user_123"
    business_id = "business_123"

    cl.user_session.set("user_id", user_id)
    cl.user_session.set("business_id", business_id)
    
    context = business_profiler_queries.get_business_context(user_id, business_id)
    cl.user_session.set("context", context)

    await cl.Message(content = (
        "Welcome to LumenIQ.\n\n"
        "I'm your AI assistant. I can help you create engaging social media content, schedule posts, analyze trends, and manage your social media strategy.\n\n"
        "Your business profile has been set up. Whenever you're ready, let me know would you like to work on today?"
    )).send()
    
