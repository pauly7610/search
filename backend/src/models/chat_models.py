from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from src.config.database import Base

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), nullable=False)
    session_id = Column(String(255), unique=True, nullable=False)
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"))
    sender = Column(String(50), nullable=False)  # 'user' or 'agent'
    content = Column(Text, nullable=False)
    meta = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    agent = Column(String, nullable=True)
    agent_type = Column(String, nullable=True)
    answer_type = Column(String, nullable=True)
    intent = Column(String, nullable=True)
    intent_data = Column(JSON, nullable=True)
    conversation = relationship("Conversation", back_populates="messages") 