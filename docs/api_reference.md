# API Reference

## Overview

The Xfinity Agentic AI Platform provides comprehensive REST and **enhanced WebSocket APIs** for real-time customer support interactions. All endpoints support JSON request/response format with comprehensive error handling and **enterprise-grade WebSocket communication**.

## Base URLs

- **REST API**: `http://localhost:8000/api/v1`
- **Enhanced WebSocket**: `ws://localhost:8000/api/v1/chat/ws`
- **Client-Specific WebSocket**: `ws://localhost:8000/api/v1/chat/ws/{client_id}`
- **Business Intelligence**: `http://localhost:8000/api/v1/metrics`
- **Documentation**: `http://localhost:8000/docs` (Swagger UI)

## Enhanced Conversational Flow Features

### **Follow-up Detection Patterns**

The system automatically detects when customers indicate that previous solutions didn't work:

- **Pattern Recognition**: `"that didn't work"`, `"still not working"`, `"it's still broken"`, `"try something else"`
- **Contextual Responses**: Acknowledges failure with empathy instead of repeating solutions
- **Alternative Solutions**: Provides different troubleshooting approaches
- **Escalation Triggers**: Proactively offers human help when frustration is high

### **Adaptive Tone System**

The AI dynamically adjusts its communication style based on conversation context:

1. **helpful_friendly** (Default): Professional, solution-focused approach
2. **understanding_adaptive**: Acknowledges previous solution failures empathetically
3. **patient_alternative**: Offers different approaches when multiple attempts made
4. **empathetic_supportive**: Shows understanding for customer frustration
5. **empathetic_escalation**: Offers human agent assistance for high frustration

### **Frustration Detection Scale**

Customer emotional state is tracked on a 0-10 scale:

- **0-2**: Calm, neutral interaction
- **3-4**: Mild concern or impatience
- **5-6**: Moderate frustration detected
- **7-8**: High frustration - empathetic responses triggered
- **9-10**: Extreme frustration - automatic escalation recommendation

**Indicators tracked:**

- Caps lock usage (ALL CAPS text)
- Multiple punctuation marks (!!! or ???)
- Explicit frustration words ("frustrated", "angry", "annoyed")
- Conversation attempt count
- Solution failure patterns

## Authentication

```http
Authorization: Bearer <jwt_token>
```

## Enhanced Chat & WebSocket Endpoints

### **WebSocket Chat Interface**

#### **Connect to WebSocket (Auto-assign Client ID)**

```
WS /api/v1/chat/ws
```

**Features:**

- Automatic client ID generation
- Connection health monitoring
- Heartbeat keep-alive
- Automatic reconnection support

#### **Connect to WebSocket (Specific Client ID)**

```
WS /api/v1/chat/ws/{client_id}
```

**Parameters:**

- `client_id` (string): Unique client identifier for connection tracking

**Connection Features:**

- Client identification and tracking
- Connection metadata storage
- Message queue management
- Performance monitoring

#### **WebSocket Message Format**

**Send Message:**

```json
{
  "content": "My internet is not working",
  "metadata": {
    "timestamp": "2024-01-15T10:30:00Z",
    "user_agent": "Mozilla/5.0...",
    "session_id": "optional-session-id"
  }
}
```

**Receive Message (Enhanced with Conversational Flow):**

```json
{
  "id": "msg-123",
  "role": "assistant",
  "content": "I can help you troubleshoot your internet connection...",
  "agent": "Tech Support Agent",
  "agent_type": "tech_support",
  "intent": "connectivity_issues",
  "intent_data": {
    "confidence": 0.95,
    "matched_patterns": ["internet", "not working"],
    "agent_type": "tech_support"
  },
  "conversation_flow": {
    "is_follow_up": false,
    "frustration_level": 2,
    "tone": "helpful_friendly",
    "attempt_count": 1,
    "context_state": "initial"
  },
  "source": "knowledge_base",
  "timestamp": "2024-01-15T10:30:01Z",
  "client_id": "client-abc123",
  "response_time": 0.45
}
```

