from providers.base import LLMProvider


class MockProvider(LLMProvider):

    @property
    def name(self) -> str:
        return "mock"

    @property
    def model(self) -> str:
        return "mock-model"

    def generate(self, prompt: str) -> str:
        return f"Mock response for: {prompt}"

    def estimate_cost(self, prompt: str) -> float:
        return 0.01

    def estimate_latency(self) -> float:
        return 100.0


class CheapMockProvider(LLMProvider):

    @property
    def name(self) -> str:
        return "cheap-mock"

    @property
    def model(self) -> str:
        return "cheap-model"

    def generate(self, prompt: str) -> str:
        return f"Cheap mock response for: {prompt}"

    def estimate_cost(self, prompt: str) -> float:
        return 0.001

    def estimate_latency(self) -> float:
        return 250.0