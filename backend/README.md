# Xfinity Agentic AI Backend

This backend powers an agentic AI customer support demo for an Xfinity-style telecom/ISP company. It features **enterprise-grade WebSocket connection management**, enhanced multi-agent routing, intelligent knowledge base matching with natural language processing, comprehensive analytics, MLOps integration, and enterprise-grade monitoring with Prometheus and Grafana.

## 🚀 Features

### **🔌 Enterprise-Grade WebSocket Architecture**

- **Robust Connection Manager**: Client tracking with unique IDs and metadata
- **Automatic Reconnection**: Exponential backoff strategy for connection resilience
- **Heartbeat Keep-Alive**: Ping/pong mechanism prevents connection timeouts
- **Comprehensive Error Handling**: Graceful fallbacks that never break chat flow
- **Real-time Monitoring**: Connection statistics and health tracking

### **🤖 Intelligent AI System with Enhanced Conversational Flow**

- **Multi-Agent Architecture**: Specialized agents (Tech Support, Billing, General) with intent-based routing
- **Enhanced Natural Language Understanding**: Advanced intent classification with confidence scoring
- **Human-Centered Conversational Flow**: Natural follow-up handling with "that didn't work" responses
- **Adaptive Tone System**: Context-aware empathetic responses based on frustration levels (5 different tones)
- **Intelligent Frustration Detection**: Monitors sentiment, caps lock, punctuation patterns for proactive escalation
- **Local Intent Service**: Fast, reliable intent classification with cloud fallback
- **Smart Knowledge Base**: Semantic search with normalized keyword processing and solution tracking
- **Smart Fallback**: OpenAI GPT integration for complex queries beyond knowledge base

### **📊 Analytics & Business Intelligence**

- **Real-time Metrics**: Chat volume, response times, satisfaction scores, intent distribution
- **Conversation Quality Tracking**: Intent resolution rates, frustration level monitoring, tone adaptation analytics
- **Follow-up Pattern Analysis**: Tracks "that didn't work" scenarios and solution effectiveness
- **Business Intelligence Dashboard**: Real-time conversation flow analysis and escalation predictions
- **WebSocket Metrics**: Connection count, message throughput, error rates
- **Prometheus Integration**: Production-ready metrics at `/metrics` endpoint with conversation-specific tracking
- **Database Monitoring**: PostgreSQL health, connection pools, query performance
- **Connection Health Tracking**: Real-time WebSocket connection monitoring and performance

### **🔬 MLOps & Data Science**

- **Enhanced Intent Classification**: Advanced pattern matching and confidence scoring
- **Experiment Tracking**: MLflow integration for model versioning
- **Semantic Search**: Vector embeddings with sentence transformers
- **Conversation Analytics**: WebSocket message flow analysis
- **Data Pipeline**: ETL processes for feedback and intent training
- **Model Deployment**: Containerized ML models with FastAPI

### **🛠️ Production Ready**

- **Enhanced WebSocket & REST APIs**: Real-time and traditional endpoints with robust error handling
- **Async Operations**: High-performance async/await patterns
- **Connection Management**: Enterprise-grade WebSocket client tracking and lifecycle management
- **Security**: JWT authentication, input validation, rate limiting
- **Comprehensive Error Handling**: Graceful error responses and detailed logging

## 🏗️ Setup

### 1. Install Python dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install core dependencies
pip install -r requirements.txt

# Install MLOps dependencies (optional)
pip install -r ../requirements-mlops.txt
```

### 2. Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Core Configuration
OPENAI_API_KEY=your-openai-key-here
DATABASE_URL=postgresql://user:password@localhost:5432/xfinity_ai
REDIS_URL=redis://localhost:6379

# WebSocket Configuration
WEBSOCKET_HEARTBEAT_INTERVAL=30000
WEBSOCKET_RECONNECT_ATTEMPTS=5
WEBSOCKET_RECONNECT_DELAY=1000
WEBSOCKET_MAX_CONNECTIONS=1000

# Security
JWT_SECRET_KEY=your-jwt-secret-key
BCRYPT_ROUNDS=12

# Monitoring
PROMETHEUS_PORT=9090
SENTRY_DSN=your-sentry-dsn

# MLOps
MLFLOW_TRACKING_URI=http://localhost:5000
EXPERIMENT_NAME=xfinity-ai-experiments

# Development
DEBUG=True
LOG_LEVEL=INFO
```

### 3. Database Setup

