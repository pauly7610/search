# Agent Routing & Intent Classification

## Overview

The backend uses a multi-agent system to route user queries to the most appropriate agent (Tech Support, Billing, General) based on intent classification.

## Flow

1. **User message received**
2. **Intent classified** using an LLM prompt (see `services/intent_service.py`)
   - Intents: `technical_support`, `billing`, `general_inquiry`, etc.
3. **Coordinator agent** routes the message to the correct agent:
   - `technical_support` → Tech Support Agent
   - `billing` → Billing Agent
   - Other/general → General Agent
4. **Agent searches its knowledge base section** for the best answer (keyword match)
5. **If no KB match, fallback to LLM** (GPT)
6. **Response includes** agent name, answer type, and intent for frontend display

## Customization

- **Add new intents:** Update the prompt in `intent_service.py` and add a new agent in the knowledge base
- **Change routing logic:** Edit the `coordinator` method in `chat_service.py`
- **Improve matching:** Replace or enhance the keyword match in `search_agent_kb` with semantic search or vector DB

## Extension Points

- Add more agents (e.g., Sales, Retention)
- Add more granular intents
- Integrate with external APIs for agent escalation

## Example

```python
# In chat_service.py
intent, intent_data = await self.intent_service.route_message(message)
if intent == "technical_support":
    agent = "tech_support"
elif intent == "billing":
    agent = "billing"
else:
    agent = "general"
```
