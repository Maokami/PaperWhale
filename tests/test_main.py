from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import pytest

# Import the main app
from app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.mark.asyncio
async def test_slack_events(client):
    with patch("app.main.slack_handler.handle", new_callable=AsyncMock) as mock_handle:
        mock_handle.return_value = {"status": "ok"}

        response = client.post("/slack/events", json={"type": "event_callback"})

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
        mock_handle.assert_called_once()