**Follow-up Response Example:**

```json
{
  "id": "msg-124",
  "role": "assistant",
  "content": "I understand that didn't work for you. Let me suggest a different approach. Have you checked if there are any service outages in your area?",
  "agent": "Tech Support Agent",
  "agent_type": "tech_support",
  "intent": "connectivity_issues",
  "intent_data": {
    "confidence": 0.87,
    "matched_patterns": ["that didn't work"],
    "agent_type": "tech_support"
  },
  "conversation_flow": {
    "is_follow_up": true,
    "frustration_level": 4,
    "tone": "understanding_adaptive",
    "attempt_count": 2,
    "context_state": "follow_up",
    "previous_solutions": ["modem_restart"]
  },
  "source": "knowledge_base",
  "timestamp": "2024-01-15T10:32:15Z",
  "client_id": "client-abc123",
  "response_time": 0.38
}
```

**Heartbeat Messages:**

```json
// Ping (sent by server)
{
  "type": "ping",
  "timestamp": "2024-01-15T10:30:00Z"
}

// Pong (sent by client)
{
  "type": "pong",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### **WebSocket Connection Statistics**

```http
GET /api/v1/chat/ws/stats
```

**Response:**

```json
{
  "active_connections": 25,
  "total_messages_sent": 1247,
  "average_messages_per_connection": 49.88,
  "connection_details": {
    "client-abc123": {
      "connected_at": "2024-01-15T10:00:00Z",
      "message_count": 15,
      "last_activity": "2024-01-15T10:29:45Z",
      "user_agent": "Mozilla/5.0...",
      "ip_address": "192.168.1.100"
    }
  },
  "queued_messages": 3
}
```

### **REST Chat Endpoints**

#### **Send Message**

```http
POST /api/v1/chat/messages
```

**Request:**

```json
{
  "content": "My bill seems too expensive this month",
  "context": {
    "user_id": "user-123",
    "session_id": "session-456"
  }
}
```

**Response:**

```json
{
  "id": "msg-789",
  "role": "assistant",
  "content": "I understand your concern about your bill. Let me help you review the charges...",
  "agent": "Billing Agent",
  "agent_type": "billing",
  "intent": "billing_inquiry",
  "intent_data": {
    "confidence": 0.92,
    "matched_patterns": ["bill", "expensive"],
    "agent_type": "billing"
  },
  "source": "knowledge_base",
  "timestamp": "2024-01-15T10:30:01Z",
  "response_time": 0.32,
  "conversation_id": "conv-123"
}
```

## Enhanced Knowledge Base Endpoints

#### **Semantic Search**

```http
GET /api/v1/knowledge/search?q={query}&agent={agent_type}&confidence_threshold={threshold}
```

**Parameters:**

- `q` (string, required): Search query
- `agent` (string, optional): Filter by agent type (`tech_support`, `billing`, `general`)
- `confidence_threshold` (float, optional): Minimum confidence score (0.0-1.0)

**Response:**

```json
{
  "results": [
    {
      "content": "To troubleshoot internet connectivity issues...",
      "category": "connectivity_issues",
      "agent": "tech_support",
      "confidence": 0.95,
      "matched_keywords": ["internet", "connectivity"],
      "response_time": 0.12
    }
  ],
  "total_results": 1,
  "search_time": 0.12,
  "query_preprocessing": {
    "original_query": "internet not working",
    "normalized_query": "internet not working",
    "detected_intent": "technical",
    "intent_confidence": 0.89
  }
}
```

## Enhanced Analytics & Business Intelligence Endpoints

#### **Conversation Quality Metrics**

```http
GET /api/v1/metrics/conversation-quality
```

**Response:**

```json
{
  "overall_metrics": {
    "total_conversations": 1250,
    "intent_resolution_rate": 0.84,
    "average_frustration_level": 2.3,
    "escalation_rate": 0.12,
    "follow_up_rate": 0.28
  },
  "tone_adaptation_analytics": {
    "helpful_friendly": { "usage": 0.45, "success_rate": 0.89 },
    "understanding_adaptive": { "usage": 0.23, "success_rate": 0.76 },
    "patient_alternative": { "usage": 0.18, "success_rate": 0.71 },
    "empathetic_supportive": { "usage": 0.1, "success_rate": 0.68 },
    "empathetic_escalation": { "usage": 0.04, "success_rate": 0.55 }
  },
  "frustration_trends": [
    {
      "time_period": "2024-01-15T10:00:00Z",
      "average_frustration": 2.1,
      "high_frustration_conversations": 8,
      "escalations_triggered": 3
    }
  ],
  "follow_up_patterns": {
    "that_didnt_work": 145,
    "still_not_working": 89,
    "try_something_else": 67,
    "resolution_after_followup": 0.73
  }
}
```

#### **Individual Conversation Flow Analysis**

```http
GET /api/v1/metrics/conversation-flow/{conversation_id}
```

**Response:**

```json
{
  "conversation_id": "conv-123",
  "flow_analysis": {
    "total_messages": 6,
    "follow_up_detected": true,
    "frustration_progression": [1, 2, 4, 3, 2, 1],
    "tone_progression": [
      "helpful_friendly",
      "understanding_adaptive",
      "patient_alternative",
      "empathetic_supportive",
      "understanding_adaptive",
      "helpful_friendly"
    ],
    "solutions_attempted": ["modem_restart", "check_cables", "speed_test"],
    "final_outcome": "resolved",
    "escalation_likelihood": 0.23
  },
  "recommendations": [
    "Customer showed good response to empathetic tone",
    "Multiple technical solutions were effective",
    "Low escalation risk - AI resolution successful"
  ],
  "business_insights": {
    "resolution_time": "12 minutes",
    "customer_satisfaction_predicted": 4.2,
    "agent_effectiveness": "high"
  }
}
```

#### **Intent Resolution Rate Analysis**

```http
GET /api/v1/metrics/intent-resolution-rate?days={time_window}&intent={specific_intent}
```

**Response:**

```json
{
  "time_window": "7 days",
  "resolution_rates": {
    "connectivity_issues": {
      "total_conversations": 234,
      "first_attempt_resolution": 0.68,
      "overall_resolution": 0.89,
      "average_attempts": 1.8,
      "escalation_rate": 0.11
    },
    "billing_inquiry": {
      "total_conversations": 156,
      "first_attempt_resolution": 0.79,
      "overall_resolution": 0.94,
      "average_attempts": 1.4,
      "escalation_rate": 0.06
    },
    "equipment_setup": {
      "total_conversations": 98,
      "first_attempt_resolution": 0.52,
      "overall_resolution": 0.82,
      "average_attempts": 2.3,
      "escalation_rate": 0.18
    }
  },
  "trends": [
    {
      "date": "2024-01-15",
      "overall_resolution_rate": 0.84,
      "improvement_from_previous": 0.03
    }
  ]
}
```

#### **Escalation Predictions**

```http
GET /api/v1/metrics/escalation-predictions?active_only=true
```

**Response:**

```json
{
  "predictions": [
    {
      "conversation_id": "conv-456",
      "escalation_likelihood": 0.78,
      "confidence": 0.91,
      "factors": ["high_frustration", "multiple_attempts", "solution_failure"],
      "recommendation": "offer_human_agent",
      "predicted_escalation_time": "within_5_minutes",
      "current_frustration_level": 7
    },
    {
      "conversation_id": "conv-789",
      "escalation_likelihood": 0.45,
      "confidence": 0.73,
      "factors": ["complex_intent", "solution_failure"],
      "recommendation": "continue_ai",
      "alternative_approaches": [
        "try_different_agent",
        "escalate_to_specialist_knowledge"
      ]
    }
  ],
  "summary": {
    "total_active_conversations": 42,
    "high_risk_conversations": 3,
    "medium_risk_conversations": 8,
    "proactive_interventions_available": 11
  }
}
```

#### **Analytics Overview with WebSocket & Conversation Metrics**

```http
GET /api/v1/analytics/overview
```

**Response:**

```json
{
  "chat_metrics": {
    "total_conversations": 1250,
    "messages_today": 340,
    "average_response_time": 0.45,
    "satisfaction_score": 4.2
  },
  "websocket_metrics": {
    "active_connections": 25,
    "total_connections_today": 156,
    "messages_per_second": 2.3,
    "connection_errors": 3,
    "average_connection_duration": 1245.5,
    "reconnection_rate": 0.02
  },
  "intent_distribution": {
    "technical": 45.2,
    "billing": 32.1,
    "general": 22.7
  },
  "agent_performance": {
    "tech_support": {
      "response_time": 0.38,
      "confidence": 0.91,
      "kb_hit_rate": 0.85
    },
    "billing": {
      "response_time": 0.42,
      "confidence": 0.88,
      "kb_hit_rate": 0.79
    },
    "general": {
      "response_time": 0.35,
      "confidence": 0.83,
      "kb_hit_rate": 0.72
    }
  }
}
```

#### **Intent Classification Analytics**

```http
GET /api/v1/analytics/intents?timeframe={period}&include_confidence=true
```

**Response:**

```json
{
  "intent_trends": [
    {
      "date": "2024-01-15",
      "technical": 45,
      "billing": 32,
      "general": 23,
      "average_confidence": {
        "technical": 0.89,
        "billing": 0.91,
        "general": 0.83
      }
    }
  ],
  "confidence_distribution": {
    "high_confidence": 78.5,
    "medium_confidence": 18.2,
    "low_confidence": 3.3
  },
  "pattern_performance": {
    "billing_patterns": {
      "accuracy": 0.94,
      "usage_count": 234
    },
    "technical_patterns": {
      "accuracy": 0.91,
      "usage_count": 345
    }
  }
}
```

## System Health Endpoints

#### **Enhanced Health Check**

```http
GET /api/v1/health
```

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "services": {
    "database": {
      "status": "healthy",
      "response_time": 0.05,
      "connection_pool": {
        "active": 5,
        "idle": 15,
        "total": 20
      }
    },
    "redis": {
      "status": "healthy",
      "response_time": 0.02,
      "memory_usage": "45MB"
    },
    "websocket": {
      "status": "healthy",
      "active_connections": 25,
      "total_messages": 1247,
      "error_rate": 0.001
    },
    "openai": {
      "status": "healthy",
      "response_time": 1.23,
      "rate_limit_remaining": 4850
    }
  },
  "system_metrics": {
    "cpu_usage": 23.5,
    "memory_usage": 67.2,
    "disk_usage": 45.1
  }
}
```

