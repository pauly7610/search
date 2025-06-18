# Xfinity Agentic AI Backend

This backend powers an agentic AI customer support demo for an Xfinity-style telecom/ISP company. It features enhanced multi-agent routing, intelligent knowledge base matching with natural language processing, comprehensive analytics, MLOps integration, and enterprise-grade monitoring with Prometheus and Grafana.

## 🚀 Features

### **🤖 Intelligent AI System**

- **Multi-Agent Architecture**: Specialized agents (Tech Support, Billing, General) with intent-based routing
- **Enhanced Knowledge Base**: Natural language matching with normalized keyword processing
- **Smart Fallback**: OpenAI GPT integration for complex queries beyond knowledge base
- **Intent Classification**: Automatic routing based on user query analysis

### **📊 Analytics & Monitoring**

- **Real-time Metrics**: Chat volume, response times, satisfaction scores, intent distribution
- **Prometheus Integration**: Production-ready metrics at `/metrics` endpoint
- **Database Monitoring**: PostgreSQL health, connection pools, query performance
- **WebSocket Tracking**: Real-time connection monitoring and performance

### **🔬 MLOps & Data Science**

- **Experiment Tracking**: MLflow integration for model versioning
- **Semantic Search**: Vector embeddings with sentence transformers
- **Data Pipeline**: ETL processes for feedback and intent training
- **Model Deployment**: Containerized ML models with FastAPI

### **🛠️ Production Ready**

- **WebSocket & REST APIs**: Real-time and traditional endpoints
- **Async Operations**: High-performance async/await patterns
- **Security**: JWT authentication, input validation, rate limiting
- **Error Handling**: Comprehensive error responses and logging

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

### **Chat & Conversations**

- `POST /api/v1/chat/messages` — Send message, get AI response with agent routing
- `GET /api/v1/chat/conversations` — List user conversations with pagination
- `GET /api/v1/chat/conversations/{id}` — Get specific conversation details
- `WS /api/v1/chat/ws` — Real-time WebSocket chat interface

### **Knowledge Base**

- `GET /api/v1/knowledge/search` — Search knowledge base with query
- `GET /api/v1/knowledge/categories` — List all categories by agent
- `POST /api/v1/knowledge/feedback` — Submit knowledge base feedback

### **Analytics & Insights**

- `GET /api/v1/analytics/overview` — Comprehensive analytics summary
- `GET /api/v1/analytics/metrics` — Detailed metrics with time ranges
- `GET /api/v1/analytics/intents` — Intent distribution and trends
- `GET /api/v1/analytics/satisfaction` — User satisfaction scores

### **Feedback & Quality**

- `POST /api/v1/feedback` — Submit conversation feedback
- `GET /api/v1/feedback/summary` — Feedback analytics and trends
- `POST /api/v1/feedback/rating` — Rate specific responses

### **System & Health**

- `GET /api/v1/health` — System health check with dependencies
- `GET /api/v1/profile` — User profile management
- `GET /metrics` — Prometheus metrics endpoint

## 📊 Monitoring & Observability

### **Prometheus Metrics**

The backend exposes comprehensive metrics at `/metrics`:

```python
# Custom metrics examples
http_requests_total = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
chat_response_time = Histogram('chat_response_time_seconds', 'Chat response time')
knowledge_base_hits = Counter('knowledge_base_hits_total', 'KB search hits')
llm_fallback_requests = Counter('llm_fallback_requests_total', 'LLM fallback requests')
```

### **Structured Logging**

```python
import structlog

logger = structlog.get_logger()
logger.info("Chat message processed",
    user_id=user_id,
    intent=detected_intent,
    agent=selected_agent,
    response_time=elapsed_time
)
```

### **Health Checks**

```bash
# Basic health
curl http://localhost:8000/api/v1/health

# Detailed health with dependencies
curl http://localhost:8000/api/v1/health?detailed=true
```

## 🧠 Enhanced Knowledge Base

### **Natural Language Matching**

The system now includes sophisticated matching algorithms:

```python
def normalize(text: str) -> str:
    """Normalize text for better matching"""
    return re.sub(r'[^\w\s]', ' ', text.lower()).strip()

def search_agent_kb(query: str, agent_data: dict) -> Optional[dict]:
    """Enhanced search with category name and keyword matching"""
    normalized_query = normalize(query)
    query_words = set(normalized_query.split())

    # Multi-level matching strategy
    for category_name, category_data in agent_data.get("categories", {}).items():
        # 1. Category name matching
        if normalized_query in normalize(category_name):
            return category_data

        # 2. Keyword overlap matching
        category_keywords = set(normalize(" ".join(category_data.get("keywords", []))).split())
        if len(query_words.intersection(category_keywords)) >= 2:
            return category_data

    return None
```

### **Knowledge Base Structure**

```json
{
  "agents": {
    "tech_support": {
      "categories": {
        "connectivity_issues": {
          "keywords": [
            "internet",
            "wifi",
            "connection",
            "outage",
            "down",
            "slow"
          ],
          "response": "I can help you troubleshoot connectivity issues...",
          "confidence": 0.95
        }
      }
    }
  }
}
```

## 🏗️ Directory Structure

