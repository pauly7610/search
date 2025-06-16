# Product Requirements Document (PRD)

## **Product Overview**

An autonomous customer support agent that uses multi-agent workflows to provide intelligent, context-aware support by searching knowledge bases, escalating complex issues, and learning from human feedback.

## **Core Features**

**Multi-Agent Architecture**

- **Router Agent**: Classifies incoming queries by type (technical, billing, general)
- **Search Agent**: Performs PostgreSQL-powered searches with vector similarity
- **Response Agent**: Generates contextual responses using retrieved information
- **Escalation Agent**: Determines when to route to human agents
- **Feedback Agent**: Processes human corrections to improve future responses

**Key Capabilities**

- Real-time knowledge base search with semantic similarity using PostgreSQL vector extensions
- Persistent conversation memory across user sessions
- Human-in-the-loop feedback collection for continuous improvement
- Automatic escalation for complex queries
- Analytics dashboard for monitoring agent performance

**Technical Architecture**

- LangGraph for orchestrating multi-agent workflows
- PostgreSQL with pgvector extension for vector search and knowledge retrieval
- FastAPI backend with real-time WebSocket support
- React frontend with chat interface
- AWS deployment with MLOps pipeline monitoring

## **Monorepo Structure**

```
customer-support-agent/
├── backend/
│   ├── src/
│   │   ├── agents/
│   │   │   ├── __init__.py
│   │   │   ├── router_agent.py
│   │   │   ├── search_agent.py
│   │   │   ├── response_agent.py
│   │   │   ├── escalation_agent.py
│   │   │   └── feedback_agent.py
│   │   ├── graph/
│   │   │   ├── __init__.py
│   │   │   ├── workflow.py
│   │   │   └── state.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── postgres_service.py
│   │   │   ├── vector_service.py
│   │   │   ├── llm_service.py
│   │   │   └── memory_service.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── chat.py
│   │   │   ├── feedback.py
│   │   │   └── analytics.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── chat_models.py
│   │   │   ├── feedback_models.py
│   │   │   └── knowledge_models.py
│   │   ├── migrations/
│   │   │   ├── __init__.py
│   │   │   └── versions/
│   │   ├── config/
│   │   │   ├── __init__.py
│   │   └── settings.py
│   │   └── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Chat/
│   │   │   │   ├── ChatInterface.tsx
│   │   │   │   ├── MessageBubble.tsx
│   │   │   │   └── FeedbackButton.tsx
│   │   │   ├── Dashboard/
│   │   │   │   ├── Analytics.tsx
│   │   │   │   └── MetricsCard.tsx
│   │   │   └── Layout/
│   │   │       ├── Header.tsx
│   │   │       └── Sidebar.tsx
│   │   ├── hooks/
│   │   │   ├── useWebSocket.ts
│   │   │   └── useChat.ts
│   │   ├── services/
│   │   │   ├── api.ts
│   │   │   └── websocket.ts
│   │   ├── types/
│   │   │   └── chat.ts
│   │   ├── utils/
│   │   │   └── helpers.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── Dockerfile
├── infrastructure/
│   ├── terraform/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── kubernetes/
│   │   ├── backend-deployment.yaml
│   │   ├── frontend-deployment.yaml
│   │   └── postgres-deployment.yaml
│   └── docker-compose.yml
├── database/
│   ├── migrations/
│   │   ├── 001_create_knowledge_base.sql
│   │   ├── 002_create_conversations.sql
│   │   ├── 003_create_feedback.sql
│   │   └── 004_enable_vector_extension.sql
│   ├── seeds/
│   │   └── sample_knowledge_base.sql
│   └── scripts/
│       ├── setup_postgres.py
│       └── seed_knowledge_base.py
├── monitoring/
│   ├── grafana/
│   │   └── dashboards/
│   └── prometheus/
│       └── rules/
└── README.md
```

## **Dependencies**

### **Backend (requirements.txt)**

```txt
# Core Framework
fastapi==0.115.0
uvicorn[standard]==0.32.0
websockets==13.1

# LangChain & LangGraph
langchain==0.3.7
langchain-openai==0.2.8
langchain-community==0.3.7
langgraph==0.2.34
langsmith==0.1.140

# Database & Vector Store
psycopg2-binary==2.9.9
sqlalchemy==2.0.36
alembic==1.14.0
pgvector==0.3.6
asyncpg==0.29.0

# Vector & Embeddings
sentence-transformers==3.2.1
numpy==2.1.3

# Caching & Session Storage
redis==5.2.0

# ML & AI
openai==1.54.3
anthropic==0.39.0
pandas==2.2.3
scikit-learn==1.5.2

# Monitoring & Observability
prometheus-client==0.21.0
structlog==24.4.0
sentry-sdk[fastapi]==2.18.0

# AWS Services
boto3==1.35.67
botocore==1.35.67

# Development & Testing
pytest==8.3.3
pytest-asyncio==0.24.0
black==24.10.0
flake8==7.1.1
mypy==1.13.0
pre-commit==4.0.1

# Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.12

# Configuration
pydantic==2.10.2
pydantic-settings==2.6.1
python-dotenv==1.0.1
```

