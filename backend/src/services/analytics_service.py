from datetime import datetime, timedelta
from typing import List, Dict
import json
from collections import defaultdict


class AnalyticsService:
    def __init__(self):
        self.conversations = []
        self.response_times = []
        self.satisfaction_scores = []
        self.intent_counts = defaultdict(int)

    def add_conversation(self, conversation_id: str, messages: List[Dict]):
        self.conversations.append(
            {
                "id": conversation_id,
                "messages": messages,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    def add_response_time(self, response_time: float):
        self.response_times.append(
            {"timestamp": datetime.utcnow().isoformat(), "response_time": response_time}
        )

    def add_satisfaction_score(self, score: int):
        self.satisfaction_scores.append(
            {"timestamp": datetime.utcnow().isoformat(), "score": score}
        )

    def add_intent(self, intent: str):
        self.intent_counts[intent] += 1

    def get_conversation_volume(self, days: int = 30) -> List[Dict]:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # Group conversations by date
        volume_by_date = defaultdict(int)
        for conv in self.conversations:
            conv_date = datetime.fromisoformat(conv["timestamp"]).date()
            if start_date.date() <= conv_date <= end_date.date():
                volume_by_date[conv_date.isoformat()] += 1

        return [
            {"date": date, "conversations": count}
            for date, count in sorted(volume_by_date.items())
        ]

    def get_response_time_trend(self, days: int = 30) -> List[Dict]:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # Group response times by date
        times_by_date = defaultdict(list)
        for rt in self.response_times:
            rt_date = datetime.fromisoformat(rt["timestamp"]).date()
            if start_date.date() <= rt_date <= end_date.date():
                times_by_date[rt_date.isoformat()].append(rt["response_time"])

        return [
            {"date": date, "responseTime": sum(times) / len(times) if times else 0}
            for date, times in sorted(times_by_date.items())
        ]

    def get_satisfaction_trend(self, days: int = 30) -> List[Dict]:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # Group satisfaction scores by date
        scores_by_date = defaultdict(list)
        for score in self.satisfaction_scores:
            score_date = datetime.fromisoformat(score["timestamp"]).date()
            if start_date.date() <= score_date <= end_date.date():
                scores_by_date[score_date.isoformat()].append(score["score"])

        return [
            {"date": date, "satisfaction": sum(scores) / len(scores) if scores else 0}
            for date, scores in sorted(scores_by_date.items())
        ]

    def get_intent_distribution(self) -> Dict[str, int]:
        return dict(self.intent_counts)

    def get_overview(self) -> Dict:
        return {
            "totalConversations": len(self.conversations),
            "averageResponseTime": (
                f"{sum(rt['response_time'] for rt in self.response_times) / len(self.response_times):.1f}s"
                if self.response_times
                else "0s"
            ),
            "satisfactionRate": (
                f"{sum(score['score'] for score in self.satisfaction_scores) / len(self.satisfaction_scores):.0f}%"
                if self.satisfaction_scores
                else "0%"
            ),
            "activeUsers": len(set(conv["id"] for conv in self.conversations)),
            "conversationVolume": self.get_conversation_volume(),
            "responseTimeTrend": self.get_response_time_trend(),
            "satisfactionTrend": self.get_satisfaction_trend(),
            "intentDistribution": self.get_intent_distribution(),
        }
