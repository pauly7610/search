# Monitoring & Observability

This directory contains comprehensive monitoring and observability configuration for the **Xfinity Agentic AI Demo Platform**. Provides enterprise-grade monitoring with Prometheus metrics collection, Grafana dashboards, alerting, and performance analytics.

## 🎯 Monitoring Architecture

### **Core Components**

- **Prometheus**: Time-series metrics collection and alerting engine
- **Grafana**: Interactive dashboards and data visualization
- **AlertManager**: Intelligent alert routing and notification management
- **Node Exporter**: System-level metrics collection
- **Postgres Exporter**: Database performance monitoring
- **Custom Exporters**: Application-specific metrics

### **Advanced Features**

- **Real-time Dashboards**: Live system performance monitoring
- **Business Metrics**: Chat analytics, AI effectiveness, user satisfaction
- **Predictive Alerting**: Proactive issue detection and notification
- **Performance Analytics**: Response time analysis and optimization insights
- **Security Monitoring**: Authentication failures, rate limiting, suspicious activity

## 📊 Available Dashboards

### **System Performance Dashboards**

- **Backend API Dashboard**: Response times, throughput, error rates, AI processing metrics
- **Database Dashboard**: Connection pools, query performance, storage utilization, pgvector metrics
- **WebSocket Dashboard**: Real-time connection monitoring, message throughput, connection stability
- **Infrastructure Dashboard**: CPU, memory, disk, network utilization across all nodes

### **Business Intelligence Dashboards**

- **AI Agents Dashboard**: Agent performance, intent classification accuracy, knowledge base effectiveness
- **User Experience Dashboard**: Chat satisfaction, session duration, feature usage patterns
- **Customer Support Analytics**: Resolution rates, escalation patterns, common issues
- **Performance Optimization**: Query optimization insights, caching effectiveness, resource utilization

## 🚀 Quick Start

### **Local Development Setup**

```bash
# Start monitoring stack with main application
docker-compose -f infrastructure/docker-compose.yml up --build
docker-compose -f monitoring/docker-compose.monitoring.yml up -d

# Verify services are running
docker-compose ps
```

### **Access Monitoring Services**

- **Prometheus UI**: http://localhost:9090
  - Query metrics, configure alerts, view targets
- **Grafana UI**: http://localhost:3001
  - Default credentials: admin/admin
  - Pre-configured dashboards and data sources
- **AlertManager UI**: http://localhost:9093
  - Alert management and notification configuration

### **Production Deployment**

```bash
# Deploy monitoring stack to Kubernetes
kubectl apply -f infrastructure/kubernetes/monitoring/

# Verify deployment
kubectl get pods -n monitoring
kubectl get services -n monitoring

# Access via port forwarding (if ingress not configured)
kubectl port-forward service/grafana 3001:3000 -n monitoring
kubectl port-forward service/prometheus 9090:9090 -n monitoring
```

## 📁 Directory Structure

```
monitoring/
├── docker-compose.monitoring.yml   # Docker Compose monitoring stack
├── grafana/                        # Grafana configuration
│   ├── dashboards/                # Pre-built dashboard definitions
│   │   ├── ai-agents-dashboard.json      # AI agent performance
│   │   ├── backend-api-dashboard.json    # Backend API metrics
│   │   ├── database-dashboard.json       # PostgreSQL monitoring
│   │   ├── websocket-dashboard.json      # WebSocket connections
│   │   ├── backend.json                  # Legacy backend dashboard
│   │   └── postgres.json                 # Legacy database dashboard
│   ├── datasources/               # Data source configurations
│   │   └── prometheus.yml         # Prometheus data source
│   └── grafana.ini               # Grafana server configuration
├── prometheus/                    # Prometheus configuration
│   ├── prometheus.yml            # Main Prometheus configuration
│   └── rules/                    # Alert rules and recording rules
│       ├── alerts.yml            # General system alerts
│       ├── backend-alerts.yml    # Backend-specific alerts
│       ├── database-alerts.yml   # Database alerts
│       ├── frontend-alerts.yml   # Frontend alerts
│       └── README.md             # Alert rule documentation
└── README.md                     # This file
```

## 🔧 Configuration

### **Prometheus Configuration**

```yaml
# prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: "xfinity-ai-demo"
    environment: "production"

rule_files:
  - "rules/*.yml"

scrape_configs:
  - job_name: "xfinity-backend"
    static_configs:
      - targets: ["backend:8000"]
    metrics_path: "/metrics"
    scrape_interval: 30s
    scrape_timeout: 10s

  - job_name: "postgres-exporter"
    static_configs:
      - targets: ["postgres-exporter:9187"]

  - job_name: "node-exporter"
    static_configs:
      - targets: ["node-exporter:9100"]

  - job_name: "redis-exporter"
    static_configs:
      - targets: ["redis-exporter:9121"]
```

