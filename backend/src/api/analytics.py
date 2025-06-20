"""
Analytics API Module for Customer Support Performance Monitoring

This module provides comprehensive analytics endpoints for monitoring and analyzing
customer support system performance. It includes metrics for conversation volume,
response times, satisfaction rates, and knowledge base effectiveness.

Key Features:
- Real-time analytics dashboard data
- Conversation volume and trends analysis
- Response time tracking and optimization insights
- Customer satisfaction monitoring
- Knowledge base performance metrics
- Intent classification analytics
- Export capabilities for further analysis
- Flexible filtering and date range selection

Database Integration:
- Asynchronous database operations for performance
- Complex aggregation queries for trend analysis
- Cross-table joins for comprehensive insights
- Optimized queries with proper indexing considerations

The analytics system provides both overview metrics and detailed drill-down
capabilities for comprehensive performance monitoring and optimization.
"""

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

# Initialize API router for analytics endpoints
router = APIRouter()

class ConversationVolume(BaseModel):
    """
    Data model for conversation volume metrics over time.
    
    Represents the number of conversations on a specific date,
    useful for tracking usage patterns and system load.
    """
    date: str           # Date in YYYY-MM-DD format
    conversations: int  # Number of conversations on this date

class ResponseTimeTrend(BaseModel):
    """
    Data model for response time trend analysis.
    
    Tracks average response times over time to identify
    performance improvements or degradations.
    """
    date: str            # Date in YYYY-MM-DD format
    responseTime: float  # Average response time in seconds

class SatisfactionTrend(BaseModel):
    """
    Data model for customer satisfaction trends.
    
    Monitors satisfaction scores over time to track
    service quality improvements.
    """
    date: str         # Date in YYYY-MM-DD format
    satisfaction: int # Average satisfaction score

class Analytics(BaseModel):
    """
    Comprehensive analytics data model for dashboard overview.
    
    Combines multiple metrics into a single response for
    efficient dashboard loading and display.
    """
    totalConversations: int                           # Total conversation count
    averageResponseTime: str                          # Formatted average response time
    satisfactionRate: str                            # Formatted satisfaction percentage
    activeUsers: int                                 # Count of unique active users
    conversationVolume: List[ConversationVolume]     # Daily conversation volumes
    responseTimeTrend: List[ResponseTimeTrend]       # Response time trends
    satisfactionTrend: List[SatisfactionTrend]      # Satisfaction trends

# Path to knowledge base file for static analysis
KB_PATH = os.path.join(os.path.dirname(__file__), '../xfinity_knowledge_base.json')

def load_kb_responses():
    """
    Load and parse knowledge base responses for analysis.
    
    This function reads the knowledge base JSON file and extracts
    all response entries for statistical analysis. It's used for
    knowledge base effectiveness metrics and content analysis.
    
    Returns:
        List[Dict]: List of all knowledge base response entries
    """
    with open(KB_PATH, 'r', encoding='utf-8') as f:
        kb = json.load(f)['knowledge_base']['agents']
    
    responses = []
    # Extract all responses from all agents and categories
    for agent, agent_data in kb.items():
        for category, cat_data in agent_data.get('categories', {}).items():
            for resp in cat_data.get('responses', []):
                responses.append(resp)
    
    return responses

@router.get("/overview", response_model=Analytics)
async def get_analytics_overview(db: AsyncSession = Depends(get_db)):
    """
    Get comprehensive analytics overview for dashboard display.
    
    This endpoint aggregates multiple analytics metrics into a single
    response for efficient dashboard loading. It calculates:
    - Total conversation count
    - Average response time with outlier filtering
    - Customer satisfaction rate from feedback
    - Active user count
    - Trend data for charts and graphs
    
    The response includes both current metrics and historical trends
    for comprehensive performance monitoring.
    
    Args:
        db: Database session for async operations
        
    Returns:
        Analytics: Complete analytics overview with all metrics
    """
    # Calculate total conversations from database
    total_convs = (await db.execute(select(func.count(Conversation.id)))).scalar()
    
    # Count unique active users based on conversation participation
    active_users = (await db.execute(
        select(func.count(func.distinct(Conversation.user_id)))
    )).scalar()
    
    # Calculate average response time with outlier filtering
    # This involves analyzing message timestamps to determine response delays
    msg_stmt = select(Message).order_by(Message.conversation_id, Message.created_at)
    msgs = (await db.execute(msg_stmt)).scalars().all()
    
    response_times = []
    last_user_msg = {}  # Track last user message per conversation
    
    # Process messages to calculate response times
    for msg in msgs:
        if msg.role == 'user':
            # Store timestamp of user messages
            last_user_msg[msg.conversation_id] = msg.created_at
        elif msg.role == 'assistant' and msg.conversation_id in last_user_msg:
            # Calculate response time for assistant replies
            delta = (msg.created_at - last_user_msg[msg.conversation_id]).total_seconds()
            # Filter outliers (response times between 0 and 1 hour)
            if 0 < delta < 3600:
                response_times.append(delta)
            # Clear the user message to avoid double counting
            last_user_msg.pop(msg.conversation_id)
    
    # Format average response time for display
    avg_response_time = f"{(sum(response_times)/len(response_times)):.1f}s" if response_times else "0s"
    
    # Calculate satisfaction rate from feedback ratings
    avg_rating = (await db.execute(select(func.avg(Feedback.rating)))).scalar()
    # Convert 1-5 scale to percentage (multiply by 20)
    satisfaction_rate = f"{(avg_rating*20):.0f}%" if avg_rating else "0%"
    
    # Get trend data for charts
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
    """
    Get daily conversation volume for trend analysis.
    
    Aggregates conversations by date to show usage patterns
    and system load over time. Useful for capacity planning
    and identifying peak usage periods.
    
    Args:
        db: Database session for async operations
        
    Returns:
        List[ConversationVolume]: Daily conversation counts
    """
    # Group conversations by date and count them
    stmt = select(
        cast(Conversation.created_at, Date), 
        func.count(Conversation.id)
    ).group_by(
        cast(Conversation.created_at, Date)
    ).order_by(
        cast(Conversation.created_at, Date)
    )
    
    result = await db.execute(stmt)
    return [
        {"date": str(row[0]), "conversations": row[1]} 
        for row in result.all()
    ]

