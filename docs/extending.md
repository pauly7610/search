# Extending the System

## Backend

### Add a New Agent

1. Edit `backend/src/xfinity_knowledge_base.json`
2. Add a new agent under `knowledge_base.agents` with a unique key
3. Add categories and responses as needed
4. Update `intent_service.py` to recognize the new intent (if needed)
5. Update `chat_service.py` routing logic if you want custom routing

### Add New FAQs or Responses

- Add new categories or responses under the relevant agent in the knowledge base JSON
- Use clear questions, concise answers, and relevant keywords

### Change the LLM

- Edit the `ChatOpenAI` config in `services/chat_service.py`
- You can swap models, change temperature, or use a different provider

### Add/Extend Analytics

- Edit or extend `services/analytics_service.py`
- Add new metrics, trends, or data collection as needed

## Frontend

### Add New UI Features

- Create new components in `src/components/`
- Use or extend hooks in `src/hooks/`

### Customize Chat/Analytics

- Edit `useAIChat`, `useAnalytics`, or related hooks
- Update `MessageBubble` to display new metadata

### Change Theme/Branding

- Edit Tailwind config and CSS in `src/styles/`
- Update layout and color scheme in `src/components/layout/`

## Example: Add a "Sales Agent"

1. Add `sales` agent to the knowledge base
2. Add intent to `intent_service.py` prompt
3. Update `chat_service.py` to route `sales` intent to the new agent
4. Add UI display for "Sales Agent" in the frontend

---

For more, see the other docs in this folder and the main READMEs.