### **Frontend (package.json)**

```json
{
  "name": "customer-support-agent-frontend",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "format": "prettier --write \"src/**/*.{ts,tsx,css}\""
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.28.0",
    "@tanstack/react-query": "^5.59.16",
    "axios": "^1.7.7",
    "socket.io-client": "^4.8.1",
    "recharts": "^2.12.7",
    "lucide-react": "^0.454.0",
    "@headlessui/react": "^2.2.0",
    "clsx": "^2.1.1",
    "tailwind-merge": "^2.5.4",
    "react-hot-toast": "^2.4.1",
    "date-fns": "^4.1.0",
    "zustand": "^5.0.1"
  },
  "devDependencies": {
    "@types/react": "^18.3.12",
    "@types/react-dom": "^18.3.1",
    "@typescript-eslint/eslint-plugin": "^8.13.0",
    "@typescript-eslint/parser": "^8.13.0",
    "@vitejs/plugin-react": "^4.3.3",
    "autoprefixer": "^10.4.20",
    "eslint": "^9.13.0",
    "eslint-plugin-react-hooks": "^5.0.0",
    "eslint-plugin-react-refresh": "^0.4.14",
    "postcss": "^8.4.49",
    "prettier": "^3.3.3",
    "tailwindcss": "^3.4.14",
    "typescript": "^5.6.3",
    "vite": "^5.4.10"
  }
}
```

## **Database Schema**

### **PostgreSQL Tables with Vector Support**

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Knowledge Base table with vector embeddings
CREATE TABLE knowledge_base (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(100),
    embedding VECTOR(1536), -- OpenAI embedding dimension
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create vector similarity index
CREATE INDEX knowledge_base_embedding_idx ON knowledge_base
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Conversations table
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255),
    session_id VARCHAR(255),
    messages JSONB NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User feedback table
CREATE TABLE user_feedback (
    id SERIAL PRIMARY KEY,
    conversation_id UUID REFERENCES conversations(id),
    message_id VARCHAR(255),
    rating INTEGER CHECK (rating >= 1 AND rating  :query_embedding) as similarity
            FROM knowledge_base
            ORDER BY embedding  :query_embedding
            LIMIT :limit
        """)

        with self.engine.connect() as conn:
            result = conn.execute(
                query,
                {"query_embedding": query_embedding.tolist(), "limit": limit}
            )
            return result.fetchall()

    async def store_document(self, title: str, content: str, embedding: np.ndarray, category: str = None):
        """Store document with vector embedding"""
        query = text("""
            INSERT INTO knowledge_base (title, content, category, embedding)
            VALUES (:title, :content, :category, :embedding)
            RETURNING id
        """)

        with self.engine.connect() as conn:
            result = conn.execute(query, {
                "title": title,
                "content": content,
                "category": category,
                "embedding": embedding.tolist()
            })
            return result.fetchone()[0]
```

### **Memory and Conversation Management**

```python
from sqlalchemy.orm import sessionmaker
import json

class ConversationService:
    def __init__(self, db_session):
        self.db = db_session

    async def store_conversation(self, user_id: str, session_id: str, messages: List[Dict]):
        """Store conversation in PostgreSQL"""
        query = text("""
            INSERT INTO conversations (user_id, session_id, messages)
            VALUES (:user_id, :session_id, :messages)
            ON CONFLICT (session_id)
            DO UPDATE SET messages = :messages, updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """)

        result = await self.db.execute(query, {
            "user_id": user_id,
            "session_id": session_id,
            "messages": json.dumps(messages)
        })
        return result.fetchone()[0]

    async def get_conversation_history(self, session_id: str):
        """Retrieve conversation history"""
        query = text("""
            SELECT messages FROM conversations
            WHERE session_id = :session_id
        """)

        result = await self.db.execute(query, {"session_id": session_id})
        row = result.fetchone()
        return json.loads(row[0]) if row else []
```

### **Docker Compose Configuration**

```yaml
version: "3.8"

services:
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_DB: customer_support
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/migrations:/docker-entrypoint-initdb.d

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:password@postgres:5432/customer_support
      REDIS_URL: redis://redis:6379
    depends_on:
      - postgres
      - redis

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  postgres_data:
  redis_data:
```

## **Key Changes from ElasticSearch to PostgreSQL**

### **Architecture Benefits**

- **Unified Database**: Single PostgreSQL instance handles both structured data (conversations, feedback) and vector searches
- **ACID Compliance**: Full transactional support for data consistency
- **Cost Efficiency**: Eliminates need for separate ElasticSearch infrastructure
- **Simplified Operations**: Single database system to maintain and monitor

### **Vector Search Capabilities**

- **pgvector Extension**: Provides native vector operations with cosine similarity, L2 distance, and inner product
- **Indexing Support**: IVFFlat and HNSW indexes for efficient similarity search
- **Scalability**: Handles millions of vectors with optimized indexing strategies

### **Migration Considerations**

- **Performance**: PostgreSQL with pgvector provides comparable search performance for most use cases
- **Embedding Storage**: Native vector type eliminates need for JSON storage of embeddings
- **Query Flexibility**: SQL-based vector operations allow complex filtering and aggregations
