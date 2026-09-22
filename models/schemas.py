from pydantic import BaseModel, Field


class RouteRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    max_cost: float = Field(default=0.01, gt=0)
    max_latency_ms: float = Field(default=3000, gt=0)


class RouteResponse(BaseModel):
    provider: str
    model: str
    estimated_cost: float
    estimated_latency_ms: float
    reason: str