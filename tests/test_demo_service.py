"""Smoke tests for the demo FastAPI application."""

from fastapi.testclient import TestClient

from k8s_ml_predictive_autoscaling.demo_service.app import app

client = TestClient(app)


def test_health_endpoint_returns_ok() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_metrics_endpoint_exposes_prometheus_text() -> None:
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "demo_service_requests_total" in response.text