```bash
# Run migrations
cd src
alembic upgrade head

# Seed knowledge base (optional)
python -c "from config.database import seed_knowledge_base; seed_knowledge_base()"
```

### 4. Run the Backend

#### Development (with hot reload):

```bash
cd src
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Production:

```bash
cd src
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Docker:

```bash
docker build -t xfinity-agent-backend .
docker run -p 8000:8000 --env-file .env xfinity-agent-backend
```

## 📡 API Endpoints

### **Enhanced Chat & WebSocket**

- `POST /api/v1/chat/messages` — Send message, get AI response with agent routing
- `GET /api/v1/chat/conversations` — List user conversations with pagination
- `GET /api/v1/chat/conversations/{id}` — Get specific conversation details
- `WS /api/v1/chat/ws/{client_id}` — Enhanced WebSocket chat with client tracking
- `WS /api/v1/chat/ws` — Legacy WebSocket endpoint (auto-assigns client ID)
- `GET /api/v1/chat/ws/stats` — WebSocket connection statistics and health

### **Knowledge Base**

- `GET /api/v1/knowledge/search` — Enhanced semantic search with confidence scoring
- `GET /api/v1/knowledge/categories` — List all categories by agent
- `POST /api/v1/knowledge/feedback` — Submit knowledge base feedback

### **Analytics & Business Intelligence**

- `GET /api/v1/analytics/overview` — Comprehensive analytics summary with WebSocket metrics
- `GET /api/v1/analytics/metrics` — Detailed metrics with time ranges
- `GET /api/v1/analytics/intents` — Intent distribution and confidence trends
- `GET /api/v1/analytics/satisfaction` — User satisfaction scores
- `GET /api/v1/metrics/conversation-quality` — Conversation quality metrics and insights
- `GET /api/v1/metrics/conversation-flow/{conversation_id}` — Individual conversation flow analysis
- `GET /api/v1/metrics/intent-resolution-rate` — Business intelligence on intent resolution patterns
- `GET /api/v1/metrics/escalation-predictions` — Predictive analytics for conversation escalation

### **Feedback & Quality**

- `POST /api/v1/feedback` — Submit conversation feedback
- `GET /api/v1/feedback/summary` — Feedback analytics and trends
- `POST /api/v1/feedback/rating` — Rate specific responses

### **System & Health**

- `GET /api/v1/health` — System health check with WebSocket connection status
- `GET /api/v1/profile` — User profile management
- `GET /metrics` — Prometheus metrics endpoint with WebSocket metrics

## 🔌 WebSocket Architecture

### **Connection Manager**

```python
class ChatConnectionManager:
    """
    Robust WebSocket connection manager for multi-client chat support.

    Features:
    - Client identification and tracking
    - Connection state management
    - Error handling for failed connections
    - Graceful disconnection handling
    - Message queuing for offline clients
    """

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept connection and register client"""

    async def disconnect(self, client_id: str):
        """Remove client and cleanup metadata"""

    async def send_personal_message(self, message: Dict[str, Any], client_id: str):
        """Send message to specific client with error handling"""
```

### **Enhanced WebSocket Endpoint**

```python
@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """
    Enhanced WebSocket endpoint with:
    - Proper connection management
    - Comprehensive exception handling
    - Client identification
    - Detailed logging
    - Graceful error recovery
    """
```

### **Connection Features**

- **Client Tracking**: Unique client IDs with metadata
- **Health Monitoring**: Connection state and activity tracking
- **Error Recovery**: Graceful handling of network issues
- **Message Reliability**: Delivery confirmation and retry logic
- **Performance Monitoring**: Connection metrics and analytics

## 📊 Monitoring & Observability

### **Enhanced Prometheus Metrics**

The backend exposes comprehensive metrics at `/metrics`:

```python
# WebSocket-specific metrics
websocket_connections_total = Gauge('websocket_connections_total', 'Active WebSocket connections')
websocket_messages_total = Counter('websocket_messages_total', 'Total WebSocket messages', ['direction'])
websocket_connection_duration = Histogram('websocket_connection_duration_seconds', 'Connection duration')
websocket_errors_total = Counter('websocket_errors_total', 'WebSocket errors', ['error_type'])

# Enhanced chat metrics
chat_response_time = Histogram('chat_response_time_seconds', 'Chat response time', ['agent_type'])
intent_classification_confidence = Histogram('intent_classification_confidence', 'Intent confidence scores')
knowledge_base_hits = Counter('knowledge_base_hits_total', 'KB search hits', ['agent', 'confidence_level'])
llm_fallback_requests = Counter('llm_fallback_requests_total', 'LLM fallback requests', ['reason'])
```

