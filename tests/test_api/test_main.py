from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import pytest

# Import the FastAPI app directly
from app.api.main import app


@pytest.fixture(scope="module")
def client():
    with (
        patch("app.api.main.init_db") as mock_init_db,
        patch(
            "app.api.main.start_scheduler", new_callable=AsyncMock
        ) as mock_start_scheduler,
        patch(
            "app.api.main.shutdown_scheduler", new_callable=AsyncMock
        ) as mock_shutdown_scheduler,
    ):
        with TestClient(app) as c:
            yield c
        mock_init_db.assert_called_once()
        mock_start_scheduler.assert_called_once()
        mock_shutdown_scheduler.assert_called_once()


def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to PaperWhale API!"}
