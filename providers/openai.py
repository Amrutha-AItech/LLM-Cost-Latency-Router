import os
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from providers.base import LLMProvider


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class OpenAIProvider(LLMProvider):

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError("OPENAI_API_KEY is not configured.")

        self.client = OpenAI(api_key=api_key)

        self._cost_usd = 0.001
        self._latency_ms = 500.0

    @property
    def name(self) -> str:
        return "openai"

    @property
    def model(self) -> str:
        return "gpt-5.6-luna"

    def generate(self, prompt: str) -> str:
        start = time.perf_counter()

        response = self.client.responses.create(
            model=self.model,
            input=prompt,
        )

        self._latency_ms = (
            time.perf_counter() - start
        ) * 1000

        return response.output_text

    def estimate_cost(self, prompt: str) -> float:
        return self._cost_usd

    def estimate_latency(self) -> float:
        return self._latency_ms