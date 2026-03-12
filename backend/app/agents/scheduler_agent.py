from app.agents.base_agent import Agent

class SchedulerAgent(Agent):
    def __init__(self, kernel):
        super().__init__(kernel=kernel, name="scheduler_agent")

    async def run(self):
        pass