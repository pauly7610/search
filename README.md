# Xfinity Agentic AI Demo Platform

A full-stack, production-ready demo of an agentic AI customer support system for a telecom/ISP (Xfinity-style) company. Features multi-agent routing, a rich knowledge base, analytics, and best-practice monitoring.

---

## Quick Start

### Prerequisites

- Docker & Docker Compose
- OpenAI API key

### 1. Clone the repository

```bash
git clone <repository-url>
cd <repo>
```

### 2. Set up your environment

- Create a `.env` file in `backend/` with your OpenAI key:
  ```
  OPENAI_API_KEY=your-api-key-here
  ```

### 3. Start all services

```bash
docker-compose -f infrastructure/docker-compose.yml up --build
```

### 4. Access the system

- **Backend API:** http://localhost:8000
- **Frontend UI:** http://localhost:3000
- **Prometheus:** http://localhost:9090
- **Grafana:** http://localhost:3001 (default: admin/admin)

---

## Project Structure

- `backend/` — FastAPI, LangChain, multi-agent AI, knowledge base, analytics
- `frontend/` — React, Vite, Tailwind, chat UI, analytics dashboard
- `database/` — SQL migrations, seeds, setup scripts
- `infrastructure/` — Docker Compose, Kubernetes, Terraform
- `monitoring/` — Prometheus, Grafana, alert rules, dashboards
- `docs/` — Architecture, API, extension, and customization guides

---

## Features

- **Agentic AI:** Multi-agent system (Tech Support, Billing, General) with intent-based routing
- **Knowledge Base:** Structured, extensible JSON for Xfinity-style support
- **LLM Integration:** OpenAI GPT fallback for context-aware answers
- **Analytics:** Tracks chat volume, response times, satisfaction, and intent distribution
- **Monitoring:** Prometheus metrics, Grafana dashboards, alerting
- **Modern UI:** Real-time chat, agent/intent/source display, analytics dashboard

---

## Documentation

- [Backend README](./backend/README.md)
- [Frontend README](./frontend/README.md)
- [Full Documentation](./docs/README.md)

---

## Monitoring & Observability

- **Prometheus** scrapes backend, Postgres, and node metrics
- **Grafana** dashboards for backend API and Postgres health
- **Alerting** for latency, error rate, and DB health

---

## Extending

- Add new agents or FAQs in `backend/src/xfinity_knowledge_base.json`
- Add new analytics or metrics in backend
- Customize UI in `frontend/src/components/`
- See [docs/extending.md](./docs/extending.md) for more

---

## License

MIT