### **Grafana Data Sources**

```yaml
# grafana/datasources/prometheus.yml
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
    jsonData:
      timeInterval: "5s"
      queryTimeout: "60s"
      httpMethod: "POST"
```

### **Alert Rules Configuration**

```yaml
# prometheus/rules/backend-alerts.yml
groups:
  - name: backend-performance
    rules:
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job="xfinity-backend"}[5m])) > 0.5
        for: 2m
        labels:
          severity: warning
          component: backend
        annotations:
          summary: "High response time detected"
          description: "95th percentile response time is {{ $value }}s"

      - alert: HighErrorRate
        expr: rate(http_requests_total{job="xfinity-backend",status=~"5.."}[5m]) / rate(http_requests_total{job="xfinity-backend"}[5m]) > 0.05
        for: 1m
        labels:
          severity: critical
          component: backend
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }}"

      - alert: LLMFallbackHigh
        expr: increase(llm_fallback_requests_total[5m]) > 50
        for: 2m
        labels:
          severity: warning
          component: ai
        annotations:
          summary: "High LLM fallback rate"
          description: "Knowledge base is missing {{ $value }} queries in the last 5 minutes"
```

## 📈 Key Metrics

### **Backend Application Metrics**

```python
# Custom metrics exposed by the backend
http_requests_total = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
http_request_duration_seconds = Histogram('http_request_duration_seconds', 'HTTP request duration')
chat_messages_total = Counter('chat_messages_total', 'Total chat messages', ['agent', 'intent'])
chat_response_time_seconds = Histogram('chat_response_time_seconds', 'Chat response time')
knowledge_base_hits_total = Counter('knowledge_base_hits_total', 'Knowledge base hits', ['agent', 'category'])
llm_fallback_requests_total = Counter('llm_fallback_requests_total', 'LLM fallback requests')
websocket_connections_total = Gauge('websocket_connections_total', 'Active WebSocket connections')
user_satisfaction_score = Histogram('user_satisfaction_score', 'User satisfaction ratings')
```

### **System Metrics (Node Exporter)**

- **CPU Usage**: Per-core utilization and load averages
- **Memory**: Available, used, cached, swap utilization
- **Disk**: I/O operations, space utilization, read/write rates
- **Network**: Bandwidth utilization, packet rates, error rates
- **System**: Boot time, context switches, interrupts

### **Database Metrics (Postgres Exporter)**

- **Connection Pool**: Active, idle, waiting connections
- **Query Performance**: Execution time, rows processed, cache hit rates
- **Replication**: Lag, status, backup status
- **Storage**: Table sizes, index usage, vacuum statistics
- **pgvector**: Vector operations, index performance, search latency

### **Application Business Metrics**

- **Chat Analytics**: Volume, response times, satisfaction scores
- **AI Performance**: Intent classification accuracy, knowledge base effectiveness
- **User Engagement**: Session duration, feature usage, return rates
- **Support Quality**: Resolution rates, escalation patterns, common issues

## 🚨 Alerting Strategy

### **Alert Severity Levels**

- **Critical**: Service down, data loss, security breach
- **Warning**: Performance degradation, approaching limits
- **Info**: Deployment events, configuration changes

### **Alert Categories**

1. **System Health**: CPU, memory, disk, network thresholds
2. **Application Performance**: Response times, error rates, throughput
3. **Database Health**: Connection issues, slow queries, replication lag
4. **Business Metrics**: User satisfaction, AI effectiveness, support quality
5. **Security**: Authentication failures, rate limiting, suspicious activity

### **Notification Channels**

```yaml
# alertmanager.yml configuration
route:
  group_by: ["alertname", "severity"]
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: "web.hook"

receivers:
  - name: "web.hook"
    slack_configs:
      - api_url: "YOUR_SLACK_WEBHOOK_URL"
        channel: "#alerts"
        title: "Xfinity AI Alert"
        text: "{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}"

  - name: "email"
    email_configs:
      - to: "admin@company.com"
        subject: "Xfinity AI Alert: {{ .GroupLabels.alertname }}"
        body: "{{ range .Alerts }}{{ .Annotations.description }}{{ end }}"
```

## 📊 Dashboard Features

### **Backend API Dashboard**

- **Request Metrics**: RPS, response time percentiles, error rates
- **Resource Usage**: CPU, memory, database connections
- **AI Performance**: Agent response times, knowledge base hit rates
- **WebSocket Monitoring**: Active connections, message throughput

### **Database Dashboard**

