"""Smoke tests for the demo FastAPI application."""

from collections.abc import Callable
from typing import Any

from fastapi.routing import APIRoute

from k8s_ml_predictive_autoscaling.demo_service.app import create_app, get_settings

SETTINGS = get_settings()
app = create_app(SETTINGS)


def _get_endpoint(path: str) -> Callable[[], Any]:
    for route in app.routes:
        if isinstance(route, APIRoute) and route.path == path:
            return route.endpoint
    raise AssertionError(f"Route {path} not found")


def test_health_endpoint_returns_ok() -> None:
    handler = _get_endpoint("/health")
    result = handler()
    assert result == {"status": "ok"}


def test_metrics_endpoint_exposes_prometheus_text() -> None:
    handler = _get_endpoint(SETTINGS.metrics_path)
    response = handler()
    assert response.status_code == 200
    assert "demo_service_requests_total" in response.body.decode()
