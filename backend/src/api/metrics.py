"""
Business Metrics API for Conversation Quality and Performance Tracking
"""

from fastapi import APIRouter, Depends, Query
from typing import Optional
from datetime import datetime
from src.services.conversation_metrics import metrics_collector

router = APIRouter()


@router.get("/conversation-quality")
async def get_conversation_quality_metrics(
    hours: int = Query(24, description="Time window in hours"),
    conversation_id: Optional[str] = Query(
        None, description="Specific conversation ID"
    ),
):
    """Get conversation quality metrics and KPIs."""

    if conversation_id:
        return await metrics_collector.get_conversation_insights(conversation_id)

    # Overall metrics
    intent_resolution_rate = await metrics_collector.calculate_intent_resolution_rate(
        hours
    )

    return {
        "time_window_hours": hours,
        "intent_resolution_rate": intent_resolution_rate,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/conversation/{conversation_id}/flow")
async def get_conversation_flow_analysis(conversation_id: str):
    """Get detailed conversation flow analysis."""

    insights = await metrics_collector.get_conversation_insights(conversation_id)
    recommendations = []

    if insights.get("outcome_prediction") == "likely_escalation":
        recommendations.append("Consider proactive human agent intervention")

    if max(insights.get("frustration_progression", [0])) >= 5:
        recommendations.append("Implement more empathetic tone responses")

    if insights.get("resolution_attempts", 0) >= 3:
        recommendations.append("Offer alternative communication channels")

    return {"conversation_analysis": insights, "recommendations": recommendations}
