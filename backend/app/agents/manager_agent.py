import chainlit as cl
from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent, ChatHistoryAgentThread
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.connectors.ai.open_ai import OpenAIChatPromptExecutionSettings
from app.agents.base_agent import Agent
from app.agents.business_profiler_agent import BusinessProfilerAgent
from app.agents.competitor_analysis_agent import CompetitorAnalysisAgent
from app.agents.trend_analysis_agent import TrendAnalysisAgent
from app.agents.content_generator_agent import ContentGeneratorAgent
from app.agents.scheduler_agent import SchedulerAgent
from app.schemas.business_context import BusinessContext
from app.schemas.manager_decision import ManagerDecision
from app.schemas.user_request import UserRequest
from app.orchestrator.intent_classifier import IntentClassifier
from app.orchestrator.router import Router
from app.orchestrator.route_types import RouteType
from app.db.business_profiler_queries import BusinessProfilerQueries
from pathlib import Path

MANAGER_INSTRUCTIONS = ""

class ManagerAgent(Agent):
    def __init__(self, kernel):
        super().__init__(kernel=kernel, name="manager_agent")

        # Instantitating all agents
        self.business_profiler_agent = BusinessProfilerAgent(kernel)
        self.competitor_analysis_agent = CompetitorAnalysisAgent(kernel)
        self.trend_analysis_agent = TrendAnalysisAgent(kernel)
        self.content_generator_agent = ContentGeneratorAgent(kernel)
        self.scheduler_agent = SchedulerAgent(kernel)

        # Instantiating routes and intents
        self.intent_classifier = IntentClassifier()
        self.router = Router()

        # Instantiating Manager
        self.agent = ChatCompletionAgent(
            service = kernel.get_service(type=ChatCompletionClientBase),
            name = "Manager_Agent",
            instructions = MANAGER_INSTRUCTIONS
        )

    async def run(self, user_request, business_context, thread):

        # Try to figure out user intent, this function is wrapped in a chainlit step to show thought process on chainlit
        async with cl.Step(name = "Understanding your request...") as step:
            intent = await self.intent_classifier.classify(user_request.user_prompt)
            step.output = f"Intent detected: {intent}"

        # After identifying intent match intent with correct route, this function is wrapped in a chainlit step to show thought process on chainlit
        async with cl.Step(name = "Planning Route...") as step:
            route, target_agent, reason, pipeline_end_at = self.router.determine_route(intent, business_context)
            step.output = f"Route determined: {route} \nReason: {reason}"

        response = await self.agent.get_response(
            message = user_request.user_prompt,
            thread = thread,
            settings = OpenAIChatPromptExecutionSettings()  # Replace with OpenAIChatPromptExecutionSettings(function_choice_behavior=FunctionChoiceBehavior.Auto()) when manager tools implemented
        ) 

        fallback_msg = "I am not sure how to help you with that, could you please provide some more information?"


        return ManagerDecision(
            intent=intent,
            route=route,
            target_agent=target_agent,
            reason=reason,
            pipeline_end_at=pipeline_end_at,
            manager_response=str(response.content) if response.content else fallback_msg
        )

