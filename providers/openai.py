import os
import time

from dotenv import load_dotenv
from openai import OpenAI

from providers.base import LLMProvider

load_dotenv()


class OpenAIProvider(LLMProvider):

    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )

        # Initial fallback values before the first real request.
        self._latency_ms = 500.0
        self._cost_usd = 0.001

    @property
    def name(self) -> str:
        return "openai"

    @property
    def model(self) -> str:
        return "gpt-5.6-luna"

    def generate(self, prompt: str) -> str:
        start_time = time.perf_counter()

        response = self.client.responses.create(
            model=self.model,
            input=prompt,
        )

        end_time = time.perf_counter()

        # Measure actual request latency.
        self._latency_ms = (end_time - start_time) * 1000

        # Calculate actual request cost from API usage.
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens

        input_cost = input_tokens * 0.20 / 1_000_000
        output_cost = output_tokens * 1.20 / 1_000_000

        self._cost_usd = input_cost + output_cost

        return response.output_text

    def estimate_cost(self, prompt: str) -> float:
        return self._cost_usd

    def estimate_latency(self) -> float:
        return self._latency_ms