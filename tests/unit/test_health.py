"""
Module 04 — health endpoint tests.
Verifies degraded mode when DB is unreachable.
"""
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_ok_when_db_connected():
    with patch("app.api.v1.health.check_db_connection", return_value=True):
        response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["db"] == "connected"


def test_health_degraded_when_db_unreachable():
    with patch("app.api.v1.health.check_db_connection", return_value=False):
        response = client.get("/api/v1/health")
    assert response.status_code == 200          # still returns 200 — not a crash
    assert response.json()["status"] == "degraded"
    assert response.json()["db"] == "unreachable"


def test_health_includes_mode():
    with patch("app.api.v1.health.check_db_connection", return_value=True):
        response = client.get("/api/v1/health")
    assert "mode" in response.json()
