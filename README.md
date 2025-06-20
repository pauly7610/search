# Xfinity Agentic AI Demo Platform

A full-stack, production-ready demo of an agentic AI customer support system for a telecom/ISP (Xfinity-style) company. Features multi-agent routing, enhanced knowledge base with natural language matching, **enterprise-grade WebSocket communication**, modern dark theme UI, comprehensive analytics, MLOps capabilities, and enterprise-grade monitoring.

---

## ✨ Key Features

### 🤖 **Intelligent AI System**

- **Multi-Agent Architecture**: Specialized agents for Tech Support, Billing, and General inquiries
- **Enhanced Natural Language Understanding**: Advanced intent classification with confidence scoring
- **Smart Knowledge Base Matching**: Semantic search with normalized keyword processing
- **Robust Intent Classification**: Automatic routing to appropriate agents with fallback strategies
- **LLM Fallback**: OpenAI GPT integration for complex queries with graceful error handling

### 🔌 **Enterprise-Grade WebSocket Communication**

- **Robust Connection Management**: Client tracking with automatic reconnection and exponential backoff
- **Heartbeat Mechanism**: Ping/pong keep-alive to maintain stable connections
- **Comprehensive Error Handling**: Graceful fallbacks that never break the chat flow
- **Real-time Message Processing**: Instant bi-directional communication with typing indicators
- **Connection State Monitoring**: Detailed logging and connection health tracking

### 🎨 **Modern User Interface**

- **Dark/Light Theme Toggle**: Beautiful, modern UI with CSS variables system
- **Advanced Analytics Dashboard**: Interactive Recharts visualizations with gradients and custom tooltips
- **Real-time Chat**: WebSocket-powered instant messaging with enhanced reliability
- **Responsive Design**: Mobile-first approach with adaptive layouts
- **Connection Status Indicators**: Visual feedback for connection health and agent availability

### 📊 **Analytics & Monitoring**

- **Comprehensive Metrics**: Chat volume, response times, satisfaction scores, intent distribution
- **WebSocket Connection Monitoring**: Real-time tracking of active connections and message flow
- **Prometheus Integration**: Production-ready metrics collection with WebSocket-specific metrics
- **Grafana Dashboards**: Visual monitoring for backend API, database, and WebSocket performance
- **Alert Management**: Proactive notifications for system health and connection issues

### 🔬 **MLOps & Data Science**

- **Feedback Intent Training**: Jupyter notebook for ML model development with enhanced NLU
- **Intent Classification Analytics**: Advanced confidence scoring and pattern recognition
- **Experiment Tracking**: MLflow integration for model versioning
- **Data Visualization**: Advanced plotting and analysis tools for conversation analytics
- **Workflow Orchestration**: Apache Airflow support for data pipelines

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- OpenAI API key
- Git

### 1. Clone the repository

```bash
git clone <https://github.com/pauly7610/search>
cd search
```

### 2. Set up your environment

Create a `.env` file in `backend/` with your OpenAI key:

```env
OPENAI_API_KEY=your-api-key-here
DATABASE_URL=postgresql://user:password@localhost:5432/xfinity_ai
REDIS_URL=redis://localhost:6379
```

### 3. Start all services

```bash
# Full stack with monitoring
docker-compose -f infrastructure/docker-compose.yml up --build

# Include monitoring stack (Prometheus + Grafana)
docker-compose -f monitoring/docker-compose.monitoring.yml up -d
```

### 4. Access the system

- **🖥️ Frontend UI**: http://localhost:3000 (Modern chat interface with enhanced WebSocket reliability)
- **🔧 Backend API**: http://localhost:8000 (FastAPI with Swagger docs and WebSocket endpoints)
- **📈 Prometheus**: http://localhost:9090 (Metrics collection including WebSocket metrics)
- **📊 Grafana**: http://localhost:3001 (Dashboards with WebSocket monitoring - admin/admin)

---

## 🏗️ Project Structure

```
search/
├── backend/                 # FastAPI, LangChain, multi-agent AI with WebSocket management
│   ├── src/
│   │   ├── api/            # REST and enhanced WebSocket endpoints with connection management
│   │   ├── services/       # Business logic, AI services, and local intent classification
│   │   ├── models/         # Data models and schemas
│   │   └── config/         # Configuration management
│   ├── tests/              # Comprehensive test suite including WebSocket tests
│   └── requirements.txt    # Python dependencies
├── frontend/               # React, TypeScript, Tailwind CSS with robust WebSocket hooks
│   ├── src/
│   │   ├── components/     # UI components with connection status indicators
│   │   ├── hooks/          # Enhanced WebSocket and chat hooks with error handling
│   │   ├── services/       # API and WebSocket clients with reconnection logic
│   │   ├── store/          # State management (Zustand)
│   │   └── styles/         # CSS modules and themes
│   └── package.json        # Node.js dependencies
├── database/               # SQL migrations and seeds
├── infrastructure/         # Docker Compose, Kubernetes, Terraform
├── monitoring/             # Prometheus, Grafana, alerting with WebSocket metrics
├── docs/                   # Architecture and API documentation
├── mlops_feedback_intent_training.ipynb  # ML model development with enhanced NLU
└── requirements-mlops.txt  # Data science dependencies
```

---

## 🎯 Core Features

### **Enhanced Natural Language Understanding**

- **Advanced Intent Classification**: Multi-pattern matching with confidence scoring
- **Semantic Knowledge Base Search**: Understands variations like "bill is expensive" → "billing concerns"
- **Local Intent Service**: Fast, reliable intent classification with fallback to cloud services
- **Bidirectional Pattern Matching**: Flexible keyword and phrase recognition
- **Normalized Query Processing**: Handles punctuation, spaces, case variations

