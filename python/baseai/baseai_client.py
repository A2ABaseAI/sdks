from .api import agents, threads
from .agent import BaseAIAgent
from .thread import BaseAIThread


class BaseAI:
    def __init__(self, api_key: str, api_url: str = "https://a2abase.ai"):
        self._agents_client = agents.create_agents_client(api_url, api_key)
        self._threads_client = threads.create_threads_client(api_url, api_key)

        self.Agent = BaseAIAgent(self._agents_client)
        self.Thread = BaseAIThread(self._threads_client)

