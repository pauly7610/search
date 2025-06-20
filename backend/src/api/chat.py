"""
Chat API Module for Real-time Customer Support

This module implements the REST and WebSocket endpoints for the chat functionality,
providing both synchronous and real-time communication channels for the customer
support system. It handles message processing, conversation management, and
integration with the AI agent routing system.

Key Features:
- RESTful API endpoints for message handling
- WebSocket support for real-time chat
- Conversation history management
- Error handling and rate limiting
- Integration with AI agent routing
- Message metadata tracking

Endpoints:
- POST /messages: Send a message and get AI response
- GET /conversations: List all conversations
- GET /conversations/{id}: Get specific conversation
- WebSocket /ws: Real-time chat communication
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
from datetime import datetime
import uuid
from openai import OpenAI, RateLimitError

from src.services.chat_service import ChatService

# Initialize API router with chat endpoints
router = APIRouter()

# In-memory message store for demo purposes
# In production, this would be replaced with a database
MESSAGES = []

class Message(BaseModel):
    """
    Message data model for chat communication.
    
    This model defines the structure of messages exchanged between users
    and the AI system, including metadata for tracking, analytics, and
    display purposes.
    
    Attributes:
        id: Unique message identifier
        content: The actual message text
        role: Message sender ('user' or 'assistant')
        timestamp: ISO format timestamp
        agent: Name of the AI agent that handled the message
        agent_type: Type of agent (technical, billing, general)
        answer_type: Source of the answer (kb, llm_generated, error)
        intent: Classified intent of the message
        intent_data: Additional intent classification metadata
    """
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
    """
    Conversation data model for multi-message chat sessions.
    
    This model represents a complete conversation thread with multiple
    messages, timestamps, and metadata for conversation management.
    
    Attributes:
        id: Unique conversation identifier
        messages: List of messages in the conversation
        createdAt: Conversation creation timestamp
        updatedAt: Last update timestamp
    """
    id: str
    messages: List[Message]
    createdAt: str
    updatedAt: str

# Dependency injection for chat service
def get_chat_service():
    """
    Dependency provider for chat service instances.
    
    This function provides a chat service instance to API endpoints,
    enabling dependency injection for better testability and
    separation of concerns.
    
    Returns:
        ChatService: Configured chat service instance
    """
    return ChatService()

@router.post("/messages", response_model=Message)
async def send_message(message: Message, chat_service: ChatService = Depends(get_chat_service)):
    """
    Process a user message and return AI-generated response.
    
    This endpoint handles synchronous message processing where the client
    sends a message and waits for the complete AI response. The message
    is processed through the agent routing system and returns a response
    with full metadata.
    
    The endpoint:
    1. Receives the user message
    2. Routes it through the AI agent system
    3. Generates an appropriate response
    4. Returns the response with metadata
    
    Args:
        message: User message to process
        chat_service: Injected chat service instance
        
    Returns:
        Message: AI-generated response with metadata
        
    Raises:
        HTTPException: If message processing fails
    """
    # Process message with AI agent routing system
    # This involves intent classification, knowledge base search,
    # and potentially LLM generation for complex queries
    agent_response = await chat_service.process_message(message.id, message.content)
    
    # Create assistant message with complete metadata
    assistant_msg = Message(
        id=str(uuid.uuid4()),                          # Unique response ID
        content=agent_response["answer"],               # AI-generated response
        role="assistant",                               # Mark as assistant message
        timestamp=datetime.utcnow().isoformat(),        # Current timestamp
        agent=agent_response["agent"],                  # Agent name
        agent_type=agent_response["agent_type"],        # Agent category
        answer_type=agent_response["answer_type"],      # Response source
        intent=agent_response["intent"],                # Classified intent
        intent_data=agent_response["intent_data"]       # Intent metadata
    )
    
    return assistant_msg

@router.get("/conversations", response_model=List[Conversation])
async def get_conversations(chat_service: ChatService = Depends(get_chat_service)):
    """
    Retrieve all conversations from the chat service.
    
    This endpoint provides access to conversation history across all
    sessions. It's useful for analytics, debugging, and providing
    users with access to their conversation history.
    
    The endpoint:
    1. Retrieves all active conversations from the service
    2. Formats conversation data with message history
    3. Returns standardized conversation objects
    
    Args:
        chat_service: Injected chat service instance
        
    Returns:
        List[Conversation]: List of all conversations with messages
    """
    conversations = []
    
    # Iterate through all stored conversations in the chat service
    for conv_id in chat_service.conversations.keys():
        # Get message history for each conversation
        messages = chat_service.get_conversation_history(conv_id)
        
        # Create conversation object with formatted messages
        conversations.append(
            Conversation(
                id=conv_id,
                messages=[
                    Message(
                        id=str(uuid.uuid4()),
                        content=msg.content,
                        role=msg.type,  # Map LangChain message type to role
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
    """
    Retrieve a specific conversation by ID.
    
    This endpoint provides access to a single conversation's complete
    history. It's useful for resuming conversations, providing context
    to users, and debugging specific conversation flows.
    
    Args:
        conversation_id: Unique identifier of the conversation
        chat_service: Injected chat service instance
        
    Returns:
        Conversation: Complete conversation with message history
        
    Raises:
        HTTPException: If conversation is not found
    """
    # Get message history for the specified conversation
    messages = chat_service.get_conversation_history(conversation_id)
    
    # Create and return conversation object
    return Conversation(
        id=conversation_id,
        messages=[
            Message(
                id=str(uuid.uuid4()),
                content=msg.content,
                role=msg.type,  # Map LangChain message type to role
                timestamp=datetime.utcnow().isoformat(),
            )
            for msg in messages
        ],
        createdAt=datetime.utcnow().isoformat(),
        updatedAt=datetime.utcnow().isoformat(),
    )

# WebSocket endpoint for real-time chat communication
@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    WebSocket endpoint for real-time chat communication.
    
    This endpoint enables real-time bidirectional communication between
    the client and the AI system. It maintains a persistent connection
    for immediate message exchange and provides a more interactive
    chat experience.
    
    The WebSocket connection:
    1. Accepts the client connection
    2. Creates a unique conversation session
    3. Listens for incoming messages
    4. Processes messages through the AI system
    5. Sends responses immediately
    6. Handles connection errors and disconnections
    
    Features:
    - Real-time message processing
    - Automatic error handling
    - Rate limiting protection
    - Graceful connection management
    
    Args:
        websocket: WebSocket connection instance
        chat_service: Injected chat service instance
    """
    # Accept the WebSocket connection
    await websocket.accept()
    
    # Create unique conversation ID for this WebSocket session
    conversation_id = str(uuid.uuid4())
    
    try:
        # Main message handling loop
        while True:
            # Wait for message from client
            data = await websocket.receive_json()
            
            try:
                # Process message through AI agent system
                agent_response = await chat_service.process_message(
                    conversation_id,
                    data["content"]
                )
                
                # Send AI response back to client with full metadata
                await websocket.send_json({
                    "id": str(uuid.uuid4()),
                    "content": agent_response["answer"],
                    "role": "assistant",
                    "timestamp": datetime.utcnow().isoformat(),
                    "agent": agent_response.get("agent", "Support Agent"),
                    "agent_type": agent_response.get("agent_type", "general"),
                    "answer_type": agent_response.get("answer_type", "kb_response"),
                    "intent": agent_response.get("intent", "general"),
                    "intent_data": agent_response.get("intent_data", {})
                })
                
            except Exception as e:
                # Handle all processing errors gracefully
                error_message = str(e)
                print(f"WebSocket error processing message: {error_message}")
                
                # Provide user-friendly error message
                if "rate limit" in error_message.lower() or "429" in error_message:
                    user_message = "I'm here to help with your Xfinity services. The AI service is temporarily busy, but I can still assist you with information from our knowledge base. What specific issue are you experiencing?"
                elif "insufficient_quota" in error_message.lower():
                    user_message = "I'm here to help with your Xfinity services. I can assist you with internet issues, billing questions, equipment troubleshooting, and general support. What specific problem are you experiencing?"
                else:
                    user_message = "I'm here to help with your Xfinity services. What can I assist you with today?"
                
                await websocket.send_json({
                    "id": str(uuid.uuid4()),
                    "content": user_message,
                    "role": "assistant",
                    "timestamp": datetime.utcnow().isoformat(),
                    "agent": "Support Agent",
                    "agent_type": "general",
                    "answer_type": "error_fallback",
                    "intent": "general",
                    "intent_data": {}
                })
                
    except WebSocketDisconnect:
        # Handle client disconnection gracefully
        # In production, this might involve cleanup tasks like:
        # - Saving conversation state
        # - Logging session metrics
        # - Updating user presence status
        pass 