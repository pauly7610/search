import pytest
from httpx import AsyncClient
from backend.src.main import app

@pytest.mark.asyncio
async def test_submit_feedback():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        payload = {
            "conversation_id": "test-conv",
            "message_id": "msg-1",
            "rating": 5,
            "comment": "Great answer!"
        }
        response = await ac.post("/api/v1/feedback/submit", json=payload)
        assert response.status_code == 200
        assert response.json()["status"] == "received"

@pytest.mark.asyncio
async def test_submit_feedback_root():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        payload = {
            "conversation_id": "test-conv",
            "message_id": "msg-2",
            "rating": 4,
            "comment": "Pretty good."
        }
        response = await ac.post("/api/v1/feedback/", json=payload)
        assert response.status_code == 200
        assert response.json()["status"] == "received" 