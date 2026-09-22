from router.router import CostLatencyRouter
from models.schemas import RouteRequest
from providers.mock import MockProvider, CheapMockProvider


def test_cheapest_provider_within_latency():
    router = CostLatencyRouter()

    request = RouteRequest(
        prompt="Hello, how are you?",
        max_cost=0.01,
        max_latency_ms=3000,
    )

    response = router.route(request)

    assert response.provider == "cheap-mock"
    assert response.estimated_cost == 0.001
    assert response.estimated_latency_ms == 250


def test_cheapest_provider_with_latency_constraint():
    router = CostLatencyRouter()

    request = RouteRequest(
        prompt="Hello, how are you?",
        max_cost=0.01,
        max_latency_ms=150,
    )

    response = router.route(request)

    assert response.provider == "mock"
    assert response.estimated_cost == 0.01
    assert response.estimated_latency_ms == 100

def test_no_provider_satisfies_constraints():
    router = CostLatencyRouter()

    request = RouteRequest(
        prompt="Hello, how are you?",
        max_cost=0.0001,
        max_latency_ms=50,
    )

    try:
        router.route(request)
        assert False, "Expected ValueError"
    except ValueError as e:
        assert str(e) == "No provider satisfies the cost and latency requirement."

def test_router_accepts_custom_providers():
    custom_provider = MockProvider()

    router = CostLatencyRouter(providers=[custom_provider])

    request = RouteRequest(
        prompt="Hello",
        max_cost=0.01,
        max_latency_ms=200
    )

    response = router.route(request)

    assert response.provider == "mock"
    assert response.model == "mock-model"

def test_router_falls_back_when_cheapest_provider_fails():

    class FailingCheapProvider(CheapMockProvider):
        def generate(self, prompt: str) -> str:
            raise RuntimeError("Provider temporarily unavailable")

    router = CostLatencyRouter(
        providers=[
            FailingCheapProvider(),
            MockProvider(),
        ]
    )

    request = RouteRequest(
        prompt="Hello",
        max_cost=0.01,
        max_latency_ms=300,
    )

    response = router.route(request)

    assert response.provider == "mock"
    assert response.model == "mock-model"