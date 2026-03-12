from app.agents.base_agent import Agent

class ContentGeneratorAgent(Agent):
    def __init__(self, kernel):
        super().__init__(kernel=kernel, name="content_generator_agent")

    async def run(self):
        pass
