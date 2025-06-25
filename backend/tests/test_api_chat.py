import pytest
from httpx import AsyncClient
from backend.src.main import app


@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


@pytest.mark.asyncio
async def test_send_message_kb(monkeypatch):
    # Mock ChatService to always return a KB answer
    from backend.src.api.chat import get_chat_service

    class DummyChatService:
        async def process_message(self, conversation_id, message):
            return {
                "answer": "KB answer",
                "agent": "Tech Support",
                "agent_type": "tech_support",
                "answer_type": "kb",
                "intent": "technical_support",
                "intent_data": {},
            }

    monkeypatch.setattr(
        "backend.src.api.chat.get_chat_service", lambda: DummyChatService()
    )
    async with AsyncClient(app=app, base_url="http://test") as ac:
        payload = {
            "id": "test-conv",
            "content": "modem reset",
            "role": "user",
            "timestamp": "2024-01-01T00:00:00Z",
        }
        response = await ac.post("/api/v1/chat/messages", json=payload)
        assert response.status_code == 200
        assert response.json()["content"] == "KB answer"


@pytest.mark.asyncio
async def test_get_conversations():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/chat/conversations")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


# WebSocket test structure (full test would require more setup)
def test_websocket_endpoint_structure():
    # Placeholder for WebSocket test
    pass