```
backend/
├── src/
│   ├── api/                    # FastAPI route handlers
│   │   ├── chat.py            # Chat and conversation endpoints
│   │   ├── analytics.py       # Analytics and metrics endpoints
│   │   ├── feedback.py        # Feedback collection endpoints
│   │   └── knowledge.py       # Knowledge base endpoints
│   ├── services/              # Core business logic
│   │   ├── chat_service.py    # Enhanced chat processing
│   │   ├── intent_service.py  # Intent classification
│   │   ├── analytics_service.py # Analytics computation
│   │   └── semantic_search.py # Vector search capabilities
│   ├── models/                # Pydantic models and schemas
│   │   ├── chat_models.py     # Chat-related data models
│   │   ├── analytics_models.py # Analytics schemas
│   │   └── feedback_models.py # Feedback data structures
│   ├── config/                # Configuration management
│   │   ├── database.py        # Database connection and ORM
│   │   └── __init__.py        # Config initialization
│   ├── migrations/            # Alembic database migrations
│   ├── xfinity_knowledge_base.json # Enhanced knowledge base
│   └── main.py               # FastAPI application entry point
├── tests/                     # Comprehensive test suite
│   ├── test_api_chat.py      # Chat API tests
│   ├── test_api_analytics.py # Analytics API tests
│   └── test_api_feedback.py  # Feedback API tests
├── requirements.txt          # Python dependencies
├── setup.py                  # Package configuration
└── Dockerfile               # Container configuration
```

## 🔧 How It Works

### **Message Processing Flow**

1. **Message Received** → WebSocket or REST endpoint
2. **Intent Classification** → Determine user intent (tech, billing, general)
3. **Agent Selection** → Route to appropriate specialized agent
4. **Knowledge Base Search** → Enhanced matching with normalization
5. **LLM Fallback** → OpenAI GPT for complex queries
6. **Response Generation** → Include agent info, source, confidence
7. **Analytics Tracking** → Log metrics for monitoring
8. **Response Delivery** → Real-time or synchronous response

### **Knowledge Base Matching Strategy**

```python
# 1. Exact category name matching
# 2. Normalized keyword overlap (≥2 words)
# 3. Substring matching with confidence scoring
# 4. Semantic similarity (when enabled)
# 5. LLM fallback for unmatched queries
```

### **Multi-Agent Architecture**

- **Tech Support Agent**: Hardware, connectivity, troubleshooting
- **Billing Agent**: Payments, plans, account management
- **General Agent**: Company info, policies, general inquiries
- **Coordinator**: Intent classification and routing logic

## 🧪 Testing

### **Run Tests**

```bash
# All tests
pytest tests/ -v

# Specific test categories
pytest tests/test_api_chat.py -v
pytest tests/test_api_analytics.py -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

### **Test Categories**

- **Unit Tests**: Individual service and utility functions
- **Integration Tests**: API endpoints with database
- **Performance Tests**: Load testing for chat endpoints
- **ML Tests**: Knowledge base matching accuracy

## 🚀 Extending

### **Add New Agents**

1. Update `xfinity_knowledge_base.json`:

```json
{
  "agents": {
    "new_agent": {
      "categories": {
        "new_category": {
          "keywords": ["keyword1", "keyword2"],
          "response": "Agent response template",
          "confidence": 0.9
        }
      }
    }
  }
}
```

2. Update intent classification in `intent_service.py`
3. Add routing logic in `chat_service.py`

### **Add New Analytics**

Extend `analytics_service.py` with new metrics:

```python
@track_metric("custom_metric")
async def compute_custom_metric():
    # Your metric computation
    return metric_value
```

### **Add New Endpoints**

Create new API routes in `api/` directory:

```python
from fastapi import APIRouter
from services.custom_service import CustomService

router = APIRouter()

@router.post("/custom")
async def custom_endpoint():
    return await CustomService.process()
```

## 📈 Performance Optimization

### **Database Optimization**

- Connection pooling with SQLAlchemy
- Query optimization with proper indexing
- Async database operations

### **Caching Strategy**

- Redis for session storage
- In-memory caching for knowledge base
- Response caching for analytics

### **Monitoring & Alerts**

- Response time monitoring
- Error rate tracking
- Resource utilization alerts
- Custom business metrics

## 🔐 Security

### **Authentication & Authorization**

- JWT token-based authentication
- Role-based access control
- API rate limiting

### **Data Protection**

- Input validation and sanitization
- SQL injection prevention
- CORS configuration
- Sensitive data encryption

## 📚 Example Usage

### **Send Chat Message**

```bash
curl -X POST http://localhost:8000/api/v1/chat/messages \
  -H 'Content-Type: application/json' \
  -d '{
    "id": "msg-123",
    "content": "My internet is not working",
    "role": "user",
    "timestamp": "2024-01-15T10:30:00Z"
  }'
```

### **Get Analytics**

```bash
curl http://localhost:8000/api/v1/analytics/overview
```

### **WebSocket Connection**

```javascript
const ws = new WebSocket("ws://localhost:8000/api/v1/chat/ws");
ws.onmessage = (event) => {
  const response = JSON.parse(event.data);
  console.log("Agent:", response.agent);
  console.log("Response:", response.content);
};
```

---

For more details, see the documentation in the `docs/` directory and explore the code in `src/`.
