"""
Database Models for Authentication and AgentAuth Integration

Compatible with SQLAlchemy 2.0.35 and Pydantic 2.10.2
"""

from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    """User model for authentication compatible with SQLAlchemy 2.0.35."""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to AgentAuth connections
    agent_connections = relationship("AgentConnection", back_populates="user")

class AgentConnection(Base):
    """AgentAuth connection model compatible with SQLAlchemy 2.0.35."""
    __tablename__ = "agent_connections"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    app_name = Column(String(100), nullable=False)
    connection_id = Column(String(255), unique=True, nullable=False)
    connected_account_id = Column(String(255))
    status = Column(String(50), default="pending")  # pending, connected, failed, disconnected
    auth_metadata = Column(JSONB)  # Store additional auth data
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to user
    user = relationship("User", back_populates="agent_connections")

# Pydantic models compatible with Pydantic 2.10.2

class UserCreate(BaseModel):
    """User creation request model compatible with Pydantic 2.10.2."""
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=255)
    password: str = Field(..., min_length=6, max_length=255)
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    """User login request model compatible with Pydantic 2.10.2."""
    email: EmailStr
    password: str
    
    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    """User response model compatible with Pydantic 2.10.2."""
    id: str
    email: str
    name: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class ConnectionRequest(BaseModel):
    """AgentAuth connection request model compatible with Pydantic 2.10.2."""
    app_name: str = Field(..., min_length=1, max_length=100)
    
    class Config:
        from_attributes = True
    
class ConnectionResponse(BaseModel):
    """AgentAuth connection response model compatible with Pydantic 2.10.2."""
    id: str
    app_name: str
    connection_id: str
    connected_account_id: Optional[str] = None
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ActionRequest(BaseModel):
    """Agent action request model compatible with Pydantic 2.10.2."""
    app_name: str
    action_name: str
    parameters: Dict[str, Any] = {}
    
    class Config:
        from_attributes = True

class ActionResponse(BaseModel):
    """Agent action response model compatible with Pydantic 2.10.2."""
    id: str
    app_name: str
    action_name: str
    success: bool
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time_ms: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True 