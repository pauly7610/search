# Architecture Overview

## System Components

- **Backend (FastAPI, LangChain, OpenAI):**

  - Multi-agent system (Tech Support, Billing, General)
  - Intent classification and routing
  - Knowledge base search and LLM fallback
  - Analytics tracking
  - REST and WebSocket APIs

- **Frontend (React, Vite, Tailwind):**
  - Modern chat UI with agent/intent/source display
  - Analytics dashboard
  - Feedback and real-time updates

## Data Flow

1. **User sends a message** via chat UI (frontend)
2. **Backend receives message**
   - Classifies intent (tech support, billing, general, etc.)
   - Routes to the correct agent
   - Agent searches its section of the knowledge base for the best answer
   - If no KB match, falls back to LLM (GPT)
   - Returns answer + agent info + answer type + intent
3. **Frontend displays**
   - The answer
   - Which agent responded
   - Source (Knowledge Base or AI)
   - Detected intent

## Multi-Agent System

- Each agent is responsible for a domain (tech support, billing, general)
- Coordinator agent uses intent classification to route queries
- Agents can be extended or new ones added by updating the knowledge base and backend logic

## Knowledge Base

- Stored as structured JSON
- Each agent has its own categories and responses
- Supports keyword-based search for best match

## Analytics

- Tracks conversation volume, response times, satisfaction, and intent distribution
- Data available via `/api/v1/analytics/overview`

---

See other docs in this folder for more details on each component.
