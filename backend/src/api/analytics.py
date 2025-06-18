from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from typing import List
import os
import json
from collections import Counter, defaultdict
from sqlalchemy import select, func, desc, asc, cast, Date
from src.config.database import get_db
from src.models.chat_models import Conversation, Message
from src.models.feedback_models import Feedback
from src.models.knowledge_models import KnowledgeBase
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from fastapi.responses import StreamingResponse, JSONResponse
import csv
from io import StringIO

router = APIRouter()

class ConversationVolume(BaseModel):
    date: str
    conversations: int

class ResponseTimeTrend(BaseModel):
    date: str
    responseTime: float

class SatisfactionTrend(BaseModel):
    date: str
    satisfaction: int

class Analytics(BaseModel):
    totalConversations: int
    averageResponseTime: str
    satisfactionRate: str
    activeUsers: int
    conversationVolume: List[ConversationVolume]
    responseTimeTrend: List[ResponseTimeTrend]
    satisfactionTrend: List[SatisfactionTrend]

KB_PATH = os.path.join(os.path.dirname(__file__), '../xfinity_knowledge_base.json')

def load_kb_responses():
    with open(KB_PATH, 'r', encoding='utf-8') as f:
        kb = json.load(f)['knowledge_base']['agents']
    responses = []
    for agent, agent_data in kb.items():
        for category, cat_data in agent_data.get('categories', {}).items():
            for resp in cat_data.get('responses', []):
                responses.append(resp)
    return responses

@router.get("/overview", response_model=Analytics)
async def get_analytics_overview(db: AsyncSession = Depends(get_db)):
    # Total conversations
    total_convs = (await db.execute(select(func.count(Conversation.id)))).scalar()
    # Active users (unique user_id)
    active_users = (await db.execute(select(func.count(func.distinct(Conversation.user_id))))).scalar()
    # Average response time (difference between consecutive messages in a conversation, agent replies only)
    msg_stmt = select(Message).order_by(Message.conversation_id, Message.created_at)
    msgs = (await db.execute(msg_stmt)).scalars().all()
    response_times = []
    last_user_msg = {}
    for msg in msgs:
        if msg.role == 'user':
            last_user_msg[msg.conversation_id] = msg.created_at
        elif msg.role == 'assistant' and msg.conversation_id in last_user_msg:
            delta = (msg.created_at - last_user_msg[msg.conversation_id]).total_seconds()
            if 0 < delta < 3600:  # Ignore outliers
                response_times.append(delta)
            last_user_msg.pop(msg.conversation_id)
    avg_response_time = f"{(sum(response_times)/len(response_times)):.1f}s" if response_times else "0s"
    # Satisfaction rate (average feedback rating)
    avg_rating = (await db.execute(select(func.avg(Feedback.rating)))).scalar()
    satisfaction_rate = f"{(avg_rating*20):.0f}%" if avg_rating else "0%"
    # Trends
    conv_trend = await get_conversation_volume(db=db)
    resp_trend = await get_response_time_trend(db=db)
    sat_trend = await get_satisfaction_trend(db=db)
    return Analytics(
        totalConversations=total_convs or 0,
        averageResponseTime=avg_response_time,
        satisfactionRate=satisfaction_rate,
        activeUsers=active_users or 0,
        conversationVolume=conv_trend,
        responseTimeTrend=resp_trend,
        satisfactionTrend=sat_trend
    )

@router.get("/conversation-volume", response_model=List[ConversationVolume])
async def get_conversation_volume(db: AsyncSession = Depends(get_db)):
    stmt = select(cast(Conversation.created_at, Date), func.count(Conversation.id)).group_by(cast(Conversation.created_at, Date)).order_by(cast(Conversation.created_at, Date))
    result = await db.execute(stmt)
    return [
        {"date": str(row[0]), "conversations": row[1]} for row in result.all()
    ]

@router.get("/response-time", response_model=List[ResponseTimeTrend])
async def get_response_time_trend(db: AsyncSession = Depends(get_db)):
    # Calculate average response time per day
    msg_stmt = select(Message).order_by(Message.conversation_id, Message.created_at)
    msgs = (await db.execute(msg_stmt)).scalars().all()
    resp_times_by_date = defaultdict(list)
    last_user_msg = {}
    for msg in msgs:
        if msg.role == 'user':
            last_user_msg[msg.conversation_id] = msg.created_at
        elif msg.role == 'assistant' and msg.conversation_id in last_user_msg:
            delta = (msg.created_at - last_user_msg[msg.conversation_id]).total_seconds()
            if 0 < delta < 3600:
                resp_times_by_date[msg.created_at.date()].append(delta)
            last_user_msg.pop(msg.conversation_id)
    return [
        {"date": str(date), "responseTime": sum(times)/len(times) if times else 0}
        for date, times in sorted(resp_times_by_date.items())
    ]

@router.get("/satisfaction", response_model=List[SatisfactionTrend])
async def get_satisfaction_trend(db: AsyncSession = Depends(get_db)):
    stmt = select(cast(Feedback.timestamp, Date), func.avg(Feedback.rating)).group_by(cast(Feedback.timestamp, Date)).order_by(cast(Feedback.timestamp, Date))
    result = await db.execute(stmt)
    return [
        {"date": str(row[0]), "satisfaction": int(row[1]) if row[1] is not None else 0} for row in result.all()
    ]

@router.get("/kb-intents")
def kb_intent_stats():
    responses = load_kb_responses()
    intent_counter = Counter()
    for resp in responses:
        for tag in resp.get('intent_tags', []):
            intent_counter[tag] += 1
    return dict(intent_counter)

@router.get("/kb-difficulty")
def kb_difficulty_stats():
    responses = load_kb_responses()
    diff_counter = Counter()
    for resp in responses:
        diff = resp.get('difficulty_level', 'unknown')
        diff_counter[diff] += 1
    return dict(diff_counter)

