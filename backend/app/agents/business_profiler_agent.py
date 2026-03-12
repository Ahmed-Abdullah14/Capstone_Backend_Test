from app.agents.base_agent import Agent

class BusinessProfilerAgent(Agent):
    def __init__(self, kernel):
        super().__init__(kernel=kernel, name="business_profiler_agent")

    async def run(self):
        pass
