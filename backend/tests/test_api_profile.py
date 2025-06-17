import pytest
from httpx import AsyncClient
from backend.src.main import app

@pytest.mark.asyncio
async def test_get_profile():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/user/profile")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data and "name" in data

@pytest.mark.asyncio
async def test_update_profile():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        payload = {
            "id": "user-1",
            "name": "Updated User",
            "email": "updated@example.com",
            "avatar_url": "https://api.dicebear.com/6.x/identicon/svg?seed=updated",
            "bio": "Updated bio."
        }
        response = await ac.put("/api/v1/user/profile", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated User" 