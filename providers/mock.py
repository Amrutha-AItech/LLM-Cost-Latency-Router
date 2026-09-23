from providers.base import LLMProvider


class CheapMockProvider(LLMProvider):

    @property
    def name(self) -> str:
        return "cheap-mock"

    @property
    def model(self) -> str:
        return "cheap-model"

    def generate(self, prompt: str) -> str:
        return "Mock response"

    def estimate_cost(self, prompt: str) -> float:
        return 0.001

    def estimate_latency(self) -> float:
        return 250.0


class MockProvider(LLMProvider):

    @property
    def name(self) -> str:
        return "mock"

    @property
    def model(self) -> str:
        return "mock-model"

    def generate(self, prompt: str) -> str:
        return "Mock response"

    def estimate_cost(self, prompt: str) -> float:
        return 0.003

    def estimate_latency(self) -> float:
        return 700.0