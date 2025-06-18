# Xfinity Agentic AI Demo Platform

A full-stack, production-ready demo of an agentic AI customer support system for a telecom/ISP (Xfinity-style) company. Features multi-agent routing, enhanced knowledge base with natural language matching, modern dark theme UI, comprehensive analytics, MLOps capabilities, and enterprise-grade monitoring.

---

## ✨ Key Features

### 🤖 **Intelligent AI System**

- **Multi-Agent Architecture**: Specialized agents for Tech Support, Billing, and General inquiries
- **Enhanced Knowledge Base Matching**: Natural language processing with normalized keyword matching
- **Smart Intent Classification**: Automatic routing to appropriate agents
- **LLM Fallback**: OpenAI GPT integration for complex queries

### 🎨 **Modern User Interface**

- **Dark/Light Theme Toggle**: Beautiful, modern UI with CSS variables system
- **Advanced Analytics Dashboard**: Interactive Recharts visualizations with gradients and custom tooltips
- **Real-time Chat**: WebSocket-powered instant messaging with typing indicators
- **Responsive Design**: Mobile-first approach with adaptive layouts

### 📊 **Analytics & Monitoring**

- **Comprehensive Metrics**: Chat volume, response times, satisfaction scores, intent distribution
- **Prometheus Integration**: Production-ready metrics collection
- **Grafana Dashboards**: Visual monitoring for backend API, database, and WebSocket performance
- **Alert Management**: Proactive notifications for system health

### 🔬 **MLOps & Data Science**

- **Feedback Intent Training**: Jupyter notebook for ML model development
- **Experiment Tracking**: MLflow integration for model versioning
- **Data Visualization**: Advanced plotting and analysis tools
- **Workflow Orchestration**: Apache Airflow support for data pipelines

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- OpenAI API key
- Git

### 1. Clone the repository

```bash
git clone <repository-url>
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

- **🖥️ Frontend UI**: http://localhost:3000 (Modern chat interface with dark theme)
- **🔧 Backend API**: http://localhost:8000 (FastAPI with Swagger docs)
- **📈 Prometheus**: http://localhost:9090 (Metrics collection)
- **📊 Grafana**: http://localhost:3001 (Dashboards - admin/admin)

---

## 🏗️ Project Structure

```
search/
├── backend/                 # FastAPI, LangChain, multi-agent AI
│   ├── src/
│   │   ├── api/            # REST and WebSocket endpoints
│   │   ├── services/       # Business logic and AI services
│   │   ├── models/         # Data models and schemas
│   │   └── config/         # Configuration management
│   ├── tests/              # Comprehensive test suite
│   └── requirements.txt    # Python dependencies
├── frontend/               # React, TypeScript, Tailwind CSS
│   ├── src/
│   │   ├── components/     # UI components with dark theme
│   │   ├── hooks/          # Custom React hooks
│   │   ├── services/       # API and WebSocket clients
│   │   ├── store/          # State management (Zustand)
│   │   └── styles/         # CSS modules and themes
│   └── package.json        # Node.js dependencies
├── database/               # SQL migrations and seeds
├── infrastructure/         # Docker Compose, Kubernetes, Terraform
├── monitoring/             # Prometheus, Grafana, alerting
├── docs/                   # Architecture and API documentation
├── mlops_feedback_intent_training.ipynb  # ML model development
└── requirements-mlops.txt  # Data science dependencies
```

---

## 🎯 Core Features

### **Enhanced Knowledge Base**

- **Natural Language Matching**: Understands variations like "internet is out" → "connectivity issues"
- **Category Name Matching**: Searches both keywords and category names
- **Bidirectional Substring Matching**: Flexible pattern matching
- **Normalized Keyword Processing**: Handles punctuation, spaces, underscores

### **Modern UI Components**

- **Dark Theme by Default**: Professional, eye-friendly interface
- **Interactive Analytics**: Real-time charts with hover effects and gradients
- **Message Bubbles**: Distinct styling for user/assistant messages
- **Navigation**: Responsive sidebar and tab-based navigation

### **Production Monitoring**

- **Backend Metrics**: API response times, error rates, request volumes
- **Database Monitoring**: Connection pools, query performance, health checks
- **WebSocket Tracking**: Real-time connection monitoring
- **Custom Alerts**: Configurable thresholds for proactive monitoring

---

## 📖 Documentation

### Core Documentation

- [🏗️ Architecture Overview](./docs/architecture.md)
- [🔧 Backend Guide](./backend/README.md)
- [🎨 Frontend Guide](./frontend/README.md)
- [📊 API Reference](./docs/api_reference.md)

### Advanced Topics

- [🤖 Agent Routing & Intent Classification](./docs/agent_routing.md)
- [📚 Knowledge Base Format](./docs/knowledge_base.md)
- [🎨 Frontend Customization](./docs/frontend_customization.md)
- [🔧 Extending the System](./docs/extending.md)

### Operations

- [🚀 Infrastructure & Deployment](./infrastructure/README.md)
- [📈 Monitoring & Observability](./monitoring/README.md)

---

## 🔬 MLOps & Data Science

The platform includes comprehensive MLOps capabilities:

### Jupyter Notebook Development

```bash
# Install ML dependencies
pip install -r requirements-mlops.txt

# Start Jupyter
jupyter notebook mlops_feedback_intent_training.ipynb
```

### Available ML Tools

- **Experiment Tracking**: MLflow for model versioning
- **Data Analysis**: Pandas, NumPy, Scikit-learn
- **Visualization**: Matplotlib, Seaborn, Plotly
- **NLP Processing**: NLTK, Sentence Transformers
- **Workflow Orchestration**: Apache Airflow

---

## 🔧 Configuration

### Environment Variables

```env
# Backend Configuration
OPENAI_API_KEY=your-openai-key
DATABASE_URL=postgresql://user:password@localhost:5432/xfinity_ai
REDIS_URL=redis://localhost:6379

# Monitoring
PROMETHEUS_PORT=9090
GRAFANA_PORT=3001

# MLOps
MLFLOW_TRACKING_URI=http://localhost:5000
```

### Theme Customization

The frontend uses CSS variables for easy theme customization:

```css
:root {
  --color-primary: #3b82f6;
  --color-background: #0f172a;
  --color-surface: #1e293b;
  --color-text: #f8fafc;
}
```

---

## 🚀 Deployment Options

### Docker Compose (Recommended for Demo)

```bash
docker-compose -f infrastructure/docker-compose.yml up --build
```

### Kubernetes

```bash
kubectl apply -f infrastructure/kubernetes/
```

### Cloud (Terraform)

```bash
cd infrastructure/terraform/
terraform init && terraform plan && terraform apply
```

---

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v
```

### Frontend Tests

```bash
cd frontend
npm test
```

### End-to-End Testing

```bash
# Coming soon - Playwright integration
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🆘 Support

- 📖 **Documentation**: Check the [docs/](./docs/) directory
- 🐛 **Issues**: Report bugs via GitHub Issues
- 💬 **Discussions**: Join our GitHub Discussions
- 📧 **Contact**: [Your contact information]

---

**Built with ❤️ using FastAPI, React, LangChain, and modern web technologies.**
