"""
Enhanced Chat Service Module for Multi-Agent Customer Support System with Natural Conversational Flow

This module implements enhanced chat functionality with intelligent agent routing,
knowledge base search, conversation management, and natural follow-up handling.
It serves as the orchestrator for the AI-powered customer support system.

Key Components:
- Multi-agent routing based on intent classification
- Knowledge base search with fuzzy matching
- Conversation memory management with context awareness
- Natural follow-up detection and handling ("that didn't work", "still not working")
- Frustration level monitoring and tone adaptation
- LLM fallback for complex queries
- Business metrics tracking for conversation quality
- Robust error handling and recovery

Enhanced Features:
- Follow-up conversation patterns recognition
- Context-aware tone selection (helpful, empathetic, escalation)
- Frustration detection and adaptive responses
- Solution tracking and alternative suggestion logic
- Business intelligence metrics collection

Architecture:
The service follows an enhanced coordinator pattern where incoming messages are:
1. Analyzed for follow-up context and frustration indicators
2. Classified by intent with conversation state awareness
3. Routed to appropriate specialized agents with tone adaptation
4. Matched against knowledge base responses with context
5. Augmented with empathetic LLM responses when needed
6. Tracked for business metrics and conversation quality
7. Returned with full context, metadata, and flow information
"""

import json
import time
import uuid
import logging
import re
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
from dataclasses import dataclass

from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

from src.services.intent_service import IntentService
from src.repositories.chat_repository import ChatRepository
from src.config.database import get_db

logger = logging.getLogger(__name__)


class ConversationState(Enum):
    INITIAL = "initial"
    PROBLEM_SOLVING = "problem_solving"
    FOLLOW_UP = "follow_up"
    ESCALATION = "escalation"
    RESOLVED = "resolved"


@dataclass
class ConversationContext:
    conversation_id: str
    user_id: str
    current_state: ConversationState
    last_solution_offered: Optional[str] = None
    attempt_count: int = 0
    frustration_level: int = 0  # 0-10 scale
    topic: Optional[str] = None
    preferred_tone: str = "helpful"
    resolution_attempts: List[Dict] = None

    def __post_init__(self):
        if self.resolution_attempts is None:
            self.resolution_attempts = []


