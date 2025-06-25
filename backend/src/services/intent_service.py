"""
Intent Classification Service for Multi-Agent Message Routing

This service provides intelligent message classification and routing capabilities
for the customer support system. It uses large language models to understand
user intent and route messages to appropriate specialized agents.

Key Features:
- Natural language intent classification using LLMs
- JSON-structured response parsing with fallback handling
- Confidence scoring for classification transparency
- Keyword extraction for enhanced understanding
- Multi-category support for diverse customer needs
- Robust error handling with graceful degradation

Intent Categories:
- general_inquiry: Basic questions and information requests
- technical_support: Technical issues, troubleshooting, connectivity
- billing: Payment, account, subscription-related queries
- feature_request: Product enhancement suggestions
- complaint: Service issues and dissatisfaction
- other: Fallback for unclassifiable messages

The service follows a two-stage process: classification followed by routing,
enabling both transparency and flexible agent assignment logic.
"""

from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from typing import Dict, List, Tuple
import json


class IntentService:
    """
    Service for classifying user messages and routing them to appropriate agents.

    This service leverages large language models to understand the intent behind
    user messages and categorize them into predefined categories. It provides
    confidence scores and keyword extraction to enable transparent and intelligent
    routing to specialized support agents.

    The classification process uses carefully crafted prompts to ensure consistent
    and accurate intent detection across various message types and phrasings.
    """

    def __init__(self):
        """
        Initialize the intent classification service with LLM and prompt configuration.

        Sets up:
        - LLM client with deterministic settings for consistent classification
        - Intent classification prompt template with clear instructions
        - Fallback mechanisms for error handling
        """
        # Initialize LLM with temperature=0 for deterministic, consistent classifications
        # This ensures reproducible results for the same input messages
        self.llm = ChatOpenAI(
            temperature=0,  # Deterministic responses for consistency
            model_name="gpt-3.5-turbo",  # Balance of capability and cost-effectiveness
        )

        # Define the prompt template for intent classification
        # This template provides clear instructions and expected output format
        self.intent_prompt = PromptTemplate(
            input_variables=["message"],
            template="""
            Analyze the following message and classify it into one of these categories:
            - general_inquiry: Basic questions, information requests, general help
            - technical_support: Technical issues, troubleshooting, connectivity problems
            - billing: Payment issues, account questions, subscription concerns
            - feature_request: Suggestions for new features or improvements
            - complaint: Service issues, dissatisfaction, problems with service
            - other: Messages that don't fit clearly into the above categories

            Message: {message}

            Analyze the message carefully and respond with a JSON object containing:
            {{
                "intent": "category",
                "confidence": 0.0-1.0,
                "keywords": ["relevant", "key", "words"]
            }}
            
            The confidence should reflect how certain you are about the classification.
            Keywords should be the most relevant words that led to your decision.
            """,
        )

    async def classify_intent(self, message: str) -> Dict:
        """
        Classify the intent of a user message using LLM analysis.

        This method sends the user message through the LLM with a structured
        prompt to get intent classification, confidence scoring, and keyword
        extraction. It includes robust error handling to ensure the service
        always returns a valid response even if the LLM output is malformed.

        Args:
            message: The user message to classify

        Returns:
            Dict: Classification result with intent, confidence, and keywords
                 Always returns a valid dict even on parsing errors
        """
        # Create and execute the LLM chain with the message
        chain = self.intent_prompt | self.llm
        result = await chain.ainvoke({"message": message})

        try:
            # Attempt to parse the LLM response as JSON
            # The LLM is instructed to return structured JSON for easy parsing
            return json.loads(result.content)
        except (json.JSONDecodeError, KeyError, AttributeError):
            # Fallback response if JSON parsing fails
            # This ensures the service never fails completely due to LLM output issues
            return {
                "intent": "other",  # Safe default category
                "confidence": 0.0,  # Low confidence indicates parsing failure
                "keywords": [],  # Empty keywords when parsing fails
            }

    async def route_message(self, message: str) -> Tuple[str, Dict]:
        """
        Route a message to the appropriate agent based on intent classification.

        This method combines intent classification with routing logic to determine
        which specialized agent should handle the user's message. It provides both
        the routing decision and the underlying classification data for transparency.

        The routing logic can be customized to handle business rules, agent
        availability, escalation policies, and other organizational requirements.

        Args:
            message: The user message to route

        Returns:
            Tuple[str, Dict]: Agent type and classification data
                - Agent type: String identifier for the target agent
                - Classification data: Full intent analysis with confidence and keywords
        """
        # First, classify the message to understand user intent
        intent_data = await self.classify_intent(message)

        # Route based on classified intent with business logic
        # This mapping can be enhanced with more sophisticated routing rules
        if intent_data["intent"] == "technical_support":
            # Route technical issues to specialized technical support agents
            return "technical_support", intent_data
        elif intent_data["intent"] == "billing":
            # Route billing queries to financial/account specialists
            return "billing", intent_data
        elif intent_data["intent"] == "feature_request":
            # Route feature requests to product team or specialized handlers
            return "feature_request", intent_data
        else:
            # Default routing for general inquiries and unclassified messages
            # This includes general_inquiry, complaint, and other categories
            return "general", intent_data
