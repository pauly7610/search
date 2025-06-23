from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import desc
from typing import List, Optional
from uuid import UUID
import uuid

from src.models.chat_models import Conversation, Message

class ChatRepository:
    """Repository for chat-related database operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_conversation(self, user_id: str, session_id: str = None) -> Conversation:
        """Create a new conversation."""
        if not session_id:
            session_id = str(uuid.uuid4())
            
        conversation = Conversation(
            user_id=user_id,
            session_id=session_id,
            status="active"
        )
        self.db.add(conversation)
        await self.db.commit()
        await self.db.refresh(conversation)
        return conversation
    
    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get conversation by ID or session_id."""
        # Try by session_id first
        result = await self.db.execute(
            select(Conversation)
            .options(selectinload(Conversation.messages))
            .where(Conversation.session_id == conversation_id)
        )
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            # Try by UUID if session_id failed
            try:
                uuid_id = UUID(conversation_id)
                result = await self.db.execute(
                    select(Conversation)
                    .options(selectinload(Conversation.messages))
                    .where(Conversation.id == uuid_id)
                )
                conversation = result.scalar_one_or_none()
            except ValueError:
                pass
        
        return conversation
    
    async def get_or_create_conversation(self, conversation_id: str, user_id: str = "anonymous") -> Conversation:
        """Get existing conversation or create new one."""
        conversation = await self.get_conversation(conversation_id)
        if not conversation:
            conversation = await self.create_conversation(user_id, conversation_id)
        return conversation
    
    async def add_message(
        self, 
        conversation_id: str, 
        content: str, 
        sender: str,
        role: str,
        agent: str = None,
        agent_type: str = None,
        answer_type: str = None,
        intent: str = None,
        intent_data: dict = None,
        meta: dict = None
    ) -> Message:
        """Add a message to a conversation."""
        conversation = await self.get_conversation(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        message = Message(
            conversation_id=conversation.id,
            content=content,
            sender=sender,
            role=role,
            agent=agent,
            agent_type=agent_type,
            answer_type=answer_type,
            intent=intent,
            intent_data=intent_data,
            meta=meta
        )
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message
    
    async def get_conversation_messages(
        self, 
        conversation_id: str, 
        limit: int = 50,
        offset: int = 0
    ) -> List[Message]:
        """Get messages for a conversation with pagination."""
        conversation = await self.get_conversation(conversation_id)
        if not conversation:
            return []
        
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .order_by(desc(Message.created_at))
            .limit(limit)
            .offset(offset)
        )
        messages = result.scalars().all()
        return list(reversed(messages))  # Return in chronological order
    
    async def update_conversation_status(self, conversation_id: str, status: str) -> bool:
        """Update conversation status."""
        conversation = await self.get_conversation(conversation_id)
        if not conversation:
            return False
        
        conversation.status = status
        await self.db.commit()
        return True
    
    async def get_user_conversations(self, user_id: str, limit: int = 10) -> List[Conversation]:
        """Get user's recent conversations."""
        result = await self.db.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(desc(Conversation.updated_at))
            .limit(limit)
        )
        return result.scalars().all() 