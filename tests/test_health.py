import os

os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "database" in data
    assert "uptime_seconds" in data