### **Structured Logging**

```python
import structlog

logger = structlog.get_logger()

# WebSocket connection logging
logger.info("WebSocket connection established",
    client_id=client_id,
    connection_count=connection_manager.get_connection_count()
)

# Enhanced chat logging
logger.info("Chat message processed",
    user_id=user_id,
    client_id=client_id,
    intent=detected_intent,
    confidence=intent_confidence,
    agent=selected_agent,
    response_time=elapsed_time,
    knowledge_base_hit=kb_hit
)
```

### **Health Checks**

```bash
# Basic health with WebSocket status
curl http://localhost:8000/api/v1/health

# WebSocket connection statistics
curl http://localhost:8000/api/v1/chat/ws/stats
```

## 🧠 Enhanced Natural Language Understanding

### **Advanced Intent Classification**

```python
class LocalIntentService:
    """
    Local intent classification service with enhanced pattern matching.

    Features:
    - Multi-pattern matching with confidence scoring
    - Keyword normalization and preprocessing
    - Fallback to cloud services
    - Performance optimization
    """

    def classify_intent(self, query: str) -> Dict[str, Any]:
        """
        Classify intent with confidence scoring.

        Returns:
        - intent: Classified category
        - confidence: Confidence score (0-1)
        - matched_patterns: Patterns that matched
        - agent_type: Recommended agent
        """
```

### **Enhanced Knowledge Base Search**

```python
def enhanced_semantic_search(query: str, agent_type: str = None) -> List[Dict]:
    """
    Enhanced semantic search with:
    - Query preprocessing and normalization
    - Multi-level matching (exact, partial, semantic)
    - Confidence scoring
    - Agent-specific filtering
    - Result ranking and deduplication
    """

    # Query preprocessing
    normalized_query = preprocess_query(query)

    # Multi-level search strategy
    exact_matches = find_exact_matches(normalized_query)
    partial_matches = find_partial_matches(normalized_query)
    semantic_matches = find_semantic_matches(normalized_query)

    # Combine and rank results
    return rank_and_deduplicate_results(exact_matches, partial_matches, semantic_matches)
```

### **Pattern Matching Algorithms**

```python
# Enhanced pattern matching with confidence scoring
BILLING_PATTERNS = [
    {"pattern": r"\b(bill|billing|charge|cost|expensive|payment)\b", "weight": 0.9},
    {"pattern": r"\b(cancel|disconnect|service)\b", "weight": 0.7},
    {"pattern": r"\b(refund|credit|discount)\b", "weight": 0.8}
]

TECHNICAL_PATTERNS = [
    {"pattern": r"\b(internet|wifi|connection|slow|down|outage)\b", "weight": 0.9},
    {"pattern": r"\b(router|modem|equipment|device)\b", "weight": 0.8},
    {"pattern": r"\b(speed|performance|lag|buffering)\b", "weight": 0.7}
]
```

## 🎯 Enhanced Conversational Flow Services

### **Conversation State Management**

```python
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional

class ConversationState(Enum):
    INITIAL = "initial"
    FOLLOW_UP = "follow_up"
    FRUSTRATED = "frustrated"
    ESCALATION = "escalation"
    RESOLVED = "resolved"

@dataclass
class ConversationContext:
    conversation_id: str
    user_id: str
    state: ConversationState
    attempt_count: int
    previous_solutions: List[str]
    frustration_level: int  # 0-10 scale
    tone: str
    follow_up_detected: bool
```

### **Enhanced Chat Service with Follow-up Handling**

