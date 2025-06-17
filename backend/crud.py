from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from typing import List, Optional
from . import models, schemas

# Conversation CRUD
async def create_conversation(db: AsyncSession, conversation: schemas.ConversationCreate) -> models.Conversation:
    db_conversation = models.Conversation(**conversation.model_dump())
    db.add(db_conversation)
    await db.commit()
    await db.refresh(db_conversation)
    return db_conversation

async def get_conversation(db: AsyncSession, conversation_id: int) -> Optional[models.Conversation]:
    result = await db.execute(
        select(models.Conversation)
        .options(selectinload(models.Conversation.messages))
        .where(models.Conversation.id == conversation_id)
    )
    return result.scalar_one_or_none()

async def get_user_conversations(db: AsyncSession, user_id: str) -> List[models.Conversation]:
    result = await db.execute(
        select(models.Conversation)
        .where(models.Conversation.user_id == user_id)
        .order_by(models.Conversation.updated_at.desc())
    )
    return result.scalars().all()

# Message CRUD
async def create_message(db: AsyncSession, message: schemas.MessageCreate) -> models.Message:
    db_message = models.Message(**message.model_dump())
    db.add(db_message)
    await db.commit()
    await db.refresh(db_message)
    return db_message

async def get_conversation_messages(db: AsyncSession, conversation_id: int) -> List[models.Message]:
    result = await db.execute(
        select(models.Message)
        .where(models.Message.conversation_id == conversation_id)
        .order_by(models.Message.created_at)
    )
    return result.scalars().all()

# Analytics CRUD
async def create_analytics_event(db: AsyncSession, event: schemas.AnalyticsEventCreate) -> models.AnalyticsEvent:
    db_event = models.AnalyticsEvent(**event.model_dump())
    db.add(db_event)
    await db.commit()
    await db.refresh(db_event)
    return db_event

async def get_user_analytics(db: AsyncSession, user_id: str) -> List[models.AnalyticsEvent]:
    result = await db.execute(
        select(models.AnalyticsEvent)
        .where(models.AnalyticsEvent.user_id == user_id)
        .order_by(models.AnalyticsEvent.created_at.desc())
    )
    return result.scalars().all()

# Feedback CRUD
async def create_feedback(db: AsyncSession, feedback: schemas.FeedbackCreate) -> models.Feedback:
    db_feedback = models.Feedback(**feedback.model_dump())
    db.add(db_feedback)
    await db.commit()
    await db.refresh(db_feedback)
    return db_feedback

async def get_conversation_feedback(db: AsyncSession, conversation_id: int) -> Optional[models.Feedback]:
    result = await db.execute(
        select(models.Feedback)
        .where(models.Feedback.conversation_id == conversation_id)
    )
    return result.scalar_one_or_none() 