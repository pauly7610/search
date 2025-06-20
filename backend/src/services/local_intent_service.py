"""
Local Intent Classification Service

This service provides intent classification without requiring external API calls.
It uses keyword-based matching to classify user messages into different support categories.
"""

import logging
from typing import Dict, Any, List, Tuple
import re

logger = logging.getLogger(__name__)

class LocalIntentService:
    """
    Local intent classification service using keyword-based matching.
    
    This service classifies user messages into different support categories
    without requiring external API calls, providing a reliable fallback
    when AI services are unavailable.
    """
    
    def __init__(self):
        """Initialize the local intent service with keyword patterns."""
        self.intent_patterns = {
            "billing": {
                "keywords": [
                    "bill", "billing", "charge", "charges", "payment", "pay", "cost", "costs",
                    "expensive", "high bill", "overcharge", "refund", "credit", "balance",
                    "account", "statement", "invoice", "fee", "fees", "price", "pricing",
                    "my bill is so high", "help me understand my bill", "explain my charges",
                    "why is my bill", "billing question", "payment due", "autopay"
                ],
                "phrases": [
                    "my bill is so high", "help me understand my bill", "explain my charges",
                    "why is my bill", "how much do i owe", "payment is due", "can't afford",
                    "billing error", "wrong charge", "unexpected charge"
                ],
                "confidence_boost": 0.3
            },
            "technical_support": {
                "keywords": [
                    "internet", "wifi", "connection", "slow", "down", "outage", "not working",
                    "broken", "fix", "repair", "troubleshoot", "speed", "bandwidth", "modem",
                    "router", "cable", "signal", "network", "ethernet", "wireless", "connect",
                    "disconnect", "reset", "reboot", "setup", "install", "configuration"
                ],
                "phrases": [
                    "internet is slow", "wifi not working", "connection problems", "can't connect",
                    "internet is down", "no internet", "wifi issues", "slow speed", "internet out",
                    "connection lost", "can't get online", "network problems"
                ],
                "confidence_boost": 0.3
            },
            "equipment": {
                "keywords": [
                    "box", "cable box", "remote", "tv", "television", "dvr", "receiver",
                    "equipment", "device", "hardware", "replacement", "upgrade", "install",
                    "setup", "activation", "activate", "new equipment", "broken equipment"
                ],
                "phrases": [
                    "cable box not working", "remote not working", "tv problems", "need new equipment",
                    "equipment broken", "box is broken", "remote broken", "dvr issues"
                ],
                "confidence_boost": 0.2
            },
            "general": {
                "keywords": [
                    "help", "support", "assistance", "question", "info", "information",
                    "service", "customer service", "representative", "agent", "talk to someone"
                ],
                "phrases": [
                    "can you help me", "need assistance", "have a question", "need help",
                    "customer service", "talk to agent", "speak to someone"
                ],
                "confidence_boost": 0.1
            }
        }
        
        logger.info("Local intent service initialized successfully")
    
    def classify_intent(self, message: str) -> Dict[str, Any]:
        """
        Classify the intent of a user message using keyword-based matching.
        
        Args:
            message: User message to classify
            
        Returns:
            Dict containing intent classification results
        """
        if not message or not isinstance(message, str):
            return {
                "intent": "general",
                "confidence": 0.5,
                "method": "local_fallback",
                "keywords_matched": [],
                "reasoning": "Empty or invalid message"
            }
        
        message_lower = message.lower().strip()
        intent_scores = {}
        matched_keywords = {}
        
        # Calculate scores for each intent category
        for intent, patterns in self.intent_patterns.items():
            score = 0
            keywords_found = []
            
            # Check for exact phrase matches (higher weight)
            for phrase in patterns.get("phrases", []):
                if phrase.lower() in message_lower:
                    score += 0.8  # High score for phrase matches
                    keywords_found.append(phrase)
            
            # Check for individual keyword matches
            for keyword in patterns.get("keywords", []):
                if keyword.lower() in message_lower:
                    score += 0.3  # Lower score for individual keywords
                    keywords_found.append(keyword)
            
            # Apply confidence boost
            if score > 0:
                score += patterns.get("confidence_boost", 0)
            
            intent_scores[intent] = score
            matched_keywords[intent] = keywords_found
        
        # Determine the best intent
        if not intent_scores or max(intent_scores.values()) == 0:
            return {
                "intent": "general",
                "confidence": 0.5,
                "method": "local_default",
                "keywords_matched": [],
                "reasoning": "No keywords matched, defaulting to general"
            }
        
        best_intent = max(intent_scores.keys(), key=lambda k: intent_scores[k])
        confidence = min(intent_scores[best_intent], 1.0)  # Cap at 1.0
        
        # Boost confidence for very specific matches
        if confidence > 0.8:
            confidence = min(confidence + 0.15, 0.95)  # High confidence for good matches
        
        result = {
            "intent": best_intent,
            "confidence": confidence,
            "method": "local_keyword_matching",
            "keywords_matched": matched_keywords[best_intent],
            "reasoning": f"Matched {len(matched_keywords[best_intent])} keywords/phrases for {best_intent}",
            "all_scores": intent_scores
        }
        
        logger.debug(f"Local intent classification: {message[:50]}... -> {best_intent} ({confidence:.2f})")
        return result
    
    async def route_message(self, message: str) -> Tuple[str, Dict[str, Any]]:
        """
        Route a message to the appropriate agent based on intent classification.
        
        This method combines intent classification with routing logic to determine
        which specialized agent should handle the user's message. It provides both
        the routing decision and the underlying classification data for transparency.
        
        Args:
            message: The user message to route
            
        Returns:
            Tuple[str, Dict]: Agent type and classification data
                - Agent type: String identifier for the target agent
                - Classification data: Full intent analysis with confidence and keywords
        """
        # First, classify the message to understand user intent
        intent_data = self.classify_intent(message)
        
        # Route based on classified intent with business logic
        # This mapping can be enhanced with more sophisticated routing rules
        if intent_data["intent"] == "technical_support":
            # Route technical issues to specialized technical support agents
            return "technical_support", intent_data
        elif intent_data["intent"] == "billing":
            # Route billing queries to financial/account specialists
            return "billing", intent_data
        elif intent_data["intent"] == "equipment":
            # Route equipment issues to technical support
            return "technical_support", intent_data
        else:
            # Default routing for general inquiries and unclassified messages
            # This includes general_inquiry and other categories
            return "general", intent_data
    
    def get_supported_intents(self) -> List[str]:
        """Get list of supported intent categories."""
        return list(self.intent_patterns.keys())
    
    def add_custom_pattern(self, intent: str, keywords: List[str], phrases: List[str] = None):
        """
        Add custom patterns for intent classification.
        
        Args:
            intent: Intent category name
            keywords: List of keywords to match
            phrases: List of phrases to match (optional)
        """
        if intent not in self.intent_patterns:
            self.intent_patterns[intent] = {
                "keywords": [],
                "phrases": [],
                "confidence_boost": 0.1
            }
        
        self.intent_patterns[intent]["keywords"].extend(keywords)
        if phrases:
            self.intent_patterns[intent]["phrases"].extend(phrases)
        
        logger.info(f"Added custom patterns for intent: {intent}")

# Global instance for easy import
local_intent_service = LocalIntentService() 