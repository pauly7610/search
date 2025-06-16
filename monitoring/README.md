# Monitoring & Observability

This directory contains all monitoring and observability configuration for the Xfinity Agentic AI Demo Platform.

## Components

- **Prometheus:** Scrapes metrics from backend, Postgres, and node exporters
- **Grafana:** Dashboards for backend API and Postgres health
- **Exporters:**
  - `postgres-exporter` for Postgres metrics
  - `node-exporter` for host/node metrics
- **Alerting:** Prometheus alert rules for backend latency, error rate, and DB health

## How to Use

- Prometheus config: `prometheus/prometheus.yml`
- Alert rules: `prometheus/rules/alerts.yml`
- Grafana dashboards: `grafana/dashboards/`

## Access

- **Prometheus UI:** http://localhost:9090
- **Grafana UI:** http://localhost:3001 (default: admin/admin)

## Extending

- Add new dashboards in `grafana/dashboards/`
- Add new alert rules in `prometheus/rules/`
- Add more exporters as needed

---

See the root README and docs for more.
