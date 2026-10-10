from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_add_numbers_api() -> None:
    response = client.post(
        "/add",
        json={"first_number": 12.5, "second_number": 7.5},
    )

    assert response.status_code == 200
    assert response.json() == {"result": 20.0}