@router.get("/kb-popularity")
def kb_popularity_stats():
    responses = load_kb_responses()
    pop_by_type = defaultdict(list)
    for resp in responses:
        pop_by_type[resp.get('type', 'unknown')].append(resp.get('popularity_score', 0))
    avg_pop = {k: (sum(v)/len(v) if v else 0) for k, v in pop_by_type.items()}
    return avg_pop

@router.get("/kb-success")
def kb_success_stats():
    responses = load_kb_responses()
    succ_by_type = defaultdict(list)
    for resp in responses:
        succ_by_type[resp.get('type', 'unknown')].append(resp.get('success_rate', 0))
    avg_succ = {k: (sum(v)/len(v) if v else 0) for k, v in succ_by_type.items()}
    return avg_succ

@router.get("/top-intents")
async def top_intents(limit: int = 10, db: AsyncSession = Depends(get_db)):
    stmt = select(Message.intent, func.count(Message.id)).where(Message.intent != None).group_by(Message.intent).order_by(desc(func.count(Message.id))).limit(limit)
    result = await db.execute(stmt)
    return dict(result.all())

@router.get("/hardest-questions")
async def hardest_questions(limit: int = 10, db: AsyncSession = Depends(get_db)):
    # Find KB responses with lowest average feedback rating (hardest)
    stmt = select(
        Message.intent, Message.content, func.avg(Feedback.rating).label('avg_rating')
    ).join(Feedback, Feedback.message_id == Message.id, isouter=True)
    stmt = stmt.group_by(Message.intent, Message.content).order_by(asc(func.avg(Feedback.rating))).limit(limit)
    result = await db.execute(stmt)
    return [
        {"intent": row[0], "content": row[1], "avg_rating": row[2]} for row in result.all()
    ]

@router.get("/most-successful")
async def most_successful(limit: int = 10, db: AsyncSession = Depends(get_db)):
    # KB responses with highest average feedback rating
    stmt = select(
        Message.intent, Message.content, func.avg(Feedback.rating).label('avg_rating')
    ).join(Feedback, Feedback.message_id == Message.id, isouter=True)
    stmt = stmt.group_by(Message.intent, Message.content).order_by(desc(func.avg(Feedback.rating))).limit(limit)
    result = await db.execute(stmt)
    return [
        {"intent": row[0], "content": row[1], "avg_rating": row[2]} for row in result.all()
    ]

@router.get("/least-successful")
async def least_successful(limit: int = 10, db: AsyncSession = Depends(get_db)):
    # KB responses with lowest average feedback rating (excluding nulls)
    stmt = select(
        Message.intent, Message.content, func.avg(Feedback.rating).label('avg_rating')
    ).join(Feedback, Feedback.message_id == Message.id)
    stmt = stmt.group_by(Message.intent, Message.content).order_by(asc(func.avg(Feedback.rating))).limit(limit)
    result = await db.execute(stmt)
    return [
        {"intent": row[0], "content": row[1], "avg_rating": row[2]} for row in result.all()
    ]

@router.get("/export")
async def export_analytics(format: str = Query('json', enum=['json', 'csv']), db: AsyncSession = Depends(get_db)):
    # Export daily analytics: date, conversations, avg_response_time, avg_satisfaction
    # Conversation volume
    conv_stmt = select(cast(Conversation.created_at, Date), func.count(Conversation.id)).group_by(cast(Conversation.created_at, Date)).order_by(cast(Conversation.created_at, Date))
    conv_result = await db.execute(conv_stmt)
    conv_data = {str(row[0]): row[1] for row in conv_result.all()}
    # Response time trend
    msg_stmt = select(Message).order_by(Message.conversation_id, Message.created_at)
    msgs = (await db.execute(msg_stmt)).scalars().all()
    resp_times_by_date = defaultdict(list)
    last_user_msg = {}
    for msg in msgs:
        if msg.role == 'user':
            last_user_msg[msg.conversation_id] = msg.created_at
        elif msg.role == 'assistant' and msg.conversation_id in last_user_msg:
            delta = (msg.created_at - last_user_msg[msg.conversation_id]).total_seconds()
            if 0 < delta < 3600:
                resp_times_by_date[msg.created_at.date().isoformat()].append(delta)
            last_user_msg.pop(msg.conversation_id)
    # Satisfaction trend
    sat_stmt = select(cast(Feedback.timestamp, Date), func.avg(Feedback.rating)).group_by(cast(Feedback.timestamp, Date)).order_by(cast(Feedback.timestamp, Date))
    sat_result = await db.execute(sat_stmt)
    sat_data = {str(row[0]): row[1] for row in sat_result.all()}
    # Merge by date
    all_dates = set(conv_data.keys()) | set(resp_times_by_date.keys()) | set(sat_data.keys())
    rows = []
    for date in sorted(all_dates):
        conversations = conv_data.get(date, 0)
        resp_times = resp_times_by_date.get(date, [])
        avg_response_time = sum(resp_times)/len(resp_times) if resp_times else 0
        avg_satisfaction = sat_data.get(date, 0)
        rows.append({
            'date': date,
            'conversations': conversations,
            'avg_response_time': avg_response_time,
            'avg_satisfaction': avg_satisfaction
        })
    if format == 'csv':
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['date', 'conversations', 'avg_response_time', 'avg_satisfaction'])
        for row in rows:
            writer.writerow([row['date'], row['conversations'], row['avg_response_time'], row['avg_satisfaction']])
        output.seek(0)
        return StreamingResponse(output, media_type='text/csv', headers={
            'Content-Disposition': 'attachment; filename=analytics_export.csv'
        })
    else:
        return JSONResponse(content=rows) 