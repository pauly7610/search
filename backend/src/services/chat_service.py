import json
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain_openai import ChatOpenAI
from typing import Dict, List, Optional
import os
from src.services.intent_service import IntentService
import re

class ChatService:
    def __init__(self):
        self.conversations: Dict[str, ConversationChain] = {}
        self.llm = ChatOpenAI(
            temperature=0.7,
            model_name="gpt-3.5-turbo"
        )
        # Load knowledge base
        kb_path = os.path.join(os.path.dirname(__file__), '../xfinity_knowledge_base.json')
        with open(kb_path, 'r') as f:
            self.kb = json.load(f)["knowledge_base"]["agents"]
        self.intent_service = IntentService()

    def get_or_create_conversation(self, conversation_id: str) -> ConversationChain:
        if conversation_id not in self.conversations:
            memory = ConversationBufferMemory()
            chain = ConversationChain(
                llm=self.llm,
                memory=memory,
                verbose=True
            )
            self.conversations[conversation_id] = chain
        return self.conversations[conversation_id]

    def normalize(self, text: str) -> str:
        return re.sub(r'[^a-z0-9 ]', '', text.lower().replace('_', ' ')).strip()

    def tokenize(self, text: str) -> set:
        return set(self.normalize(text).split())

    def search_agent_kb(self, agent: str, message: str) -> Optional[Dict]:
        """Search the agent's knowledge base for the best matching response, including category name match and token overlap."""
        agent_kb = self.kb.get(agent, {}).get("categories", {})
        best_match = None
        best_score = 0
        message_norm = self.normalize(message)
        message_tokens = self.tokenize(message)
        for cat_name, cat in agent_kb.items():
            cat_name_norm = self.normalize(cat_name)
            cat_name_tokens = self.tokenize(cat_name)
            # Direct category name match or token overlap
            if cat_name_norm in message_norm or message_norm in cat_name_norm or cat_name_tokens & message_tokens:
                if cat["responses"]:
                    return cat["responses"][0]
            for resp in cat["responses"]:
                # Token overlap scoring
                score = 0
                for kw in resp["keywords"]:
                    kw_tokens = self.tokenize(kw)
                    if kw_tokens & message_tokens:
                        score += 1
                if score > best_score:
                    best_score = score
                    best_match = resp
        return best_match

    async def coordinator(self, conversation_id: str, message: str) -> Dict:
        # Use intent service to classify and route
        intent, intent_data = await self.intent_service.route_message(message)
        if intent == "technical_support":
            agent = "tech_support"
        elif intent == "billing":
            agent = "billing"
        else:
            agent = "general"
        kb_response = self.search_agent_kb(agent, message)
        if kb_response:
            answer = kb_response["content"]
            answer_type = kb_response["type"]
        else:
            # Fallback to LLM if no KB match, with robust error handling
            try:
                chain = self.get_or_create_conversation(conversation_id)
                answer = await chain.arun(message)
                answer_type = "llm_generated"
            except Exception as e:
                answer = "Sorry, I can't answer that right now. Please try again later."
                answer_type = "error"
        return {
            "answer": answer,
            "agent": self.kb[agent]["name"],
            "agent_type": agent,
            "answer_type": answer_type,
            "intent": intent,
            "intent_data": intent_data
        }

    async def process_message(self, conversation_id: str, message: str) -> Dict:
        return await self.coordinator(conversation_id, message)

    def get_conversation_history(self, conversation_id: str) -> List[Dict]:
        if conversation_id not in self.conversations:
            return []
        memory = self.conversations[conversation_id].memory
        return memory.chat_memory.messages 