```python
class EnhancedChatService:
    """
    Enhanced chat service with human-centered conversational flow.

    Features:
    - Follow-up pattern detection ("that didn't work", "still not working")
    - Adaptive tone system (5 different empathy levels)
    - Frustration level monitoring (0-10 scale)
    - Context-aware response generation
    - Solution effectiveness tracking
    """

    def __init__(self):
        self.follow_up_patterns = [
            r"(?i)that didn'?t work",
            r"(?i)still not working",
            r"(?i)it'?s still broken",
            r"(?i)try something else",
            r"(?i)need another solution"
        ]

        self.frustration_indicators = [
            r"[A-Z]{3,}",  # Caps lock
            r"[!]{2,}",    # Multiple exclamation marks
            r"[?]{2,}",    # Multiple question marks
            r"(?i)frustrated|annoyed|angry"
        ]

    async def handle_message(self, message: str, context: ConversationContext) -> ChatResponse:
        """Enhanced message handling with follow-up detection"""

        # Detect follow-up patterns
        is_follow_up = self.detect_follow_up(message)

        # Calculate frustration level
        frustration_level = self.calculate_frustration_level(message, context)

        # Determine appropriate tone
        tone = self.determine_tone(context, is_follow_up, frustration_level)

        # Generate contextual response
        response = await self.generate_response(message, context, tone, is_follow_up)

        return response

    def detect_follow_up(self, message: str) -> bool:
        """Detect if message is a follow-up indicating previous solution failed"""
        return any(re.search(pattern, message) for pattern in self.follow_up_patterns)

    def calculate_frustration_level(self, message: str, context: ConversationContext) -> int:
        """Calculate frustration level on 0-10 scale"""
        frustration = 0

        # Check for caps lock usage
        caps_ratio = sum(1 for c in message if c.isupper()) / len(message) if message else 0
        if caps_ratio > 0.3:
            frustration += 3

        # Check for frustration indicators
        for pattern in self.frustration_indicators:
            if re.search(pattern, message):
                frustration += 2

        # Factor in attempt count
        frustration += min(context.attempt_count, 3)

        return min(frustration, 10)

    def determine_tone(self, context: ConversationContext, is_follow_up: bool, frustration_level: int) -> str:
        """Determine appropriate conversational tone based on context"""
        if frustration_level >= 8:
            return "empathetic_escalation"
        elif frustration_level >= 6:
            return "empathetic_supportive"
        elif is_follow_up or context.attempt_count >= 2:
            return "patient_alternative"
        elif context.attempt_count >= 1:
            return "understanding_adaptive"
        else:
            return "helpful_friendly"
```

### **Business Intelligence Metrics Service**

```python
class ConversationMetricsCollector:
    """
    Comprehensive conversation analytics for business intelligence.

    Tracks:
    - Intent resolution rates over time
    - Follow-up pattern analysis
    - Solution effectiveness metrics
    - Frustration level trends
    - Tone adaptation analytics
    - Escalation prediction indicators
    """

    def __init__(self):
        self.metrics_store = {}
        self.conversation_outcomes = {}

    def track_conversation_flow(self, conversation_id: str, metrics: Dict):
        """Track conversation flow metrics for business analysis"""

        self.metrics_store[conversation_id] = {
            "processing_time": metrics.get("processing_time"),
            "is_follow_up": metrics.get("is_follow_up", False),
            "frustration_level": metrics.get("frustration_level", 0),
            "attempt_count": metrics.get("attempt_count", 1),
            "tone_used": metrics.get("tone", "helpful_friendly"),
            "intent": metrics.get("intent"),
            "agent_type": metrics.get("agent_type"),
            "timestamp": datetime.utcnow()
        }

    def calculate_intent_resolution_rate(self, time_window_days: int = 7) -> Dict[str, float]:
        """Calculate resolution rates by intent over time window"""

        cutoff_date = datetime.utcnow() - timedelta(days=time_window_days)

        resolution_data = {}
        for conv_id, metrics in self.metrics_store.items():
            if metrics["timestamp"] >= cutoff_date:
                intent = metrics["intent"]
                if intent not in resolution_data:
                    resolution_data[intent] = {"total": 0, "resolved": 0}

                resolution_data[intent]["total"] += 1
                if not metrics["is_follow_up"]:  # First attempt resolution
                    resolution_data[intent]["resolved"] += 1

        return {
            intent: data["resolved"] / data["total"] if data["total"] > 0 else 0
            for intent, data in resolution_data.items()
        }

    def predict_escalation_likelihood(self, conversation_id: str) -> Dict[str, Any]:
        """Predict likelihood of conversation requiring human escalation"""

        if conversation_id not in self.metrics_store:
            return {"likelihood": 0, "confidence": 0, "factors": []}

        metrics = self.metrics_store[conversation_id]

        # Calculate escalation likelihood based on factors
        escalation_score = 0
        factors = []

        # High frustration indicator
        if metrics["frustration_level"] >= 7:
            escalation_score += 0.4
            factors.append("high_frustration")

        # Multiple attempts
        if metrics["attempt_count"] >= 3:
            escalation_score += 0.3
            factors.append("multiple_attempts")

        # Follow-up pattern
        if metrics["is_follow_up"]:
            escalation_score += 0.2
            factors.append("solution_failure")

        # Complex intent patterns
        if metrics["intent"] in ["technical_complex", "billing_dispute"]:
            escalation_score += 0.1
            factors.append("complex_intent")

        return {
            "likelihood": min(escalation_score, 1.0),
            "confidence": 0.85,  # Model confidence
            "factors": factors,
            "recommendation": "offer_human_agent" if escalation_score > 0.6 else "continue_ai"
        }
```

