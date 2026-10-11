import pytest
from httpx import AsyncClient

from src.presentation.routers import health


class FailingConnection:
    async def __aenter__(self):
        raise RuntimeError("database unavailable")

    async def __aexit__(self, exc_type, exc_value, traceback):
        return False


@pytest.mark.asyncio
async def test_health_check(async_client: AsyncClient):
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


@pytest.mark.asyncio
async def test_health_check_returns_503_when_database_check_fails(
    async_client: AsyncClient, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(health.engine, "connect", lambda: FailingConnection())

    response = await async_client.get("/health")

    assert response.status_code == 503
    assert response.json()["status"] == "unhealthy"


@pytest.mark.asyncio
async def test_create_and_list_greetings_api(async_client: AsyncClient):
    payload = {"message": "¡Hola desde integración!", "language": "es"}
    response = await async_client.post("/greetings/", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["message"] == payload["message"]
    assert data["language"] == payload["language"]
    assert "id" in data
    greeting_id = data["id"]

    response_list = await async_client.get("/greetings/")
    assert response_list.status_code == 200
    greetings = response_list.json()

    assert len(greetings) == 1
    assert greetings[0]["id"] == greeting_id
    assert greetings[0]["message"] == "¡Hola desde integración!"
