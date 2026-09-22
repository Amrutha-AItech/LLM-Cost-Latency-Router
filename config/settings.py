import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = "LLM Cost Latency Router"
APP_VERSION = "1.0.0"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

DEFAULT_TIMEOUT = float(os.getenv("DEFAULT_TIMEOUT", "10"))

MAX_COST_PER_REQUEST = float(
    os.getenv("MAX_COST_PER_REQUEST", "0.01")
)

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()