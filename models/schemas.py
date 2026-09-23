from pydantic import BaseModel


class RouteRequest(BaseModel):
    prompt: str
    max_cost: float
    max_latency_ms: float


class RouteResponse(BaseModel):
    provider: str
    model: str
    estimated_cost: float
    estimated_latency_ms: float
    reason: str