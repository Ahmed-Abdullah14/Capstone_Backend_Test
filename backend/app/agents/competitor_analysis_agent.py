from app.agents.base_agent import Agent

class CompetitorAnalysisAgent(Agent):
    def __init__(self, kernel):
        super().__init__(kernel=kernel, name="competitor_analysis_agent")

    async def run(self):
        pass