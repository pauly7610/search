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
import json
import logging
from openai import OpenAI, RateLimitError

from src.services.chat_service import ChatService
from src.services.conversation_metrics import metrics_collector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize API router with chat endpoints
router = APIRouter()

# In-memory message store for demo purposes
# In production, this would be replaced with a database
MESSAGES = []


class ChatConnectionManager:
    """
    Robust WebSocket connection manager for multi-client chat support.

    This class manages WebSocket connections, handles client identification,
    and provides methods for sending messages to specific clients or
    broadcasting to all connected clients.

    Features:
    - Client identification and tracking
    - Connection state management
    - Error handling for failed connections
    - Graceful disconnection handling
    - Message queuing for offline clients
    """

    def __init__(self):
        # Dictionary to store active WebSocket connections by client ID
        self.active_connections: Dict[str, WebSocket] = {}
        # Track connection metadata for debugging and analytics
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
        # Track last heartbeat time for each connection
        self.last_heartbeat: Dict[str, datetime] = {}
        # Track reconnection attempts for each client
        self.reconnection_attempts: Dict[str, int] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        """
        Accept a new WebSocket connection and register the client.

        Args:
            websocket: WebSocket connection instance
            client_id: Unique identifier for the client
        """
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.connection_metadata[client_id] = {
            "connected_at": datetime.utcnow().isoformat(),
            "message_count": 0,
            "last_activity": datetime.utcnow().isoformat(),
            "client_id": client_id,
        }
        self.last_heartbeat[client_id] = datetime.utcnow()
        self.reconnection_attempts[client_id] = 0
        logger.info(
            f"Client {client_id} connected. Total connections: {len(self.active_connections)}"
        )

    async def disconnect(self, client_id: str):
        """
        Remove a client connection and clean up metadata.

        Args:
            client_id: Unique identifier of the client to disconnect
        """
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.connection_metadata:
            del self.connection_metadata[client_id]
        if client_id in self.last_heartbeat:
            del self.last_heartbeat[client_id]
        # Keep reconnection attempts for potential reconnection
        logger.info(
            f"Client {client_id} disconnected. Total connections: {len(self.active_connections)}"
        )

    async def send_personal_message(self, message: Dict[str, Any], client_id: str):
        """
        Send a message to a specific client with error handling.

        Args:
            message: Message data to send
            client_id: Target client identifier
        """
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            logger.info(
                f"Attempting to send message to client {client_id}, WebSocket state: {websocket.client_state}"
            )
            try:
                logger.info(f"Sending JSON message: {json.dumps(message)[:200]}...")
                await websocket.send_json(message)
                logger.info(
                    f"JSON message sent successfully, checking connection state: {websocket.client_state}"
                )
                # Update activity tracking
                if client_id in self.connection_metadata:
                    self.connection_metadata[client_id][
                        "last_activity"
                    ] = datetime.utcnow().isoformat()
                    self.connection_metadata[client_id]["message_count"] += 1
                logger.info(f"Message successfully sent to client {client_id}")
            except Exception as e:
                logger.error(
                    f"Failed to send message to client {client_id}: {e} (WebSocket state: {websocket.client_state})"
                )
                await self.disconnect(client_id)
        else:
            logger.warning(
                f"Cannot send message to client {client_id}: client not in active connections"
            )

    async def broadcast(self, message: Dict[str, Any]):
        """
        Send a message to all connected clients.

        Args:
            message: Message data to broadcast
        """
        disconnected_clients = []
        for client_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Failed to broadcast to client {client_id}: {e}")
                disconnected_clients.append(client_id)

        # Clean up disconnected clients
        for client_id in disconnected_clients:
            await self.disconnect(client_id)

    async def send_heartbeat(self, client_id: str):
        """
        Send a heartbeat ping to a client to keep the connection alive.

        Args:
            client_id: Target client identifier

        Returns:
            bool: True if heartbeat was sent successfully, False otherwise
        """
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            try:
                await websocket.send_json(
                    {"type": "ping", "timestamp": datetime.utcnow().isoformat()}
                )
                self.last_heartbeat[client_id] = datetime.utcnow()
                logger.debug(f"Heartbeat sent to client {client_id}")
                return True
            except Exception as e:
                logger.error(f"Failed to send heartbeat to client {client_id}: {e}")
                await self.disconnect(client_id)
                return False
        return False

    def get_connection_count(self) -> int:
        """Get the number of active connections."""
        return len(self.active_connections)

    def get_client_metadata(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific client."""
        return self.connection_metadata.get(client_id)

    def update_reconnection_attempts(self, client_id: str, increment: bool = True):
        """
        Update reconnection attempts for a client.

        Args:
            client_id: Client identifier
            increment: Whether to increment (True) or reset (False) the counter
        """
        if increment and client_id in self.reconnection_attempts:
            self.reconnection_attempts[client_id] += 1
        else:
            self.reconnection_attempts[client_id] = 0

    def get_reconnection_attempts(self, client_id: str) -> int:
        """Get the number of reconnection attempts for a client."""
        return self.reconnection_attempts.get(client_id, 0)


# Global connection manager instance
connection_manager = ChatConnectionManager()


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
async def send_message(
    message: Message, chat_service: ChatService = Depends(get_chat_service)
):
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
        id=str(uuid.uuid4()),  # Unique response ID
        content=agent_response["answer"],  # AI-generated response
        role="assistant",  # Mark as assistant message
        timestamp=datetime.utcnow().isoformat(),  # Current timestamp
        agent=agent_response["agent"],  # Agent name
        agent_type=agent_response["agent_type"],  # Agent category
        answer_type=agent_response["answer_type"],  # Response source
        intent=agent_response["intent"],  # Classified intent
        intent_data=agent_response["intent_data"],  # Intent metadata
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
    conversation_id: str, chat_service: ChatService = Depends(get_chat_service)
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


# WebSocket endpoint for real-time chat communication with robust connection management
@router.websocket("/ws/{client_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: str,
    chat_service: ChatService = Depends(get_chat_service),
):
    """
    Enhanced WebSocket endpoint with robust connection management.

    This endpoint implements the recommended WebSocket pattern with:
    - Proper connection management
    - Comprehensive exception handling
    - Client identification
    - Detailed logging
    - Graceful error recovery
    - Heartbeat mechanism

    Args:
        websocket: WebSocket connection instance
        client_id: Unique identifier for the client
        chat_service: Injected chat service instance
    """
    # Connect client using the connection manager
    await connection_manager.connect(websocket, client_id)

    # Use client_id as conversation_id for simplicity
    conversation_id = client_id

    logger.info(f"WebSocket connection established for client {client_id}")

    # Start heartbeat task
    heartbeat_task = asyncio.create_task(
        send_periodic_heartbeat(client_id, 30)  # 30 second interval
    )

    try:
        # Send welcome message
        welcome_message = {
            "id": str(uuid.uuid4()),
            "content": "Hello! I'm your Xfinity support assistant. How can I help you today?",
            "role": "assistant",
            "timestamp": datetime.utcnow().isoformat(),
            "agent": "Support Agent",
            "agent_type": "general",
            "answer_type": "welcome",
            "intent": "greeting",
            "intent_data": {},
        }
        await connection_manager.send_personal_message(welcome_message, client_id)

        # Main message handling loop
        while client_id in connection_manager.active_connections:
            try:
                # Check if WebSocket is still open before attempting to receive
                if websocket.client_state.value != 1:  # 1 = OPEN state
                    logger.info(
                        f"WebSocket for client {client_id} is no longer open (state: {websocket.client_state.value})"
                    )
                    break

                # Wait for message from client
                try:
                    data = await websocket.receive_json()
                except RuntimeError as e:
                    if "disconnect" in str(e).lower():
                        logger.info(f"Client {client_id} disconnected during receive")
                        break
                    raise

                logger.info(
                    f"Received message from client {client_id}: {data.get('content', '')[:50]}..."
                )

                # Handle heartbeat pong response
                if data.get("type") == "pong":
                    logger.debug(f"Received heartbeat pong from client {client_id}")
                    connection_manager.last_heartbeat[client_id] = datetime.utcnow()
                    continue

                # Handle heartbeat ping from client (respond with pong)
                if data.get("type") == "ping":
                    logger.debug(
                        f"Received heartbeat ping from client {client_id}, sending pong"
                    )
                    pong_message = {
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                    await connection_manager.send_personal_message(
                        pong_message, client_id
                    )
                    continue

                # Validate message format
                if not isinstance(data, dict) or "content" not in data:
                    logger.warning(
                        f"Invalid message format from client {client_id}: {data}"
                    )
                    continue

                # Process message through enhanced AI agent system
                logger.info(f"Processing message for client {client_id}")
                agent_response = await chat_service.process_message(
                    conversation_id, data["content"]
                )

                # Track conversation metrics
                if "conversation_metrics" in agent_response:
                    await metrics_collector.track_conversation_quality(
                        client_id, agent_response["conversation_metrics"]
                    )

                # Log high frustration for proactive intervention
                if (
                    agent_response.get("conversation_metrics", {}).get(
                        "frustration_level", 0
                    )
                    >= 6
                ):
                    logger.warning(
                        f"High frustration detected in conversation {client_id}"
                    )

                logger.info(
                    f"Generated response for client {client_id}: {agent_response.get('answer', '')[:50]}..."
                )

                # Send AI response back to client with enhanced metadata
                response_message = {
                    "id": str(uuid.uuid4()),
                    "content": agent_response["answer"],
                    "role": "assistant",
                    "timestamp": datetime.utcnow().isoformat(),
                    "agent": agent_response.get("agent", "Support Agent"),
                    "agent_type": agent_response.get("agent_type", "general"),
                    "answer_type": agent_response.get("answer_type", "kb_response"),
                    "intent": agent_response.get("intent", "general"),
                    "intent_data": agent_response.get("intent_data", {}),
                    # Add conversation flow information
                    "conversation_flow": agent_response.get(
                        "conversation_flow", "standard"
                    ),
                    "is_follow_up": agent_response.get("conversation_metrics", {}).get(
                        "is_follow_up", False
                    ),
                }

                logger.info(f"About to send response message: {response_message}")
                await connection_manager.send_personal_message(
                    response_message, client_id
                )
                logger.info(f"Response sent to client {client_id}")

            except WebSocketDisconnect:
                # WebSocket disconnect during receive - break out of loop
                logger.info(
                    f"Client {client_id} disconnected during message processing"
                )
                break

            except Exception as e:
                # Handle message processing errors gracefully
                logger.error(
                    f"Error processing message for client {client_id}: {str(e)}"
                )

                # Check if the error is related to a disconnected WebSocket
                if "disconnect" in str(e).lower() or "closed" in str(e).lower():
                    logger.info(f"Client {client_id} connection lost during processing")
                    break

                # Determine appropriate error message
                error_message = str(e)
                if "rate limit" in error_message.lower() or "429" in error_message:
                    user_message = "I'm here to help with your Xfinity services. The AI service is temporarily busy, but I can still assist you with information from our knowledge base. What specific issue are you experiencing?"
                elif "insufficient_quota" in error_message.lower():
                    user_message = "I'm here to help with your Xfinity services. I can assist you with internet issues, billing questions, equipment troubleshooting, and general support. What specific problem are you experiencing?"
                else:
                    user_message = "I'm here to help with your Xfinity services. What can I assist you with today?"

                # Send error fallback message
                error_response = {
                    "id": str(uuid.uuid4()),
                    "content": user_message,
                    "role": "assistant",
                    "timestamp": datetime.utcnow().isoformat(),
                    "agent": "Support Agent",
                    "agent_type": "general",
                    "answer_type": "error_fallback",
                    "intent": "general",
                    "intent_data": {},
                }

                try:
                    await connection_manager.send_personal_message(
                        error_response, client_id
                    )
                except Exception as send_error:
                    logger.error(
                        f"Failed to send error message to client {client_id}: {send_error}"
                    )
                    # If we can't send the error message, connection is likely dead
                    break

    except WebSocketDisconnect:
        # Handle client disconnection gracefully
        logger.info(f"Client {client_id} disconnected normally")
        heartbeat_task.cancel()
        await connection_manager.disconnect(client_id)

    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected WebSocket error for client {client_id}: {str(e)}")
        heartbeat_task.cancel()
        await connection_manager.disconnect(client_id)


async def send_periodic_heartbeat(client_id: str, interval: int = 30):
    """
    Send periodic heartbeat pings to keep the connection alive.

    Args:
        client_id: Client identifier
        interval: Heartbeat interval in seconds
    """
    try:
        while client_id in connection_manager.active_connections:
            await asyncio.sleep(interval)
            # Double check connection still exists after sleep
            if client_id not in connection_manager.active_connections:
                logger.debug(f"Client {client_id} disconnected during heartbeat sleep")
                break

            success = await connection_manager.send_heartbeat(client_id)
            if not success:
                logger.debug(
                    f"Heartbeat failed for client {client_id}, stopping heartbeat"
                )
                break

    except asyncio.CancelledError:
        logger.debug(f"Heartbeat task for client {client_id} cancelled")
    except Exception as e:
        logger.error(f"Error in heartbeat task for client {client_id}: {str(e)}")
    finally:
        logger.debug(f"Heartbeat task ending for client {client_id}")


# Legacy WebSocket endpoint for backward compatibility
@router.websocket("/ws")
async def legacy_websocket_endpoint(
    websocket: WebSocket, chat_service: ChatService = Depends(get_chat_service)
):
    """
    Legacy WebSocket endpoint for backward compatibility.

    This endpoint maintains compatibility with existing clients that
    don't provide a client_id. It generates a random client_id and
    forwards to the main WebSocket endpoint.
    """
    # Generate a random client ID for legacy clients
    client_id = str(uuid.uuid4())
    logger.info(f"Legacy WebSocket connection, assigned client_id: {client_id}")

    # Forward to the main WebSocket endpoint
    await websocket_endpoint(websocket, client_id, chat_service)


@router.get("/ws/stats")
async def get_websocket_stats():
    """
    Get WebSocket connection statistics for monitoring and debugging.

    Returns:
        Dict with connection statistics and metadata
    """
    return {
        "active_connections": connection_manager.get_connection_count(),
        "connection_details": {
            client_id: connection_manager.get_client_metadata(client_id)
            for client_id in connection_manager.active_connections.keys()
        },
    }
