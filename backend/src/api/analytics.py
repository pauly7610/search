from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

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

@router.get("/overview", response_model=Analytics)
def get_analytics_overview():
    return Analytics(
        totalConversations=1234,
        averageResponseTime="2.5s",
        satisfactionRate="92%",
        activeUsers=456,
        conversationVolume=[
            {"date": "2024-01", "conversations": 400},
            {"date": "2024-02", "conversations": 300},
            {"date": "2024-03", "conversations": 500},
            {"date": "2024-04", "conversations": 280},
            {"date": "2024-05", "conversations": 590},
            {"date": "2024-06", "conversations": 800},
        ],
        responseTimeTrend=[
            {"date": "2024-01", "responseTime": 2.5},
            {"date": "2024-02", "responseTime": 2.2},
            {"date": "2024-03", "responseTime": 2.8},
            {"date": "2024-04", "responseTime": 2.1},
            {"date": "2024-05", "responseTime": 1.9},
            {"date": "2024-06", "responseTime": 1.7},
        ],
        satisfactionTrend=[
            {"date": "2024-01", "satisfaction": 85},
            {"date": "2024-02", "satisfaction": 88},
            {"date": "2024-03", "satisfaction": 92},
            {"date": "2024-04", "satisfaction": 90},
            {"date": "2024-05", "satisfaction": 94},
            {"date": "2024-06", "satisfaction": 96},
        ],
    )

@router.get("/conversation-volume", response_model=List[ConversationVolume])
def get_conversation_volume():
    return [
        {"date": "2024-01", "conversations": 400},
        {"date": "2024-02", "conversations": 300},
        {"date": "2024-03", "conversations": 500},
        {"date": "2024-04", "conversations": 280},
        {"date": "2024-05", "conversations": 590},
        {"date": "2024-06", "conversations": 800},
    ]

@router.get("/response-time", response_model=List[ResponseTimeTrend])
def get_response_time_trend():
    return [
        {"date": "2024-01", "responseTime": 2.5},
        {"date": "2024-02", "responseTime": 2.2},
        {"date": "2024-03", "responseTime": 2.8},
        {"date": "2024-04", "responseTime": 2.1},
        {"date": "2024-05", "responseTime": 1.9},
        {"date": "2024-06", "responseTime": 1.7},
    ]

@router.get("/satisfaction", response_model=List[SatisfactionTrend])
def get_satisfaction_trend():
    return [
        {"date": "2024-01", "satisfaction": 85},
        {"date": "2024-02", "satisfaction": 88},
        {"date": "2024-03", "satisfaction": 92},
        {"date": "2024-04", "satisfaction": 90},
        {"date": "2024-05", "satisfaction": 94},
        {"date": "2024-06", "satisfaction": 96},
    ] 