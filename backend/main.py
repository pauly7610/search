from fastapi import FastAPI, WebSocket, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import json
import asyncio
from datetime import datetime
import os

from .database.database import get_db
from .database import models
from . import schemas, crud
from src.services.chat_service import ChatService
from src.services.knowledge_base import KnowledgeBaseService
from .middleware.rate_limit import rate_limit_middleware

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware
app.middleware("http")(rate_limit_middleware)

# Initialize services
chat_service = ChatService()
knowledge_base = KnowledgeBaseService()

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Create conversation if it doesn't exist
            conversation = await crud.create_conversation(
                next(get_db()),
                schemas.ConversationCreate(
                    title=message_data.get("message", "")[:50],
                    user_id=message_data.get("user_id", "anonymous")
                )
            )
            
            # Save user message
            user_message = await crud.create_message(
                next(get_db()),
                schemas.MessageCreate(
                    conversation_id=conversation.id,
                    role="user",
                    content=message_data.get("message", "")
                )
            )
            
            try:
                # Try knowledge base first
                kb_response = await knowledge_base.search(message_data.get("message", ""))
                if kb_response:
                    response = {
                        "type": "message",
                        "content": kb_response,
                        "source": "knowledge_base"
                    }
                else:
                    # Fall back to LLM
                    llm_response = await chat_service.get_response(message_data.get("message", ""))
                    response = {
                        "type": "message",
                        "content": llm_response,
                        "source": "llm"
                    }
            except Exception as e:
                response = {
                    "type": "error",
                    "content": "I apologize, but I'm having trouble processing your request right now. Please try again later."
                }
            
            # Save assistant message
            await crud.create_message(
                next(get_db()),
                schemas.MessageCreate(
                    conversation_id=conversation.id,
                    role="assistant",
                    content=response["content"],
                    source=response.get("source")
                )
            )
            
            await websocket.send_json(response)
            
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
    finally:
        await websocket.close()

# REST endpoints
@app.post("/api/v1/conversations", response_model=schemas.Conversation)
async def create_conversation(
    conversation: schemas.ConversationCreate,
    db: AsyncSession = Depends(get_db)
):
    return await crud.create_conversation(db, conversation)

@app.get("/api/v1/conversations/{user_id}", response_model=List[schemas.Conversation])
async def get_user_conversations(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    return await crud.get_user_conversations(db, user_id)

@app.get("/api/v1/conversations/{conversation_id}/messages", response_model=List[schemas.Message])
async def get_conversation_messages(
    conversation_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await crud.get_conversation_messages(db, conversation_id)

@app.post("/api/v1/analytics", response_model=schemas.AnalyticsEvent)
async def create_analytics_event(
    event: schemas.AnalyticsEventCreate,
    db: AsyncSession = Depends(get_db)
):
    return await crud.create_analytics_event(db, event)

@app.get("/api/v1/analytics/{user_id}", response_model=List[schemas.AnalyticsEvent])
async def get_user_analytics(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    return await crud.get_user_analytics(db, user_id)

@app.post("/api/v1/feedback", response_model=schemas.Feedback)
async def create_feedback(
    feedback: schemas.FeedbackCreate,
    db: AsyncSession = Depends(get_db)
):
    return await crud.create_feedback(db, feedback)

@app.get("/api/v1/feedback/{conversation_id}", response_model=schemas.Feedback)
async def get_conversation_feedback(
    conversation_id: int,
    db: AsyncSession = Depends(get_db)
):
    feedback = await crud.get_conversation_feedback(db, conversation_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return feedback 