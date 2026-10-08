import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(async_client: AsyncClient):
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


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