### **Enterprise-Grade WebSocket Architecture**

- **Connection Manager**: Robust client tracking with unique client IDs
- **Automatic Reconnection**: Exponential backoff strategy for connection resilience
- **Heartbeat Keep-Alive**: Ping/pong mechanism prevents connection timeouts
- **Error Recovery**: Graceful handling of network issues without breaking chat flow
- **Message Queue Management**: Reliable message delivery with proper error handling

### **Modern UI Components**

- **Dark Theme by Default**: Professional, eye-friendly interface
- **Connection Status Indicators**: Real-time feedback on WebSocket connection health
- **Interactive Analytics**: Real-time charts with hover effects and gradients
- **Enhanced Message Bubbles**: Rich metadata display with agent information
- **Responsive Navigation**: Adaptive sidebar and tab-based navigation

### **Production Monitoring**

- **WebSocket Metrics**: Connection count, message throughput, error rates
- **Backend Performance**: API response times, error rates, request volumes
- **Database Monitoring**: Connection pools, query performance, health checks
- **Real-time Dashboards**: Live WebSocket connection monitoring
- **Custom Alerts**: Configurable thresholds for proactive monitoring

---

## 📖 Documentation

### Core Documentation

- [🏗️ Architecture Overview](./docs/architecture.md) - Updated with WebSocket architecture
- [🔧 Backend Guide](./backend/README.md) - Enhanced with WebSocket connection management
- [🎨 Frontend Guide](./frontend/README.md) - Updated with robust WebSocket hooks
- [📊 API Reference](./docs/api_reference.md) - Including WebSocket endpoints

### Advanced Topics

- [🤖 Agent Routing & Intent Classification](./docs/agent_routing.md) - Enhanced NLU documentation
- [📚 Knowledge Base Format](./docs/knowledge_base.md) - Updated with semantic search capabilities
- [🎨 Frontend Customization](./docs/frontend_customization.md) - WebSocket integration patterns
- [🔧 Extending the System](./docs/extending.md) - WebSocket and NLU extension guides

### Operations

- [🚀 Infrastructure & Deployment](./infrastructure/README.md) - WebSocket scaling considerations
- [📈 Monitoring & Observability](./monitoring/README.md) - WebSocket metrics and alerting

---

## 🔌 WebSocket Features

### **Connection Management**

- Unique client identification and tracking
- Automatic connection health monitoring
- Graceful disconnection handling
- Connection metadata and analytics

### **Reliability Features**

- Exponential backoff reconnection strategy
- Heartbeat mechanism with configurable intervals
- Comprehensive error handling and recovery
- Message delivery confirmation

### **Monitoring & Debugging**

- Detailed connection logging
- Real-time connection statistics endpoint
- Connection state tracking and reporting
- Performance metrics collection

---

## 🔬 MLOps & Data Science

The platform includes comprehensive MLOps capabilities with enhanced NLU:

### Jupyter Notebook Development

```bash
# Install ML dependencies
pip install -r requirements-mlops.txt

# Start Jupyter
jupyter notebook mlops_feedback_intent_training.ipynb
```

### Available ML Tools

- **Enhanced Intent Classification**: Advanced pattern matching and confidence scoring
- **Conversation Analytics**: WebSocket message flow analysis
- **Experiment Tracking**: MLflow for model versioning
- **Data Analysis**: Pandas, NumPy, Scikit-learn with conversation data
- **Visualization**: Matplotlib, Seaborn, Plotly for WebSocket metrics
- **NLP Processing**: NLTK, Sentence Transformers for semantic understanding
- **Workflow Orchestration**: Apache Airflow for data pipelines

---

## 🔧 Configuration

### Environment Variables

```env
# Backend Configuration
OPENAI_API_KEY=your-openai-key
DATABASE_URL=postgresql://user:password@localhost:5432/xfinity_ai
REDIS_URL=redis://localhost:6379

# WebSocket Configuration
WEBSOCKET_HEARTBEAT_INTERVAL=30000
WEBSOCKET_RECONNECT_ATTEMPTS=5
WEBSOCKET_RECONNECT_DELAY=1000

# Monitoring
PROMETHEUS_PORT=9090
GRAFANA_PORT=3001

# MLOps
MLFLOW_TRACKING_URI=http://localhost:5000
```

### WebSocket Configuration Options

```typescript
// Frontend WebSocket configuration
const websocketOptions = {
  autoConnect: true,
  reconnection: true,
  reconnectionAttempts: 5,
  reconnectionDelay: 1000,
  heartbeatInterval: 30000,
};
```

---

## 🚀 Recent Enhancements

### **WebSocket Reliability Improvements**

- ✅ Fixed critical event handler conflicts
- ✅ Implemented robust connection management
- ✅ Added comprehensive error handling
- ✅ Introduced heartbeat keep-alive mechanism
- ✅ Enhanced reconnection strategies

### **Natural Language Understanding**

- ✅ Advanced intent classification with confidence scoring
- ✅ Local intent service with cloud fallback
- ✅ Enhanced semantic search capabilities
- ✅ Improved pattern matching algorithms

### **Production Readiness**

- ✅ Enterprise-grade WebSocket architecture
- ✅ Comprehensive logging and monitoring
- ✅ Graceful error recovery mechanisms
- ✅ Connection health tracking and analytics

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with FastAPI, React, and modern web technologies
- Enhanced WebSocket implementation following industry best practices
- Advanced NLU powered by local intent classification and OpenAI integration
- Production-ready monitoring with Prometheus and Grafana
