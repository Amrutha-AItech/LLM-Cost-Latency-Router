from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_health_check():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["service"] == "LLM Cost-Latency Router"


def test_route_endpoint_success():
    response = client.post(
        "/route",
        json={
            "prompt": "Hello, how are you?",
            "max_cost": 0.01,
            "max_latency_ms": 3000,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["provider"] == "cheap-mock"
    assert data["model"] == "cheap-model"
    assert data["estimated_cost"] == 0.001
    assert data["estimated_latency_ms"] == 250


def test_route_endpoint_constraint_failure():
    response = client.post(
        "/route",
        json={
            "prompt": "Hello",
            "max_cost": 0.0001,
            "max_latency_ms": 50,
        },
    )

    assert response.status_code == 400

    data = response.json()

    assert data["detail"] == (
        "No provider satisfies the cost and latency requirement."
    )