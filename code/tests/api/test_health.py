from fastapi.testclient import TestClient

from backend.main import app


def test_health_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "timestamp" in body
    assert body["uptime_seconds"] >= 0
    assert body["database"]["status"] == "ok"
    assert body["database"]["backend"]


def test_health_endpoint_returns_request_id_header() -> None:
    client = TestClient(app)
    response = client.get("/health", headers={"x-request-id": "demo-request-id"})

    assert response.status_code == 200
    assert response.headers["x-request-id"] == "demo-request-id"


def test_metrics_endpoint_reports_runtime_counters() -> None:
    client = TestClient(app)

    health_response = client.get("/health")
    assert health_response.status_code == 200

    metrics_response = client.get("/metrics", headers={"Authorization": "Bearer demo-employee-token"})

    assert metrics_response.status_code == 200
    assert "buildathon_uptime_seconds" in metrics_response.text
    assert "buildathon_requests_total" in metrics_response.text
    assert "buildathon_database_up 1" in metrics_response.text
