from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
from datetime import datetime
import uuid
from openai.error import RateLimitError

from services.chat_service import ChatService

router = APIRouter()

# In-memory message store for demo
MESSAGES = []

class Message(BaseModel):
    id: str
    content: str
    role: str  # 'user' or 'assistant'
    timestamp: str
    agent: Optional[str] = None
    agent_type: Optional[str] = None
    answer_type: Optional[str] = None
    intent: Optional[str] = None
    intent_data: Optional[Dict[str, Any]] = None

class Conversation(BaseModel):
    id: str
    messages: List[Message]
    createdAt: str
    updatedAt: str

# Dependency to get chat service
def get_chat_service():
    return ChatService()

@router.post("/messages", response_model=Message)
async def send_message(message: Message, chat_service: ChatService = Depends(get_chat_service)):
    # Process message with AI agent routing
    agent_response = await chat_service.process_message(message.id, message.content)
    assistant_msg = Message(
        id=str(uuid.uuid4()),
        content=agent_response["answer"],
        role="assistant",
        timestamp=datetime.utcnow().isoformat(),
        agent=agent_response["agent"],
        agent_type=agent_response["agent_type"],
        answer_type=agent_response["answer_type"],
        intent=agent_response["intent"],
        intent_data=agent_response["intent_data"]
    )
    return assistant_msg

@router.get("/conversations", response_model=List[Conversation])
async def get_conversations(chat_service: ChatService = Depends(get_chat_service)):
    # Get all conversations from the service
    conversations = []
    for conv_id in chat_service.conversations.keys():
        messages = chat_service.get_conversation_history(conv_id)
        conversations.append(
            Conversation(
                id=conv_id,
                messages=[
                    Message(
                        id=str(uuid.uuid4()),
                        content=msg.content,
                        role=msg.type,
                        timestamp=datetime.utcnow().isoformat(),
                    )
                    for msg in messages
                ],
                createdAt=datetime.utcnow().isoformat(),
                updatedAt=datetime.utcnow().isoformat(),
            )
        )
    return conversations

@router.get("/conversations/{conversation_id}", response_model=Conversation)
async def get_conversation(
    conversation_id: str,
    chat_service: ChatService = Depends(get_chat_service)
):
    messages = chat_service.get_conversation_history(conversation_id)
    return Conversation(
        id=conversation_id,
        messages=[
            Message(
                id=str(uuid.uuid4()),
                content=msg.content,
                role=msg.type,
                timestamp=datetime.utcnow().isoformat(),
            )
            for msg in messages
        ],
        createdAt=datetime.utcnow().isoformat(),
        updatedAt=datetime.utcnow().isoformat(),
    )

# WebSocket for real-time chat
@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    chat_service: ChatService = Depends(get_chat_service)
):
    await websocket.accept()
    conversation_id = str(uuid.uuid4())
    
    try:
        while True:
            data = await websocket.receive_json()
            try:
                agent_response = await chat_service.process_message(
                    conversation_id,
                    data["content"]
                )
                await websocket.send_json({
                    "id": str(uuid.uuid4()),
                    "content": agent_response["answer"],
                    "role": "assistant",
                    "timestamp": datetime.utcnow().isoformat(),
                    "agent": agent_response["agent"],
                    "agent_type": agent_response["agent_type"],
                    "answer_type": agent_response["answer_type"],
                    "intent": agent_response["intent"],
                    "intent_data": agent_response["intent_data"]
                })
            except RateLimitError:
                await websocket.send_json({
                    "id": str(uuid.uuid4()),
                    "content": "Sorry, the AI service is currently unavailable due to usage limits. Please try again later.",
                    "role": "assistant",
                    "timestamp": datetime.utcnow().isoformat(),
                })
            except Exception as e:
                await websocket.send_json({
                    "id": str(uuid.uuid4()),
                    "content": f"An error occurred: {str(e)}",
                    "role": "assistant",
                    "timestamp": datetime.utcnow().isoformat(),
                })
    except WebSocketDisconnect:
        pass 