## 🚀 Recent Enhancements

### **Enhanced Conversational Flow (Latest)**

- ✅ Human-centered follow-up handling with "that didn't work" detection
- ✅ Adaptive tone system with 5 empathy levels (helpful → empathetic escalation)
- ✅ Intelligent frustration detection using text analysis and conversation context
- ✅ Business intelligence metrics for conversation quality and resolution rates
- ✅ Proactive escalation prediction to identify customers needing human help
- ✅ Context-aware response generation preserving conversation history

### **WebSocket Reliability Improvements**

- ✅ Implemented robust connection manager with client tracking
- ✅ Added comprehensive error handling and recovery mechanisms
- ✅ Introduced heartbeat keep-alive with ping/pong
- ✅ Enhanced reconnection strategies with exponential backoff
- ✅ Added detailed logging and connection monitoring

### **Natural Language Understanding**

- ✅ Advanced intent classification with confidence scoring
- ✅ Local intent service with cloud fallback capabilities
- ✅ Enhanced semantic search with multi-level matching
- ✅ Improved pattern matching algorithms
- ✅ Query preprocessing and normalization

### **Production Readiness**

- ✅ Enterprise-grade WebSocket architecture
- ✅ Comprehensive metrics and monitoring
- ✅ Graceful error handling and recovery
- ✅ Connection health tracking and analytics
- ✅ Performance optimization and scaling considerations

## 🧪 Testing

### **Backend Tests**

```bash
cd backend
pytest tests/ -v

# Run WebSocket-specific tests
pytest tests/test_websocket.py -v

# Run intent classification tests
pytest tests/test_intent_service.py -v
```

### **WebSocket Testing**

```python
# Example WebSocket test
async def test_websocket_connection():
    async with websockets.connect("ws://localhost:8000/api/v1/chat/ws/test-client") as websocket:
        # Test message sending
        await websocket.send(json.dumps({"content": "internet is down"}))

        # Test response receiving
        response = await websocket.recv()
        data = json.loads(response)

        assert data["role"] == "assistant"
        assert "internet" in data["content"].lower()
```

### **Intent Classification Testing**

```python
# Test enhanced intent classification
def test_intent_classification():
    intent_service = LocalIntentService()

    result = intent_service.classify_intent("my bill is so expensive")

    assert result["intent"] == "billing"
    assert result["confidence"] > 0.8
    assert result["agent_type"] == "billing"
```

## 🔧 Configuration

### **WebSocket Configuration**

```python
# WebSocket settings
WEBSOCKET_CONFIG = {
    "heartbeat_interval": 30,  # seconds
    "max_connections": 1000,
    "connection_timeout": 300,  # seconds
    "message_queue_size": 100,
    "reconnect_attempts": 5,
    "reconnect_delay": 1000  # milliseconds
}
```

### **Intent Classification Configuration**

```python
# Intent service settings
INTENT_CONFIG = {
    "confidence_threshold": 0.7,
    "use_local_service": True,
    "fallback_to_cloud": True,
    "cache_results": True,
    "cache_ttl": 3600  # seconds
}
```

## 📚 API Documentation

### **Interactive Documentation**

- **Swagger UI**: http://localhost:8000/docs (Interactive API exploration)
- **ReDoc**: http://localhost:8000/redoc (Clean API documentation)

### **WebSocket API**

```javascript
// Connect to WebSocket
const ws = new WebSocket("ws://localhost:8000/api/v1/chat/ws/your-client-id");

// Send message
ws.send(
  JSON.stringify({
    content: "My internet is not working",
  })
);

// Handle response
ws.onmessage = (event) => {
  const response = JSON.parse(event.data);
  console.log("AI Response:", response.content);
  console.log("Agent:", response.agent);
  console.log("Intent:", response.intent);
  console.log("Confidence:", response.intent_data?.confidence);
};
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/websocket-enhancement`)
3. Make your changes with tests
4. Run the test suite (`pytest tests/ -v`)
5. Commit your changes (`git commit -m 'Add WebSocket enhancement'`)
6. Push to the branch (`git push origin feature/websocket-enhancement`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

---

**Built with FastAPI, LangChain, WebSockets, and enterprise-grade reliability patterns.**
