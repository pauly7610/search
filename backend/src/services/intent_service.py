from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from typing import Dict, List, Tuple
import json

class IntentService:
    def __init__(self):
        self.llm = ChatOpenAI(
            temperature=0,
            model_name="gpt-3.5-turbo"
        )
        
        self.intent_prompt = PromptTemplate(
            input_variables=["message"],
            template="""
            Analyze the following message and classify it into one of these categories:
            - general_inquiry
            - technical_support
            - billing
            - feature_request
            - complaint
            - other

            Message: {message}

            Respond with a JSON object containing:
            {
                "intent": "category",
                "confidence": 0.0-1.0,
                "keywords": ["relevant", "words"]
            }
            """
        )

    async def classify_intent(self, message: str) -> Dict:
        chain = self.intent_prompt | self.llm
        result = await chain.ainvoke({"message": message})
        try:
            return json.loads(result.content)
        except:
            return {
                "intent": "other",
                "confidence": 0.0,
                "keywords": []
            }

    async def route_message(self, message: str) -> Tuple[str, Dict]:
        intent_data = await self.classify_intent(message)
        
        # Route based on intent
        if intent_data["intent"] == "technical_support":
            return "technical_support", intent_data
        elif intent_data["intent"] == "billing":
            return "billing", intent_data
        elif intent_data["intent"] == "feature_request":
            return "feature_request", intent_data
        else:
            return "general", intent_data 