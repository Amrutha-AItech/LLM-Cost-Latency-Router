from abc import ABC, abstractmethod


class LLMProvider(ABC):

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate a response from the LLM."""
        pass

    @abstractmethod
    def estimate_cost(self, prompt: str) -> float:
        """Estimate the cost of processing a prompt."""
        pass

    @abstractmethod
    def estimate_latency(self) -> float:
        """Estimate the expected latency in milliseconds."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the provider name."""
        pass

    @property
    @abstractmethod
    def model(self) -> str:
        """Return the model name."""
        pass