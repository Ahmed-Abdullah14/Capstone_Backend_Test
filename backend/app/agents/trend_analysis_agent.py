from app.agents.base_agent import Agent

class TrendAnalysisAgent(Agent):
    def __init__(self, kernel):
        super().__init__(kernel=kernel, name="trend_analysis_agent")

    async def run(self):
        pass
