"""
Chat Service Module for Multi-Agent Customer Support System

This module implements the core chat functionality with intelligent agent routing,
knowledge base search, and conversation management. It serves as the orchestrator
for the AI-powered customer support system.

Key Components:
- Multi-agent routing based on intent classification
- Knowledge base search with fuzzy matching
- Conversation memory management
- LLM fallback for complex queries
- Robust error handling and recovery

Architecture:
The service follows a coordinator pattern where incoming messages are:
1. Classified by intent (technical, billing, general)
2. Routed to appropriate specialized agents
3. Matched against knowledge base responses
4. Augmented with LLM responses when needed
5. Returned with full context and metadata
"""

import json
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain_openai import ChatOpenAI
from typing import Dict, List, Optional
import os
from src.services.intent_service import IntentService
import re

class ChatService:
    """
    Main chat service orchestrating multi-agent conversations.
    
    This service manages the complete conversation lifecycle including:
    - Agent selection and routing
    - Knowledge base searching
    - LLM integration for complex queries
    - Conversation state management
    - Response formatting and metadata
    
    The service maintains separate conversation chains for each session
    to preserve context across multiple message exchanges.
    """
    
    def __init__(self):
        """
        Initialize the chat service with all necessary components.
        
        Sets up:
        - LLM client for complex query handling
        - Knowledge base loading and indexing
        - Intent classification service
        - Conversation storage
        """
        # Dictionary to store active conversation chains by session ID
        # This allows for persistent conversation context across messages
        self.conversations: Dict[str, ConversationChain] = {}
        
        # Load and parse the knowledge base from JSON file
        # The knowledge base contains structured responses for different support categories
        kb_path = os.path.join(os.path.dirname(__file__), '../xfinity_knowledge_base.json')
        with open(kb_path, 'r') as f:
            self.kb = json.load(f)["knowledge_base"]["agents"]
        
        # Initialize LLM with moderate temperature for balanced creativity (optional)
        # Temperature 0.7 provides good balance between deterministic and creative responses
        try:
            self.llm = ChatOpenAI(
                temperature=0.7,
                model_name="gpt-3.5-turbo"
            )
            self.llm_available = True
        except Exception as e:
            print(f"LLM initialization failed: {e}")
            self.llm = None
            self.llm_available = False
        
        # Initialize local intent classification service for message routing
        try:
            from src.services.local_intent_service import LocalIntentService
            self.intent_service = LocalIntentService()
            self.intent_service_available = True
            print("Local intent service initialized successfully")
        except Exception as e:
            print(f"Local intent service initialization failed: {e}")
            self.intent_service = None
            self.intent_service_available = False

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
                verbose=True  # Enable verbose mode for debugging
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
        return re.sub(r'[^a-z0-9 ]', '', text.lower().replace('_', ' ')).strip()

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
            if (cat_name_norm in message_norm or 
                message_norm in cat_name_norm or 
                cat_name_tokens & message_tokens):
                
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
            'internet', 'wifi', 'modem', 'router', 'connection', 'slow', 'outage',
            'not working', 'down', 'offline', 'reset', 'restart', 'troubleshoot',
            'technical', 'equipment', 'cable', 'signal', 'speed'
        ]
        
        billing_keywords = [
            'bill', 'billing', 'payment', 'charge', 'cost', 'price', 'fee',
            'account', 'subscription', 'plan', 'upgrade', 'downgrade', 'cancel',
            'refund', 'credit', 'balance', 'due', 'overdue', 'autopay'
        ]
        
        # Count matches for each category
        tech_score = sum(1 for keyword in tech_keywords if keyword in message_lower)
        billing_score = sum(1 for keyword in billing_keywords if keyword in message_lower)
        
        # Route based on highest score
        if tech_score > billing_score:
            return "tech_support"
        elif billing_score > 0:
            return "billing"
        else:
            return "general"

    async def coordinator(self, conversation_id: str, message: str) -> Dict:
        """
        Main coordination method orchestrating the complete response flow.
        
        This method implements the core business logic for handling user messages:
        1. Intent classification and agent routing
        2. Knowledge base search for relevant responses
        3. LLM fallback for complex or unmatched queries
        4. Response packaging with metadata
        5. Error handling and graceful degradation
        
        The coordinator ensures that every user message receives a response,
        either from the knowledge base or from the LLM, with appropriate
        metadata for frontend display and analytics.
        
        Args:
            conversation_id: Unique session identifier
            message: User's input message
            
        Returns:
            Dict: Complete response with answer, agent info, and metadata
        """
        try:
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
            
            # Step 4: Package response with complete metadata
            return {
                "answer": answer,
                "agent": self.kb[agent]["name"],
                "agent_type": agent,
                "answer_type": answer_type,
                "intent": intent,
                "intent_data": intent_data
            }
        except Exception as e:
            print(f"Coordinator error: {e}")
            # Ultimate fallback response
            return {
                "answer": "I'm here to help with your Xfinity services. You can ask me about internet issues, billing questions, or general support.",
                "agent": "General Support",
                "agent_type": "general",
                "answer_type": "error_fallback",
                "intent": "general",
                "intent_data": {"confidence": 0.0, "keywords": []}
            }

    async def process_message(self, conversation_id: str, message: str) -> Dict:
        """
        Public interface for processing user messages.
        
        This method serves as the main entry point for the chat service,
        providing a clean interface for external callers while delegating
        the complex orchestration logic to the coordinator method.
        
        Args:
            conversation_id: Unique session identifier
            message: User's input message
            
        Returns:
            Dict: Complete response with answer and metadata
        """
        return await self.coordinator(conversation_id, message)

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