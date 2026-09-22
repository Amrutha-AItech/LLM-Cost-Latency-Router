import logging

from fastapi import FastAPI, HTTPException

from models.schemas import RouteRequest, RouteResponse
from router.router import CostLatencyRouter
from config.settings import LOG_LEVEL


# ---------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------

app = FastAPI(
    title="LLM Cost-Latency Router",
    version="1.0.0",
    description=(
        "Routes LLM requests to the cheapest eligible provider "
        "that satisfies the requested cost and latency limits."
    ),
)


# ---------------------------------------------------------
# Router instance
# ---------------------------------------------------------

router = CostLatencyRouter()


# ---------------------------------------------------------
# Root / Health Check
# ---------------------------------------------------------

@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "LLM Cost-Latency Router",
    }


@app.get(
    "/health",
    summary="Health Check",
)
def health_check():
    return {
        "status": "ok",
        "service": "LLM Cost-Latency Router",
    }


# ---------------------------------------------------------
# Route LLM request
# ---------------------------------------------------------

@app.post(
    "/route",
    response_model=RouteResponse,
    summary="Route an LLM request",
    description=(
        "Selects the cheapest eligible LLM provider "
        "that satisfies the requested cost and latency limits."
    ),
)
def route_request(request: RouteRequest):
    try:
        response = router.route(request)

        logger.info(
            "Request routed successfully | provider=%s | model=%s | "
            "cost=%s | latency_ms=%s",
            response.provider,
            response.model,
            response.estimated_cost,
            response.estimated_latency_ms,
        )

        return response

    except ValueError as exc:
        logger.warning("Routing failed: %s", exc)

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception:
        logger.exception("Unexpected error while routing request")

        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )

# ---------------------------------------------------------
# Run directly with: python main.py
# ---------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )