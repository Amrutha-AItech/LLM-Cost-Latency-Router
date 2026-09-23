import pytest

from models.schemas import RouteRequest
from router import CostLatencyRouter


# ============================================================
# Test Provider
# ============================================================

class FakeProvider:

    def __init__(
        self,
        name="fake",
        model="fake-model",
        cost=0.001,
        latency=500.0,
        response="Hello!",
        should_fail=False,
        fail_during_estimation=False,
    ):
        self._name = name
        self._model = model
        self._cost = cost
        self._latency = latency
        self._response = response
        self._should_fail = should_fail
        self._fail_during_estimation = fail_during_estimation

        self.generate_called = False

    @property
    def name(self) -> str:
        return self._name

    @property
    def model(self) -> str:
        return self._model

    def estimate_cost(self, prompt: str) -> float:
        if self._fail_during_estimation:
            raise RuntimeError("Cost estimation failed")

        return self._cost

    def estimate_latency(self) -> float:
        if self._fail_during_estimation:
            raise RuntimeError("Latency estimation failed")

        return self._latency

    def generate(self, prompt: str) -> str:
        self.generate_called = True

        if self._should_fail:
            raise RuntimeError("Generation failed")

        return self._response


# ============================================================
# 1. Cheapest eligible provider should be selected
# ============================================================

def test_cheapest_provider_is_selected():

    expensive = FakeProvider(
        name="expensive",
        model="expensive-model",
        cost=0.01,
        latency=500.0,
    )

    cheap = FakeProvider(
        name="cheap",
        model="cheap-model",
        cost=0.001,
        latency=500.0,
    )

    router = CostLatencyRouter(
        providers=[expensive, cheap]
    )

    request = RouteRequest(
        prompt="Hello",
        max_cost=0.02,
        max_latency_ms=1000,
    )

    response = router.route(request)

    assert response.provider == "cheap"
    assert response.model == "cheap-model"
    assert response.estimated_cost == 0.001


# ============================================================
# 2. Latency constraint should be respected
# ============================================================

def test_latency_constraint():

    slow = FakeProvider(
        name="slow",
        model="slow-model",
        cost=0.0001,
        latency=5000.0,
    )

    fast = FakeProvider(
        name="fast",
        model="fast-model",
        cost=0.001,
        latency=300.0,
    )

    router = CostLatencyRouter(
        providers=[slow, fast]
    )

    request = RouteRequest(
        prompt="Hello",
        max_cost=0.01,
        max_latency_ms=1000,
    )

    response = router.route(request)

    assert response.provider == "fast"
    assert response.model == "fast-model"


# ============================================================
# 3. No provider satisfies constraints
# ============================================================

def test_no_provider_satisfies_constraints():

    expensive = FakeProvider(
        name="expensive",
        model="expensive-model",
        cost=1.0,
        latency=5000.0,
    )

    router = CostLatencyRouter(
        providers=[expensive]
    )

    request = RouteRequest(
        prompt="Hello",
        max_cost=0.001,
        max_latency_ms=1000,
    )

    with pytest.raises(
        ValueError,
        match="No provider satisfies",
    ):
        router.route(request)

    # Generation should never happen because
    # the provider was not eligible.
    assert expensive.generate_called is False


# ============================================================
# 4. Router should fall back when cheapest provider fails
# ============================================================

def test_fallback_when_cheapest_provider_fails():

    failing = FakeProvider(
        name="cheap-failing",
        model="cheap-model",
        cost=0.001,
        latency=500.0,
        should_fail=True,
    )

    backup = FakeProvider(
        name="backup",
        model="backup-model",
        cost=0.005,
        latency=600.0,
    )

    router = CostLatencyRouter(
        providers=[failing, backup]
    )

    request = RouteRequest(
        prompt="Hello",
        max_cost=0.01,
        max_latency_ms=1000,
    )

    response = router.route(request)

    assert failing.generate_called is True
    assert backup.generate_called is True

    assert response.provider == "backup"
    assert response.model == "backup-model"


# ============================================================
# 5. All eligible providers fail during generation
# ============================================================

def test_all_eligible_providers_fail():

    provider_one = FakeProvider(
        name="provider-one",
        model="model-one",
        cost=0.001,
        latency=500.0,
        should_fail=True,
    )

    provider_two = FakeProvider(
        name="provider-two",
        model="model-two",
        cost=0.002,
        latency=600.0,
        should_fail=True,
    )

    router = CostLatencyRouter(
        providers=[provider_one, provider_two]
    )

    request = RouteRequest(
        prompt="Hello",
        max_cost=0.01,
        max_latency_ms=1000,
    )

    with pytest.raises(
        ValueError,
        match="All eligible providers failed",
    ):
        router.route(request)

    assert provider_one.generate_called is True
    assert provider_two.generate_called is True


# ============================================================
# 6. Provider failing during estimation should be skipped
# ============================================================

def test_provider_estimation_failure_is_skipped():

    broken = FakeProvider(
        name="broken",
        model="broken-model",
        cost=0.001,
        latency=500.0,
        fail_during_estimation=True,
    )

    working = FakeProvider(
        name="working",
        model="working-model",
        cost=0.005,
        latency=600.0,
    )

    router = CostLatencyRouter(
        providers=[broken, working]
    )

    request = RouteRequest(
        prompt="Hello",
        max_cost=0.01,
        max_latency_ms=1000,
    )

    response = router.route(request)

    assert response.provider == "working"
    assert response.model == "working-model"

    assert broken.generate_called is False
    assert working.generate_called is True


# ============================================================
# 7. Custom providers should be accepted by the router
# ============================================================

def test_custom_provider_list():

    custom = FakeProvider(
        name="custom",
        model="custom-model",
        cost=0.002,
        latency=400.0,
    )

    router = CostLatencyRouter(
        providers=[custom]
    )

    request = RouteRequest(
        prompt="Test custom provider",
        max_cost=0.01,
        max_latency_ms=1000,
    )

    response = router.route(request)

    assert response.provider == "custom"
    assert response.model == "custom-model"
    assert response.estimated_cost == 0.002
    assert response.estimated_latency_ms == 400.0


# ============================================================
# 8. Response should contain correct routing information
# ============================================================

def test_route_response_contains_correct_information():

    provider = FakeProvider(
        name="test-provider",
        model="test-model",
        cost=0.003,
        latency=700.0,
    )

    router = CostLatencyRouter(
        providers=[provider]
    )

    request = RouteRequest(
        prompt="Explain APIs",
        max_cost=0.01,
        max_latency_ms=1000,
    )

    response = router.route(request)

    assert response.provider == "test-provider"
    assert response.model == "test-model"
    assert response.estimated_cost == 0.003
    assert response.estimated_latency_ms == 700.0

    assert (
        "Cheapest eligible provider selected"
        in response.reason
    )