@router.get("/response-time", response_model=List[ResponseTimeTrend])
async def get_response_time_trend(db: AsyncSession = Depends(get_db)):
    """
    Calculate average response time trends by date.
    
    Analyzes message timestamps to determine response times
    and aggregates them by date for trend visualization.
    Helps identify performance improvements or degradations.
    
    Args:
        db: Database session for async operations
        
    Returns:
        List[ResponseTimeTrend]: Daily average response times
    """
    # Retrieve all messages ordered by conversation and time
    msg_stmt = select(Message).order_by(Message.conversation_id, Message.created_at)
    msgs = (await db.execute(msg_stmt)).scalars().all()
    
    # Group response times by date
    resp_times_by_date = defaultdict(list)
    last_user_msg = {}
    
    # Process messages to calculate daily response times
    for msg in msgs:
        if msg.role == 'user':
            last_user_msg[msg.conversation_id] = msg.created_at
        elif msg.role == 'assistant' and msg.conversation_id in last_user_msg:
            delta = (msg.created_at - last_user_msg[msg.conversation_id]).total_seconds()
            # Filter outliers and group by date
            if 0 < delta < 3600:
                resp_times_by_date[msg.created_at.date()].append(delta)
            last_user_msg.pop(msg.conversation_id)
    
    # Calculate daily averages
    return [
        {"date": str(date), "responseTime": sum(times)/len(times) if times else 0}
        for date, times in sorted(resp_times_by_date.items())
    ]

@router.get("/satisfaction", response_model=List[SatisfactionTrend])
async def get_satisfaction_trend(db: AsyncSession = Depends(get_db)):
    """
    Get customer satisfaction trends over time.
    
    Aggregates feedback ratings by date to show satisfaction
    trends and identify periods of improvement or decline.
    
    Args:
        db: Database session for async operations
        
    Returns:
        List[SatisfactionTrend]: Daily satisfaction averages
    """
    # Group feedback by date and calculate averages
    stmt = select(
        cast(Feedback.timestamp, Date), 
        func.avg(Feedback.rating)
    ).group_by(
        cast(Feedback.timestamp, Date)
    ).order_by(
        cast(Feedback.timestamp, Date)
    )
    
    result = await db.execute(stmt)
    return [
        {"date": str(row[0]), "satisfaction": int(row[1]) if row[1] is not None else 0} 
        for row in result.all()
    ]

@router.get("/kb-intents")
def kb_intent_stats():
    """
    Analyze knowledge base intent distribution.
    
    Counts the frequency of different intent tags in the knowledge base
    to understand content coverage and identify gaps.
    
    Returns:
        Dict: Intent tag frequencies
    """
    responses = load_kb_responses()
    intent_counter = Counter()
    
    # Count intent tags across all responses
    for resp in responses:
        for tag in resp.get('intent_tags', []):
            intent_counter[tag] += 1
    
    return dict(intent_counter)

@router.get("/kb-difficulty")
def kb_difficulty_stats():
    """
    Analyze knowledge base difficulty level distribution.
    
    Shows the distribution of content difficulty levels to ensure
    appropriate coverage for different user expertise levels.
    
    Returns:
        Dict: Difficulty level frequencies
    """
    responses = load_kb_responses()
    diff_counter = Counter()
    
    # Count difficulty levels
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
    """
    Get the most frequently classified intents from actual conversations.
    
    Analyzes real conversation data to identify the most common
    user intents, helping with resource allocation and content planning.
    
    Args:
        limit: Maximum number of intents to return
        db: Database session for async operations
        
    Returns:
        Dict: Intent frequencies from actual conversations
    """
    # Query message intents and count occurrences
    stmt = select(
        Message.intent, 
        func.count(Message.id)
    ).where(
        Message.intent != None
    ).group_by(
        Message.intent
    ).order_by(
        desc(func.count(Message.id))
    ).limit(limit)
    
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