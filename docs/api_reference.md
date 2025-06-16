# API Reference

## Chat Endpoints

### POST `/api/v1/chat/messages`

Send a user message and receive an agentic AI response.

**Request:**

```json
{
  "id": "string",
  "content": "How do I reset my modem?",
  "role": "user",
  "timestamp": "2025-06-16T00:00:00Z"
}
```

**Response:**

```json
{
  "id": "string",
  "content": "To reset your Xfinity modem...",
  "role": "assistant",
  "timestamp": "...",
  "agent": "Tech Support Agent",
  "agent_type": "tech_support",
  "answer_type": "knowledge_base",
  "intent": "technical_support",
  "intent_data": { "intent": "technical_support", ... }
}
```

### WebSocket `/api/v1/chat/ws`

- Connect and send `{ "content": "..." }` messages
- Receive agentic responses as above

## Analytics Endpoints

### GET `/api/v1/analytics/overview`

Returns analytics summary:

```json
{
  "totalConversations": 123,
  "averageResponseTime": "2.5s",
  "satisfactionRate": "92%",
  "activeUsers": 45,
  "conversationVolume": [...],
  "responseTimeTrend": [...],
  "satisfactionTrend": [...],
  "intentDistribution": { "tech_support": 50, ... }
}
```

## Feedback Endpoint

### POST `/api/v1/feedback`

Submit feedback on a message.

```json
{
  "messageId": "string",
  "rating": 5,
  "comment": "Very helpful!",
  "timestamp": "..."
}
```

## Health

- `GET /api/v1/health` — Returns `{ "status": "ok" }`

---

See backend/README.md for more details and example usage.
