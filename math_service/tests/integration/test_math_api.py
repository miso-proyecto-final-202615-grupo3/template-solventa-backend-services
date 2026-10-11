from fastapi.testclient import TestClient

from src.main import app
from src.presentation.routers import health

client = TestClient(app)


def test_add_numbers_api() -> None:
    response = client.post(
        "/add",
        json={"first_number": 12.5, "second_number": 7.5},
    )

    assert response.status_code == 200
    assert response.json() == {"result": 20.0}


def test_health_check_returns_503_when_response_construction_fails(
    monkeypatch,
) -> None:
    monkeypatch.setattr(health.settings, "VERSION", None)

    response = client.get("/health")

    assert response.status_code == 503
    assert response.json() == {"status": "unhealthy", "version": "unknown"}