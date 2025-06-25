"""
Conversation Metrics Service for Business Intelligence and Quality Tracking

This service tracks conversation quality metrics including intent resolution rates,
tone alignment, frustration levels, and response effectiveness.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
import asyncio
import logging

logger = logging.getLogger(__name__)


@dataclass
class ConversationMetric:
    conversation_id: str
    user_id: str
    timestamp: datetime
    metric_type: str
    value: Any
    metadata: Dict[str, Any] = None


class ConversationMetricsCollector:
    """
    Collects and analyzes conversation quality metrics for business insights.
    """

    def __init__(self):
        self.metrics: List[ConversationMetric] = []
        self.session_data: Dict[str, Dict] = {}

    async def track_conversation_quality(
        self, conversation_id: str, interaction_data: Dict[str, Any]
    ) -> None:
        """Track conversation quality metrics."""

        metrics_to_track = [
            ("processing_time", interaction_data.get("processing_time_ms", 0)),
            ("is_follow_up", interaction_data.get("is_follow_up", False)),
            ("frustration_level", interaction_data.get("frustration_level", 0)),
            ("attempt_count", interaction_data.get("attempt_count", 1)),
            ("answer_type", interaction_data.get("answer_type", "unknown")),
            ("tone_used", interaction_data.get("tone_used", "default")),
        ]

        for metric_type, value in metrics_to_track:
            await self._record_metric(
                conversation_id, metric_type, value, interaction_data
            )

    async def calculate_intent_resolution_rate(
        self, time_window_hours: int = 24
    ) -> float:
        """Calculate intent resolution rate over time window."""

        cutoff_time = datetime.utcnow() - timedelta(hours=time_window_hours)
        recent_conversations = {}

        # Group metrics by conversation
        for metric in self.metrics:
            if metric.timestamp >= cutoff_time:
                conv_id = metric.conversation_id
                if conv_id not in recent_conversations:
                    recent_conversations[conv_id] = {}
                recent_conversations[conv_id][metric.metric_type] = metric.value

        # Calculate resolution rate
        total_conversations = len(recent_conversations)
        if total_conversations == 0:
            return 0.0

        resolved_count = 0
        for conv_data in recent_conversations.values():
            # Consider resolved if frustration level stayed low and no escalation
            max_frustration = conv_data.get("frustration_level", 0)
            attempt_count = conv_data.get("attempt_count", 1)

            if max_frustration < 5 and attempt_count <= 3:
                resolved_count += 1

        return resolved_count / total_conversations

    async def get_conversation_insights(self, conversation_id: str) -> Dict[str, Any]:
        """Get detailed insights for a specific conversation."""

        conv_metrics = self._get_conversation_metrics(conversation_id)

        return {
            "conversation_id": conversation_id,
            "total_interactions": conv_metrics.get("interaction_count", 0),
            "average_response_time": conv_metrics.get("avg_processing_time", 0),
            "frustration_progression": conv_metrics.get("frustration_levels", []),
            "resolution_attempts": conv_metrics.get("attempt_count", 0),
            "primary_tone": conv_metrics.get("primary_tone", "unknown"),
            "answer_types_used": conv_metrics.get("answer_types", []),
            "outcome_prediction": self._predict_outcome(conv_metrics),
        }

    def _get_conversation_metrics(self, conversation_id: str) -> Dict[str, Any]:
        """Get all metrics for a specific conversation."""
        conv_metrics = {
            "interaction_count": 0,
            "frustration_levels": [],
            "answer_types": [],
        }

        for metric in self.metrics:
            if metric.conversation_id == conversation_id:
                conv_metrics["interaction_count"] += 1

                if metric.metric_type == "frustration_level":
                    conv_metrics["frustration_levels"].append(metric.value)
                elif metric.metric_type == "answer_type":
                    conv_metrics["answer_types"].append(metric.value)
                elif metric.metric_type == "processing_time":
                    conv_metrics.setdefault("processing_times", []).append(metric.value)

        return conv_metrics

    def _predict_outcome(self, conv_metrics: Dict[str, Any]) -> str:
        """Predict conversation outcome based on metrics."""
        frustration_levels = conv_metrics.get("frustration_levels", [0])
        attempt_count = conv_metrics.get("attempt_count", 1)

        max_frustration = max(frustration_levels) if frustration_levels else 0

        if max_frustration >= 7 or attempt_count >= 4:
            return "likely_escalation"
        elif max_frustration < 3 and attempt_count <= 2:
            return "likely_resolved"
        else:
            return "ongoing_assistance"

    async def _record_metric(
        self,
        conversation_id: str,
        metric_type: str,
        value: Any,
        metadata: Dict[str, Any],
    ) -> None:
        """Record a metric for analysis."""

        metric = ConversationMetric(
            conversation_id=conversation_id,
            user_id=metadata.get("user_id", "unknown"),
            timestamp=datetime.utcnow(),
            metric_type=metric_type,
            value=value,
            metadata=metadata,
        )

        self.metrics.append(metric)

        # Keep only recent metrics (memory management)
        cutoff_time = datetime.utcnow() - timedelta(days=7)
        self.metrics = [m for m in self.metrics if m.timestamp >= cutoff_time]


# Global instance
metrics_collector = ConversationMetricsCollector()
