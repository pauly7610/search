# Xfinity Agentic AI Backend

This backend powers an agentic AI customer support demo for an Xfinity-style telecom/ISP company. It features multi-agent routing, a rich knowledge base, analytics, and best-practice monitoring with Prometheus and Grafana.

## Features

- **Agentic AI:** Multi-agent system (Tech Support, Billing, General) with intent-based routing
- **Knowledge Base:** Rich, structured Xfinity support knowledge base (JSON)
- **LLM Integration:** Uses OpenAI GPT for fallback and context-aware answers
- **Analytics:** Tracks chat volume, response times, satisfaction, and intent distribution
- **Monitoring:** Prometheus metrics at `/metrics`, exporters for Postgres and node
- **WebSocket & REST API:** Real-time and traditional chat endpoints

## Setup

### 1. Install Python dependencies

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file or set these in your environment:

```
OPENAI_API_KEY=your-openai-key
```

### 3. Run the Backend

#### Local (dev, hot reload):

```bash
cd src
uvicorn src.main:app --reload
```

#### Docker:

```bash
docker build -t xfinity-agent-backend .
docker run -p 8000:8000 xfinity-agent-backend
```

## API Endpoints

- `POST /api/v1/chat/messages` — Send a message, get agentic AI response
- `GET /api/v1/chat/conversations` — List conversations
- `GET /api/v1/chat/conversations/{id}` — Get conversation by ID
- `GET /api/v1/analytics/overview` — Analytics summary
- `POST /api/v1/feedback` — Submit feedback
- `GET /api/v1/health` — Health check
- `WS /api/v1/chat/ws` — Real-time chat
- `GET /metrics` — Prometheus metrics endpoint

## Monitoring & Observability

- **Prometheus** scrapes `/metrics` on backend, plus Postgres and node exporters
- **Docker Compose** includes `postgres-exporter` and `node-exporter` for full-stack monitoring
- **Grafana** dashboards for backend and Postgres health
- **Alerting** for latency, error rate, and DB health

## Directory Structure

```
backend/
  src/
    api/           # FastAPI route handlers
    services/      # Core business logic (chat, intent, analytics)
    models/        # (Optional) DB models
    migrations/    # (Optional) DB migrations
    config/        # (Optional) Config files
    agents/        # (Optional) Custom agent logic
    graph/         # (Optional) LangGraph configs
    xfinity_knowledge_base.json  # Main knowledge base
    main.py        # FastAPI app entry point
  requirements.txt
  Dockerfile
```

## How It Works

- User message → Intent classified → Routed to correct agent
- Agent searches its KB section for best answer (keyword match)
- If no KB match, falls back to LLM (GPT)
- Response includes agent name, answer type, and intent for UI display

## Extending

- **Add new agents:** Add to `xfinity_knowledge_base.json` under `agents`
- **Add new FAQs:** Add to the relevant agent's `categories`
- **Change LLM:** Edit `ChatService` in `services/chat_service.py`
- **Add analytics:** Extend `services/analytics_service.py`

## Example API Usage

```bash
curl -X POST http://localhost:8000/api/v1/chat/messages \
  -H 'Content-Type: application/json' \
  -d '{"id": "demo-1", "content": "How do I reset my modem?", "role": "user", "timestamp": "2025-06-16T00:00:00Z"}'
```

---

For more, see the code in `src/services/` and `src/api/`.
