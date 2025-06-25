import pytest
from httpx import AsyncClient
from backend.src.main import app


@pytest.mark.asyncio
async def test_get_knowledge_base():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/knowledge/")
        assert response.status_code == 200
        assert "articles" in response.json()


@pytest.mark.asyncio
async def test_search_knowledge_base():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/knowledge/?q=modem")
        assert response.status_code == 200
        assert "articles" in response.json()
