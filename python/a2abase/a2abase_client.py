from .api import agents, threads
from .agent import A2ABaseAgent
from .thread import A2ABaseThread


class A2ABaseClient:
    def __init__(self, api_key: str, api_url: str = "https://a2abase.ai"):
        self._agents_client = agents.create_agents_client(api_url, api_key)
        self._threads_client = threads.create_threads_client(api_url, api_key)

        self.Agent = A2ABaseAgent(self._agents_client)
        self.Thread = A2ABaseThread(self._threads_client)