## Error Handling

### **HTTP Status Codes**

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `429` - Rate Limited
- `500` - Internal Server Error
- `503` - Service Unavailable

### **WebSocket Error Codes**

- `1000` - Normal Closure
- `1001` - Going Away
- `1002` - Protocol Error
- `1003` - Unsupported Data
- `1006` - Abnormal Closure
- `1011` - Internal Error
- `4000` - Authentication Error
- `4001` - Rate Limited
- `4002` - Invalid Message Format

### **Error Response Format**

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid message format",
    "details": {
      "field": "content",
      "issue": "Content cannot be empty"
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "req-123"
  }
}
```

## Rate Limiting

### **REST API Limits**

- **General endpoints**: 100 requests/minute
- **Chat endpoints**: 60 requests/minute
- **Analytics endpoints**: 30 requests/minute

### **WebSocket Limits**

- **Messages per connection**: 30 messages/minute
- **Connection attempts**: 5 attempts/minute
- **Concurrent connections per IP**: 10 connections

### **Rate Limit Headers**

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248600
```

## WebSocket Integration Examples

### **JavaScript/TypeScript**

```javascript
// Enhanced WebSocket connection with error handling
class ChatWebSocket {
  constructor(clientId) {
    this.clientId = clientId;
    this.url = `ws://localhost:8000/api/v1/chat/ws/${clientId}`;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;
    this.heartbeatInterval = 30000;
  }

  connect() {
    this.ws = new WebSocket(this.url);

    this.ws.onopen = () => {
      console.log("WebSocket connected");
      this.reconnectAttempts = 0;
      this.startHeartbeat();
    };

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === "ping") {
        this.ws.send(
          JSON.stringify({ type: "pong", timestamp: new Date().toISOString() })
        );
        return;
      }

      this.handleMessage(data);
    };

    this.ws.onclose = (event) => {
      console.log("WebSocket closed:", event.code, event.reason);
      this.stopHeartbeat();
      this.handleReconnection();
    };

    this.ws.onerror = (error) => {
      console.error("WebSocket error:", error);
    };
  }

  sendMessage(content) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(
        JSON.stringify({
          content: content,
          metadata: {
            timestamp: new Date().toISOString(),
            user_agent: navigator.userAgent,
          },
        })
      );
    }
  }

  startHeartbeat() {
    this.heartbeatTimer = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        // Server will send ping, we respond with pong
      }
    }, this.heartbeatInterval);
  }

  handleReconnection() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      setTimeout(() => {
        this.reconnectAttempts++;
        console.log(`Reconnection attempt ${this.reconnectAttempts}`);
        this.connect();
      }, this.reconnectDelay * Math.pow(2, this.reconnectAttempts));
    }
  }
}

