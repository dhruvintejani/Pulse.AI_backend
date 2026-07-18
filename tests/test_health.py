import os

os.environ.setdefault("ENVIRONMENT", "ci")
os.environ.setdefault("SKIP_DATABASE_INIT", "true")
os.environ.setdefault("SECURITY_ALLOWED_HOSTS", "*")

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_endpoint_returns_service_metadata():
    response = client.get("/")

    assert response.status_code == 200
    payload = response.json()
    assert payload["service"] == "Pulse AI API"
    assert payload["status"] == "ok"
    assert "version" in payload


def test_health_endpoint_returns_ok_status():
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"] == "Pulse AI API"
    assert payload["environment"] in {"development", "test", "ci", "production"}


def test_readiness_endpoint_is_ci_safe():
    response = client.get("/api/v1/health/ready")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ready"
    assert payload["database"] == "connected"
