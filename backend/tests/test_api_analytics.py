import pytest
from httpx import AsyncClient
from backend.src.main import app

@pytest.mark.asyncio
async def test_analytics_overview():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/analytics/overview")
        assert response.status_code == 200
        assert "totalConversations" in response.json()

@pytest.mark.asyncio
async def test_conversation_volume():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/analytics/conversation-volume")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_response_time_trend():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/analytics/response-time")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_satisfaction_trend():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/analytics/satisfaction")
        assert response.status_code == 200
        assert isinstance(response.json(), list) 