// Usage
const chat = new ChatWebSocket("client-123");
chat.connect();
```

### **Python Client**

```python
import asyncio
import websockets
import json
from datetime import datetime

class ChatWebSocketClient:
    def __init__(self, client_id: str):
        self.client_id = client_id
        self.uri = f"ws://localhost:8000/api/v1/chat/ws/{client_id}"
        self.websocket = None

    async def connect(self):
        """Connect to WebSocket with error handling"""
        try:
            self.websocket = await websockets.connect(self.uri)
            await self.listen()
        except Exception as e:
            print(f"Connection error: {e}")

    async def listen(self):
        """Listen for messages with heartbeat handling"""
        async for message in self.websocket:
            data = json.loads(message)

            if data.get("type") == "ping":
                await self.send_pong()
                continue

            await self.handle_message(data)

    async def send_message(self, content: str):
        """Send message to server"""
        message = {
            "content": content,
            "metadata": {
                "timestamp": datetime.utcnow().isoformat(),
                "client_type": "python"
            }
        }
        await self.websocket.send(json.dumps(message))

    async def send_pong(self):
        """Respond to ping with pong"""
        pong = {
            "type": "pong",
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.websocket.send(json.dumps(pong))

    async def handle_message(self, data: dict):
        """Handle incoming messages"""
        print(f"Received: {data['content']}")
        print(f"Agent: {data.get('agent', 'Unknown')}")
        print(f"Confidence: {data.get('intent_data', {}).get('confidence', 0)}")

# Usage
async def main():
    client = ChatWebSocketClient("python-client-123")
    await client.connect()

asyncio.run(main())
```

## Monitoring & Metrics

### **Prometheus Metrics Endpoints**

```http
GET /metrics
```

**Key WebSocket Metrics:**

- `websocket_connections_total` - Active WebSocket connections
- `websocket_messages_total` - Total messages sent/received
- `websocket_connection_duration_seconds` - Connection duration histogram
- `websocket_errors_total` - WebSocket error counter
- `websocket_reconnections_total` - Reconnection attempts

**Enhanced Chat Metrics:**

- `intent_classification_confidence` - Intent confidence scores
- `knowledge_base_hits_total` - KB search success rate
- `chat_response_time_seconds` - Response time by agent type

---

This enhanced API reference provides comprehensive documentation for the enterprise-grade WebSocket communication system with robust error handling, connection management, and monitoring capabilities.
