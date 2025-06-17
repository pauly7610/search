from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Conversation schemas
class ConversationBase(BaseModel):
    title: str
    user_id: str

class ConversationCreate(ConversationBase):
    pass

class Conversation(ConversationBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    is_active: bool

    class Config:
        from_attributes = True

# Message schemas
class MessageBase(BaseModel):
    role: str
    content: str
    conversation_id: int
    tokens_used: Optional[int] = None
    source: Optional[str] = None

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Analytics schemas
class AnalyticsEventBase(BaseModel):
    event_type: str
    user_id: str
    data: str

class AnalyticsEventCreate(AnalyticsEventBase):
    pass

class AnalyticsEvent(AnalyticsEventBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Feedback schemas
class FeedbackBase(BaseModel):
    conversation_id: int
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None

class FeedbackCreate(FeedbackBase):
    pass

class Feedback(FeedbackBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True 