class ChatService:
    """
    Enhanced Chat Service with natural conversational flow, follow-up handling,
    and business metrics tracking.

    This service manages the complete conversation lifecycle including:
    - Agent selection and routing with context awareness
    - Knowledge base searching with solution tracking
    - LLM integration for complex queries with tone adaptation
    - Conversation state management and follow-up detection
    - Response formatting and metadata with flow information
    - Frustration level monitoring and empathetic responses

    The service maintains separate conversation chains for each session
    to preserve context across multiple message exchanges, while also
    tracking conversation quality metrics for business intelligence.
    """

    def __init__(self):
        """
        Initialize the enhanced chat service with all necessary components.

        Sets up:
        - LLM client for complex query handling with tone adaptation
        - Knowledge base loading and indexing
        - Intent classification service
        - Conversation storage with context tracking
        - Follow-up detection patterns
        - Tone-specific prompt templates
        """
        # Dictionary to store active conversation chains by session ID
        # This allows for persistent conversation context across messages
        self.conversations: Dict[str, ConversationChain] = {}

        # New: Conversation context tracking for follow-up handling
        self.conversation_contexts: Dict[str, ConversationContext] = {}

        # Load and parse the knowledge base from JSON file
        # The knowledge base contains structured responses for different support categories
        import os

        kb_path = os.path.join(
            os.path.dirname(__file__), "../xfinity_knowledge_base.json"
        )
        try:
            with open(kb_path, "r") as f:
                self.kb = json.load(f)["knowledge_base"]["agents"]
        except FileNotFoundError:
            logger.warning("Knowledge base file not found")
            self.kb = {
                "tech_support": {"categories": {}},
                "billing": {"categories": {}},
                "general": {"categories": {}},
            }

        # Initialize LLM with moderate temperature for balanced creativity (optional)
        # Temperature 0.7 provides good balance between deterministic and creative responses
        try:
            self.llm = ChatOpenAI(temperature=0.7, model_name="gpt-3.5-turbo")
            self.llm_available = True
        except Exception as e:
            logger.warning(f"LLM initialization failed: {e}")
            self.llm = None
            self.llm_available = False

        # Initialize local intent classification service for message routing
        try:
            from src.services.local_intent_service import LocalIntentService

            self.intent_service = LocalIntentService()
            self.intent_service_available = True
            logger.info("Local intent service initialized successfully")
        except Exception as e:
            logger.warning(f"Local intent service initialization failed: {e}")
            self.intent_service = IntentService()
            self.intent_service_available = True

        # Enhanced follow-up detection patterns
        self.follow_up_patterns = [
            r"that (?:didn't|doesn't?) work",
            r"(?:still|it's still) not working",
            r"(?:that|it) (?:didn't|doesn't) help",
            r"(?:try|give me) (?:something|another) (?:else|different)",
            r"what else (?:can|could) (?:you|we)",
            r"(?:any|got) other (?:ideas|suggestions|solutions)",
            r"(?:doesn't|isn't?) (?:solving|fixing) (?:my|the) (?:problem|issue)",
            r"I need (?:more|different|another) help",
            r"(?:can you|could you) help (?:me )?(?:with )?something else",
        ]

        self.frustration_indicators = [
            r"(?:this is )?(?:really )?frustrating",
            r"(?:why )?(?:is this|this is) so (?:hard|difficult|complicated)",
            r"(?:I|we) (?:already|just) tried that",
            r"(?:that|this) (?:makes no|doesn't make) sense",
            r"(?:I|we) (?:need|want) to (?:speak|talk) to (?:a )?(?:human|person|someone)",
            r"(?:this )?(?:chatbot|bot|system) (?:is )?(?:useless|not helping|broken)",
        ]

        # Tone-specific prompt templates
        self.tone_prompts = {
            "helpful_friendly": """You are a helpful AI customer service assistant for Xfinity. 
            Be friendly, professional, and solution-focused. Provide clear, actionable steps.""",
            "understanding_adaptive": """You understand that your previous suggestion didn't work. 
            Acknowledge this empathetically and offer a different approach. Be understanding and adaptive.
            Say something like "I understand that didn't work for you" before offering alternatives.""",
            "patient_alternative": """The customer has tried multiple solutions. 
            Be patient, offer clearly different alternatives, and ask clarifying questions.
            Show that you're taking a different approach this time.""",
            "empathetic_supportive": """The customer seems frustrated. 
            Be empathetic, acknowledge their frustration, and focus on finding a solution.
            Use phrases like "I can understand how frustrating this must be" before helping.""",
            "empathetic_escalation": """The customer is very frustrated. 
            Be deeply empathetic, apologize for the trouble, and consider escalation options.
            Offer to connect them with a human agent if needed.""",
        }

    def get_or_create_context(
        self, conversation_id: str, user_id: str = None
    ) -> ConversationContext:
        """Get existing context or create new one."""
        if conversation_id not in self.conversation_contexts:
            self.conversation_contexts[conversation_id] = ConversationContext(
                conversation_id=conversation_id,
                user_id=user_id or conversation_id,
                current_state=ConversationState.INITIAL,
            )
        return self.conversation_contexts[conversation_id]

    def detect_follow_up(self, message: str, context: ConversationContext) -> bool:
        """Detect if message is a follow-up to previous solution."""
        message_lower = message.lower()

        # Check for explicit follow-up patterns
        for pattern in self.follow_up_patterns:
            if re.search(pattern, message_lower):
                return True

        # Context-based detection
        if (
            context.current_state == ConversationState.PROBLEM_SOLVING
            and context.last_solution_offered
            and len(message.split()) < 10
        ):  # Short messages often indicate problems
            return True

        return False

    def detect_frustration_level(
        self, message: str, context: ConversationContext
    ) -> int:
        """Analyze frustration level from message content and context."""
        message_lower = message.lower()
        frustration_score = context.frustration_level

        # Check frustration indicators
        for pattern in self.frustration_indicators:
            if re.search(pattern, message_lower):
                frustration_score += 2

        # Caps lock indicates frustration
        caps_ratio = sum(1 for c in message if c.isupper()) / max(len(message), 1)
        if caps_ratio > 0.3:
            frustration_score += 1

        # Multiple punctuation marks
        if re.search(r"[!?]{2,}", message):
            frustration_score += 1

        # Repeated attempts
        if context.attempt_count > 2:
            frustration_score += 1

        return min(frustration_score, 10)

    def determine_tone(self, context: ConversationContext) -> str:
        """Determine appropriate conversational tone based on context."""
        if context.frustration_level >= 7:
            return "empathetic_escalation"
        elif context.frustration_level >= 4:
            return "empathetic_supportive"
        elif context.attempt_count >= 3:
            return "patient_alternative"
        elif context.current_state == ConversationState.FOLLOW_UP:
            return "understanding_adaptive"
        else:
            return "helpful_friendly"

    def create_follow_up_prompt(
        self, message: str, context: ConversationContext
    ) -> str:
        """Create context-aware prompt for follow-up handling."""

        base_prompt = f"""
        The customer just said: "{message}"
        
        This appears to be follow-up feedback indicating that a previous solution didn't work.
        
        Context:
        - Attempt count: {context.attempt_count}
        - Frustration level: {context.frustration_level}/10
        - Previous solution: {context.last_solution_offered or 'None recorded'}
        
        Please:
        1. Acknowledge that the previous approach didn't work
        2. Show understanding and empathy
        3. Offer a different, specific alternative solution
        4. Ask a clarifying question if needed
        
        Be conversational, helpful, and focus on resolution.
        """

        return base_prompt

    def get_or_create_conversation_with_tone(
        self, conversation_id: str, tone: str
    ) -> ConversationChain:
        """Get or create conversation chain with appropriate tone."""

        if conversation_id not in self.conversations:
            memory = ConversationBufferMemory(return_messages=True)

            # Create LLM with tone-specific system prompt
            system_prompt = self.tone_prompts.get(
                tone, self.tone_prompts["helpful_friendly"]
            )

            if self.llm_available:
                # Create new LLM instance with system message
                llm_with_tone = ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo")
            else:
                llm_with_tone = self.llm

            chain = ConversationChain(llm=llm_with_tone, memory=memory, verbose=True)

            self.conversations[conversation_id] = chain

        return self.conversations[conversation_id]

    def extract_solution_summary(self, response: str) -> str:
        """Extract key solution points for tracking."""
        # Simple extraction - could be enhanced with NLP
        sentences = response.split(".")
        action_sentences = [
            s.strip()
            for s in sentences
            if any(
                action in s.lower()
                for action in ["try", "click", "go to", "check", "update", "restart"]
            )
        ]
        return ". ".join(action_sentences[:2]) if action_sentences else response[:100]

    async def handle_follow_up(
        self, conversation_id: str, message: str, context: ConversationContext
    ) -> Dict[str, Any]:
        """Handle follow-up messages with empathy and alternative solutions."""

        # Get conversation chain with appropriate tone
        chain = self.get_or_create_conversation_with_tone(
            conversation_id, context.preferred_tone
        )

        # Create follow-up aware prompt
        follow_up_prompt = self.create_follow_up_prompt(message, context)

        try:
            # Generate response with full conversation context
            if self.llm_available:
                response = await chain.arun(follow_up_prompt)
            else:
                response = self.create_empathetic_fallback_text(context)

            return {
                "answer": response,
                "agent": "Enhanced AI Assistant",
                "agent_type": "conversational",
                "answer_type": "follow_up_response",
                "intent": "follow_up_assistance",
                "intent_data": {
                    "is_follow_up": True,
                    "attempt_count": context.attempt_count,
                    "frustration_level": context.frustration_level,
                    "previous_solutions": len(context.resolution_attempts),
                },
                "solution_summary": self.extract_solution_summary(response),
                "conversation_flow": "follow_up_adaptive",
            }

        except Exception as e:
            logger.error(f"Follow-up processing error: {str(e)}")
            return self.create_empathetic_fallback(context)

    def create_empathetic_fallback_text(self, context: ConversationContext) -> str:
        """Create empathetic fallback text when LLM is not available."""
        if context.frustration_level >= 6:
            return (
                "I understand this has been frustrating. Let me try a different approach to help you. "
                "Could you tell me more specifically what happened when you tried the previous suggestion?"
            )
        else:
            return (
                "I see that the previous solution didn't work as expected. Let me suggest a different approach. "
                "Can you tell me more details about what you're experiencing?"
            )

    def create_empathetic_fallback(
        self, context: ConversationContext
    ) -> Dict[str, Any]:
        """Create empathetic fallback response for errors."""

        if context.frustration_level >= 6:
            message = (
                "I understand this has been frustrating. Let me connect you with "
                "a human agent who can provide more personalized assistance."
            )
        else:
            message = (
                "I apologize that my previous suggestion didn't work as expected. "
                "Let me try a different approach to help resolve this issue."
            )

        return {
            "answer": message,
            "agent": "Empathy Engine",
            "agent_type": "supportive",
            "answer_type": "empathetic_fallback",
            "intent": "support",
            "intent_data": {"empathy_triggered": True},
            "conversation_flow": "empathetic_support",
        }

    def update_context(
        self, conversation_id: str, message: str, solution_offered: Optional[str] = None
    ) -> ConversationContext:
        """Update conversation context based on latest interaction."""
        context = self.conversation_contexts.get(conversation_id)
        if not context:
            return None

        # Detect follow-up
        is_follow_up = self.detect_follow_up(message, context)

        if is_follow_up:
            context.current_state = ConversationState.FOLLOW_UP
            context.attempt_count += 1
            context.frustration_level = self.detect_frustration_level(message, context)

            # Track failed solution
            if context.last_solution_offered:
                context.resolution_attempts.append(
                    {
                        "solution": context.last_solution_offered,
                        "timestamp": datetime.utcnow().isoformat(),
                        "outcome": "ineffective",
                        "user_feedback": message,
                    }
                )

        # Update solution tracking
        if solution_offered:
            context.last_solution_offered = solution_offered
            if not is_follow_up:
                context.current_state = ConversationState.PROBLEM_SOLVING

        context.preferred_tone = self.determine_tone(context)

        return context

    def get_or_create_conversation(self, conversation_id: str) -> ConversationChain:
        """
        Retrieve existing conversation or create new one for session management.

        Each conversation maintains its own memory buffer to preserve context
        across multiple message exchanges. This enables the AI to reference
        previous parts of the conversation for more coherent responses.

        Args:
            conversation_id: Unique identifier for the conversation session

        Returns:
            ConversationChain: LangChain conversation object with memory
        """
        if conversation_id not in self.conversations:
            # Create new conversation with buffer memory for context preservation
            memory = ConversationBufferMemory()
            chain = ConversationChain(
                llm=self.llm,
                memory=memory,
                verbose=True,  # Enable verbose mode for debugging
            )
            self.conversations[conversation_id] = chain
        return self.conversations[conversation_id]

    def normalize(self, text: str) -> str:
        """
        Normalize text for consistent matching across the knowledge base.

        This function standardizes text by:
        - Converting to lowercase
        - Removing punctuation and special characters
        - Converting underscores to spaces
        - Stripping whitespace

        Args:
            text: Raw text to normalize

        Returns:
            str: Normalized text suitable for matching
        """
        return re.sub(r"[^a-z0-9 ]", "", text.lower().replace("_", " ")).strip()

    def tokenize(self, text: str) -> set:
        """
        Tokenize normalized text into a set of unique words.

        This creates a set of tokens that can be used for overlap-based
        matching between user queries and knowledge base entries.

        Args:
            text: Text to tokenize

        Returns:
            set: Set of unique tokens from the text
        """
        return set(self.normalize(text).split())

    def search_agent_kb(self, agent: str, message: str) -> Optional[Dict]:
        """
        Search the specified agent's knowledge base for matching responses.

        This method implements a multi-layered search strategy:
        1. Direct category name matching
        2. Token overlap between query and category names
        3. Keyword matching against response keywords
        4. Scoring based on token overlap for ranking

        The search prioritizes exact matches and uses token overlap
        for fuzzy matching when exact matches aren't found.

        Args:
            agent: Agent type (tech_support, billing, general)
            message: User's message to search for

        Returns:
            Optional[Dict]: Best matching response or None if no match found
        """
        # Get the knowledge base for the specified agent
        agent_kb = self.kb.get(agent, {}).get("categories", {})
        best_match = None
        best_score = 0

        # Normalize the user's message for consistent matching
        message_norm = self.normalize(message)
        message_tokens = self.tokenize(message)

        # First pass: Look for direct category name matches
        for cat_name, cat in agent_kb.items():
            cat_name_norm = self.normalize(cat_name)
            cat_name_tokens = self.tokenize(cat_name)

            # Check for direct category name match or token overlap
            if (
                cat_name_norm in message_norm
                or message_norm in cat_name_norm
                or cat_name_tokens & message_tokens
            ):

                # Return first response from matching category
                if cat["responses"]:
                    return cat["responses"][0]

            # Second pass: Score responses based on keyword overlap
            for resp in cat["responses"]:
                score = 0

                # Calculate score based on keyword token overlap
                for kw in resp["keywords"]:
                    kw_tokens = self.tokenize(kw)
                    if kw_tokens & message_tokens:
                        score += 1

                # Track the best scoring response
                if score > best_score:
                    best_score = score
                    best_match = resp

        return best_match

    def simple_agent_routing(self, message: str) -> str:
        """
        Simple keyword-based agent routing when intent service is unavailable.

        This method provides a fallback routing mechanism that doesn't require
        LLM-based intent classification. It uses keyword matching to determine
        the most appropriate agent type.

        Args:
            message: User's input message

        Returns:
            str: Agent type based on keyword matching
        """
        message_lower = message.lower()

        # Define keyword patterns for each agent type
        tech_keywords = [
            "internet",
            "wifi",
            "modem",
            "router",
            "connection",
            "slow",
            "outage",
            "not working",
            "down",
            "offline",
            "reset",
            "restart",
            "troubleshoot",
            "technical",
            "equipment",
            "cable",
            "signal",
            "speed",
        ]

        billing_keywords = [
            "bill",
            "billing",
            "payment",
            "charge",
            "cost",
            "price",
            "fee",
            "account",
            "subscription",
            "plan",
            "upgrade",
            "downgrade",
            "cancel",
            "refund",
            "credit",
            "balance",
            "due",
            "overdue",
            "autopay",
        ]

        # Count matches for each category
        tech_score = sum(1 for keyword in tech_keywords if keyword in message_lower)
        billing_score = sum(
            1 for keyword in billing_keywords if keyword in message_lower
        )

        # Route based on highest score
        if tech_score > billing_score:
            return "tech_support"
        elif billing_score > 0:
            return "billing"
        else:
            return "general"

    async def coordinator(
        self, conversation_id: str, message: str, db_session=None
    ) -> Dict:
        """
        Enhanced coordination method with natural conversational flow.

        This method now includes:
        - Follow-up detection and handling
        - Context-aware tone adaptation
        - Frustration level monitoring
        - Business metrics tracking
        """
        start_time = time.time()

        try:
            # Get or create conversation context
            context = self.get_or_create_context(conversation_id, conversation_id)

            # Detect if this is a follow-up
            is_follow_up = self.detect_follow_up(message, context)

            # Determine response strategy
            if is_follow_up:
                response_data = await self.handle_follow_up(
                    conversation_id, message, context
                )
            else:
                # Use existing coordinator logic but with context awareness
                response_data = await self.handle_regular_message(
                    conversation_id, message, context
                )

            # Update context
            solution_offered = response_data.get("solution_summary")
            self.update_context(conversation_id, message, solution_offered)

            # Calculate metrics
            processing_time = (time.time() - start_time) * 1000

            # Enhanced response with metrics
            response_data["conversation_metrics"] = {
                "processing_time_ms": processing_time,
                "is_follow_up": is_follow_up,
                "attempt_count": context.attempt_count,
                "frustration_level": context.frustration_level,
                "conversation_state": context.current_state.value,
                "tone_used": context.preferred_tone,
            }

            return response_data

        except Exception as e:
            logger.error(f"Enhanced coordinator error: {str(e)}")
            return {
                "answer": "I'm here to help with your Xfinity services. You can ask me about internet issues, billing questions, or general support.",
                "agent": "General Support",
                "agent_type": "general",
                "answer_type": "error_fallback",
                "intent": "general",
                "intent_data": {"confidence": 0.0, "keywords": []},
                "conversation_metrics": {
                    "processing_time_ms": (time.time() - start_time) * 1000,
                    "is_follow_up": False,
                    "attempt_count": 0,
                    "frustration_level": 0,
                    "conversation_state": "error",
                    "tone_used": "helpful_friendly",
                },
            }

    async def handle_regular_message(
        self, conversation_id: str, message: str, context: ConversationContext
    ) -> Dict[str, Any]:
        """Handle regular messages through normal flow with enhanced context."""

        # Step 1: Classify message intent and route to appropriate agent
        if self.intent_service_available:
            try:
                intent, intent_data = await self.intent_service.route_message(message)

                # Map intent to agent type for knowledge base lookup
                if intent == "technical_support":
                    agent = "tech_support"
                elif intent == "billing":
                    agent = "billing"
                else:
                    agent = "general"
            except Exception as e:
                logger.error(f"Intent classification failed: {e}")
                # Fallback to simple keyword-based routing
                agent = self.simple_agent_routing(message)
                intent = agent
                intent_data = {"confidence": 0.5, "keywords": []}
        else:
            # Use simple keyword-based routing when intent service is unavailable
            agent = self.simple_agent_routing(message)
            intent = agent
            intent_data = {"confidence": 0.5, "keywords": []}

        # Step 2: Search knowledge base for relevant response
        kb_response = self.search_agent_kb(agent, message)

        if kb_response:
            # Use knowledge base response if found
            answer = kb_response["content"]
            answer_type = kb_response["type"]
        else:
            # Search all agents if no match found in primary agent
            for fallback_agent in ["tech_support", "billing", "general"]:
                if fallback_agent != agent:
                    kb_response = self.search_agent_kb(fallback_agent, message)
                    if kb_response:
                        answer = kb_response["content"]
                        answer_type = kb_response["type"]
                        agent = fallback_agent  # Update agent to the one that found the match
                        break

        if not kb_response:
            # Step 3: Fallback to LLM for complex queries with context-aware tone
            if self.llm_available:
                try:
                    chain = self.get_or_create_conversation_with_tone(
                        conversation_id, context.preferred_tone
                    )
                    answer = await chain.arun(message)
                    answer_type = "llm_generated"
                except Exception as e:
                    # Handle rate limiting and other LLM errors gracefully
                    logger.error(f"LLM error: {e}")
                    if "rate limit" in str(e).lower() or "429" in str(e):
                        answer = "I'm here to help with your Xfinity services. I can assist with internet issues, billing questions, equipment troubleshooting, and general support. What specific problem are you experiencing?"
                    else:
                        answer = "I found some information that might help you. Could you be more specific about what you're looking for?"
                    answer_type = "kb_fallback"
            else:
                # LLM not available, provide helpful fallback
                answer = "I'm here to help with your Xfinity services. I can assist with internet issues, billing questions, equipment troubleshooting, and general support. What specific problem are you experiencing?"
                answer_type = "kb_fallback"

        return {
            "answer": answer,
            "agent": self.kb.get(agent, {}).get("name", "Support Agent"),
            "agent_type": agent,
            "answer_type": answer_type,
            "intent": intent,
            "intent_data": intent_data,
            "solution_summary": self.extract_solution_summary(answer),
            "conversation_flow": "regular_flow",
        }
        """
        Main coordination method orchestrating the complete response flow.

        This method implements the core business logic for handling user messages:
        1. Intent classification and agent routing
        2. Knowledge base search for relevant responses
        3. LLM fallback for complex or unmatched queries
        4. Response packaging with metadata
        5. Database persistence for conversation history
        6. Error handling and graceful degradation

        The coordinator ensures that every user message receives a response,
        either from the knowledge base or from the LLM, with appropriate
        metadata for frontend display and analytics.

        Args:
            conversation_id: Unique session identifier
            message: User's input message
            db_session: Database session for persistence

        Returns:
            Dict: Complete response with answer, agent info, and metadata
        """
        try:
            # Initialize repository if database session provided
            chat_repo = ChatRepository(db_session) if db_session else None

            # Store user message in database if available
            if chat_repo:
                try:
                    await chat_repo.get_or_create_conversation(conversation_id)
                    await chat_repo.add_message(
                        conversation_id=conversation_id,
                        content=message,
                        sender="user",
                        role="user",
                    )
                except Exception as e:
                    print(f"Database error storing user message: {e}")
            # Step 1: Classify message intent and route to appropriate agent
            if self.intent_service_available:
                try:
                    intent, intent_data = await self.intent_service.route_message(
                        message
                    )

                    # Map intent to agent type for knowledge base lookup
                    if intent == "technical_support":
                        agent = "tech_support"
                    elif intent == "billing":
                        agent = "billing"
                    else:
                        agent = "general"
                except Exception as e:
                    print(f"Intent classification failed: {e}")
                    # Fallback to simple keyword-based routing
                    agent = self.simple_agent_routing(message)
                    intent = agent
                    intent_data = {"confidence": 0.5, "keywords": []}
            else:
                # Use simple keyword-based routing when intent service is unavailable
                agent = self.simple_agent_routing(message)
                intent = agent
                intent_data = {"confidence": 0.5, "keywords": []}

            # Step 2: Search knowledge base for relevant response
            kb_response = self.search_agent_kb(agent, message)

            if kb_response:
                # Use knowledge base response if found
                answer = kb_response["content"]
                answer_type = kb_response["type"]
            else:
                # Search all agents if no match found in primary agent
                for fallback_agent in ["tech_support", "billing", "general"]:
                    if fallback_agent != agent:
                        kb_response = self.search_agent_kb(fallback_agent, message)
                        if kb_response:
                            answer = kb_response["content"]
                            answer_type = kb_response["type"]
                            agent = fallback_agent  # Update agent to the one that found the match
                            break

                if not kb_response:
                    # Step 3: Fallback to LLM for complex queries with error handling
                    if self.llm_available:
                        try:
                            chain = self.get_or_create_conversation(conversation_id)
                            answer = await chain.arun(message)
                            answer_type = "llm_generated"
                        except Exception as e:
                            # Handle rate limiting and other LLM errors gracefully
                            print(f"LLM error: {e}")
                            if "rate limit" in str(e).lower() or "429" in str(e):
                                answer = "I'm here to help with your Xfinity services. I can assist with internet issues, billing questions, equipment troubleshooting, and general support. What specific problem are you experiencing?"
                            else:
                                answer = "I found some information that might help you. Could you be more specific about what you're looking for?"
                            answer_type = "kb_fallback"
                    else:
                        # LLM not available, provide helpful fallback
                        answer = "I'm here to help with your Xfinity services. I can assist with internet issues, billing questions, equipment troubleshooting, and general support. What specific problem are you experiencing?"
                        answer_type = "kb_fallback"

            # Step 4: Store AI response in database if available
            response_data = {
                "answer": answer,
                "agent": self.kb[agent]["name"],
                "agent_type": agent,
                "answer_type": answer_type,
                "intent": intent,
                "intent_data": intent_data,
            }

            if chat_repo:
                try:
                    await chat_repo.add_message(
                        conversation_id=conversation_id,
                        content=answer,
                        sender="agent",
                        role="assistant",
                        agent=self.kb[agent]["name"],
                        agent_type=agent,
                        answer_type=answer_type,
                        intent=intent,
                        intent_data=intent_data,
                    )
                except Exception as e:
                    print(f"Database error storing AI response: {e}")

            # Step 5: Package and return response with complete metadata
            return response_data
        except Exception as e:
            print(f"Coordinator error: {e}")
            # Ultimate fallback response
            return {
                "answer": "I'm here to help with your Xfinity services. You can ask me about internet issues, billing questions, or general support.",
                "agent": "General Support",
                "agent_type": "general",
                "answer_type": "error_fallback",
                "intent": "general",
                "intent_data": {"confidence": 0.0, "keywords": []},
            }

    async def process_message(
        self, conversation_id: str, message: str, db_session=None
    ) -> Dict:
        """
        Public interface for processing user messages.

        This method serves as the main entry point for the chat service,
        providing a clean interface for external callers while delegating
        the complex orchestration logic to the coordinator method.

        Args:
            conversation_id: Unique session identifier
            message: User's input message
            db_session: Database session for persistence

        Returns:
            Dict: Complete response with answer and metadata
        """
        return await self.coordinator(conversation_id, message, db_session)

    def get_conversation_history(self, conversation_id: str) -> List[Dict]:
        """
        Retrieve conversation history for a specific session.

        This method provides access to the conversation memory, allowing
        for conversation replay, analytics, and context restoration.
        Returns empty list if conversation doesn't exist.

        Args:
            conversation_id: Unique session identifier

        Returns:
            List[Dict]: List of messages in the conversation
        """
        if conversation_id not in self.conversations:
            return []
        memory = self.conversations[conversation_id].memory
        return memory.chat_memory.messages
