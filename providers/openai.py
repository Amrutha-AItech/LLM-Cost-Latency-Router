import os

from dotenv import load_dotenv
from openai import OpenAI

from providers.base import LLMProvider

load_dotenv()


class OpenAIProvider(LLMProvider):
 
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )

    @property
    def name(self) -> str:
        return "openai"

    @property
    def model(self) -> str:
        return "gpt-5.6-luna"

    def generate(self, prompt: str) -> str:
        response = self.client.responses.create(
            model=self.model,
            input=prompt,
        )

        return response.output_text

    def estimate_cost(self, prompt: str) -> float:
        # Temporary estimate.
        # We will implement real cost calculation later.
        return 0.001

    def estimate_latency(self) -> float:
        # Temporary estimate.
        # We will replace this with measured latency later.
        return 500.0