- **Performance**: Query execution times, connection pool status
- **Storage**: Database size, table growth, index usage
- **Health**: Backup status, replication lag, vacuum statistics
- **pgvector**: Vector search performance, index efficiency

### **User Experience Dashboard**

- **Chat Analytics**: Message volume, response satisfaction
- **Feature Usage**: Page views, interaction patterns
- **Performance**: Page load times, error rates
- **Business KPIs**: Support resolution rates, user engagement

## 🔧 Customization

### **Adding New Metrics**

1. **Backend Application**: Add Prometheus metrics to your service

```python
from prometheus_client import Counter, Histogram, Gauge

custom_metric = Counter('custom_metric_total', 'Description', ['label1', 'label2'])
```

2. **Prometheus Configuration**: Add scrape targets

```yaml
scrape_configs:
  - job_name: "new-service"
    static_configs:
      - targets: ["new-service:port"]
```

3. **Grafana Dashboard**: Create visualization panels

```json
{
  "title": "Custom Metric",
  "type": "graph",
  "targets": [
    {
      "expr": "rate(custom_metric_total[5m])",
      "legendFormat": "Custom Rate"
    }
  ]
}
```

### **Creating Custom Alerts**

```yaml
# prometheus/rules/custom-alerts.yml
groups:
  - name: custom-alerts
    rules:
      - alert: CustomAlert
        expr: custom_metric_total > 100
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Custom threshold exceeded"
          description: "Value is {{ $value }}"
```

### **Dashboard Development**

1. **Access Grafana**: http://localhost:3001
2. **Create New Dashboard**: Click "+" → Dashboard
3. **Add Panels**: Configure queries, visualizations, thresholds
4. **Export JSON**: Save to `grafana/dashboards/` directory
5. **Version Control**: Commit dashboard changes

## 🛠️ Troubleshooting

### **Common Issues**

#### **Prometheus Not Scraping Targets**

```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Verify service endpoints
curl http://backend:8000/metrics
curl http://postgres-exporter:9187/metrics

# Check Prometheus logs
docker-compose logs prometheus
```

#### **Grafana Dashboard Issues**

```bash
# Check Grafana logs
docker-compose logs grafana

# Verify data source connectivity
curl -X POST http://admin:admin@localhost:3001/api/datasources/proxy/1/api/v1/query \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'query=up'

# Reset Grafana admin password
docker-compose exec grafana grafana-cli admin reset-admin-password newpassword
```

#### **Missing Metrics**

```bash
# Check if application is exposing metrics
curl http://localhost:8000/metrics

# Verify Prometheus configuration
docker-compose exec prometheus promtool check config /etc/prometheus/prometheus.yml

# Test alert rules
docker-compose exec prometheus promtool check rules /etc/prometheus/rules/*.yml
```

### **Performance Optimization**

#### **Prometheus Storage**

```yaml
# prometheus.yml
global:
  external_labels:
    replica: "01" # For federation

storage:
  tsdb:
    retention.time: 30d
    retention.size: 10GB
    wal-compression: true
```

#### **Grafana Performance**

```ini
# grafana.ini
[database]
type = postgres
host = grafana-db:5432
name = grafana
user = grafana
password = grafana

[server]
enable_gzip = true

[caching]
enabled = true
```

## 📊 Monitoring Best Practices

### **Metric Collection**

- **Four Golden Signals**: Latency, traffic, errors, saturation
- **Business Metrics**: User satisfaction, feature adoption, support quality
- **Custom Metrics**: Domain-specific KPIs and performance indicators

### **Dashboard Design**

- **Hierarchy**: Overview → Service → Component dashboards
- **Time Ranges**: Multiple time windows for different analysis needs
- **Thresholds**: Visual indicators for normal, warning, critical states
- **Annotations**: Deployment markers, incident timelines

### **Alert Management**

- **Meaningful Alerts**: Focus on actionable issues
- **Alert Fatigue**: Tune thresholds to reduce noise
- **Escalation**: Progressive notification channels
- **Documentation**: Runbooks for common alerts

## 🔮 Advanced Features

### **Service Level Objectives (SLOs)**

```yaml
# Example SLO configuration
slos:
  - name: "API Availability"
    target: 99.9
    indicators:
      - query: "sum(rate(http_requests_total{status!~'5..'}[5m])) / sum(rate(http_requests_total[5m]))"

  - name: "Response Time"
    target: 95
    indicators:
      - query: "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) < 0.2"
```

### **Anomaly Detection**

Integration with machine learning-based anomaly detection for predictive alerting and trend analysis.

### **Multi-Environment Monitoring**

Federation setup for monitoring development, staging, and production environments from a central location.

---

For additional monitoring setup and configuration details, see the [infrastructure documentation](../infrastructure/README.md) and [main project README](../README.md).
