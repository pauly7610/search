# Infrastructure & Deployment

This directory contains comprehensive infrastructure-as-code and deployment configurations for the **Xfinity Agentic AI Demo Platform**. Supports local development, container orchestration, and cloud deployment with enterprise-grade monitoring and MLOps capabilities.

## 🏗️ Architecture Components

### **Core Services**

- **Backend API**: FastAPI with LangChain and multi-agent AI
- **Frontend UI**: React with dark theme and real-time chat
- **Database**: PostgreSQL with vector extensions (pgvector)
- **Cache**: Redis for session storage and response caching
- **Message Queue**: Redis for async task processing

### **Monitoring Stack**

- **Prometheus**: Metrics collection and alerting rules
- **Grafana**: Interactive dashboards and visualizations
- **Node Exporter**: System metrics collection
- **Postgres Exporter**: Database performance monitoring
- **Alert Manager**: Notification routing and management

### **MLOps & Data Science**

- **Jupyter Hub**: Notebook environment for model development
- **MLflow**: Experiment tracking and model registry
- **Apache Airflow**: Workflow orchestration (optional)
- **Vector Database**: Semantic search capabilities

## 🚀 Deployment Options

### **Local Development (Recommended for Demo)**

```bash
# Full stack with all services
docker-compose -f infrastructure/docker-compose.yml up --build

# Include monitoring stack
docker-compose -f monitoring/docker-compose.monitoring.yml up -d

# MLOps stack (optional)
docker-compose -f infrastructure/docker-compose.mlops.yml up -d
```

**Services Available:**

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001 (admin/admin)
- MLflow: http://localhost:5000
- Jupyter: http://localhost:8888

### **Production Kubernetes**

```bash
# Deploy core services
kubectl apply -f infrastructure/kubernetes/namespace.yaml
kubectl apply -f infrastructure/kubernetes/configmaps/
kubectl apply -f infrastructure/kubernetes/secrets/
kubectl apply -f infrastructure/kubernetes/deployments/
kubectl apply -f infrastructure/kubernetes/services/
kubectl apply -f infrastructure/kubernetes/ingress/

# Deploy monitoring
kubectl apply -f infrastructure/kubernetes/monitoring/

# Verify deployment
kubectl get pods -n xfinity-ai
kubectl get services -n xfinity-ai
```

### **Cloud Deployment (Terraform)**

```bash
cd infrastructure/terraform/

# Initialize and plan
terraform init
terraform plan -var-file="environments/production.tfvars"

# Deploy infrastructure
terraform apply -var-file="environments/production.tfvars"

# Get output values
terraform output
```

**Supported Cloud Providers:**

- AWS: EKS, RDS, ElastiCache, ALB
- GCP: GKE, Cloud SQL, Memorystore, Load Balancer
- Azure: AKS, Azure Database, Redis Cache, Application Gateway

## 📁 Directory Structure

```
infrastructure/
├── docker-compose.yml              # Main development stack
├── docker-compose.mlops.yml        # MLOps services
├── kubernetes/                     # K8s manifests
│   ├── namespace.yaml             # Namespace definition
│   ├── configmaps/                # Configuration management
│   │   ├── backend-config.yaml    # Backend configuration
│   │   ├── frontend-config.yaml   # Frontend configuration
│   │   └── monitoring-config.yaml # Monitoring settings
│   ├── secrets/                   # Secret management
│   │   ├── api-keys.yaml         # API keys and tokens
│   │   ├── database-creds.yaml   # Database credentials
│   │   └── tls-certs.yaml        # TLS certificates
│   ├── deployments/               # Application deployments
│   │   ├── backend-deployment.yaml
│   │   ├── frontend-deployment.yaml
│   │   ├── postgres-deployment.yaml
│   │   ├── redis-deployment.yaml
│   │   └── mlflow-deployment.yaml
│   ├── services/                  # Service definitions
│   │   ├── backend-service.yaml
│   │   ├── frontend-service.yaml
│   │   ├── postgres-service.yaml
│   │   └── redis-service.yaml
│   ├── ingress/                   # Ingress controllers
│   │   ├── main-ingress.yaml
│   │   └── monitoring-ingress.yaml
│   ├── monitoring/                # Monitoring stack
│   │   ├── prometheus.yaml
│   │   ├── grafana.yaml
│   │   └── alertmanager.yaml
│   ├── storage/                   # Persistent volumes
│   │   ├── postgres-pvc.yaml
│   │   └── grafana-pvc.yaml
│   └── rbac/                      # Role-based access
│       ├── service-accounts.yaml
│       ├── roles.yaml
│       └── role-bindings.yaml
├── terraform/                     # Cloud infrastructure
│   ├── main.tf                   # Main configuration
│   ├── variables.tf              # Input variables
│   ├── outputs.tf                # Output values
│   ├── versions.tf               # Provider versions
│   ├── modules/                  # Reusable modules
│   │   ├── eks/                  # AWS EKS module
│   │   ├── gke/                  # GCP GKE module
│   │   ├── aks/                  # Azure AKS module
│   │   ├── database/             # Database module
│   │   ├── monitoring/           # Monitoring module
│   │   └── networking/           # Network module
│   └── environments/             # Environment configs
│       ├── development.tfvars
│       ├── staging.tfvars
│       └── production.tfvars
└── packer/                       # Image building
    ├── webserver.pkr.hcl         # Web server image
    ├── api-server.pkr.hcl        # API server image
    └── ansible/                   # Configuration scripts
        └── playbook_bake_image.yml
```

## 🔧 Configuration Management

### **Environment Variables**

Create environment-specific configuration files:

```yaml
# kubernetes/configmaps/backend-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: backend-config
  namespace: xfinity-ai
data:
  ENVIRONMENT: "production"
  LOG_LEVEL: "INFO"
  DATABASE_HOST: "postgres-service"
  REDIS_HOST: "redis-service"
  PROMETHEUS_PORT: "9090"
  GRAFANA_PORT: "3001"
```

### **Secrets Management**

```yaml
# kubernetes/secrets/api-keys.yaml (base64 encoded)
apiVersion: v1
kind: Secret
metadata:
  name: api-keys
  namespace: xfinity-ai
type: Opaque
data:
  openai-api-key: <base64-encoded-key>
  sentry-dsn: <base64-encoded-dsn>
  jwt-secret: <base64-encoded-secret>
```

### **Database Configuration**

```yaml
# kubernetes/deployments/postgres-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: xfinity-ai
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
        - name: postgres
          image: postgres:15-alpine
          env:
            - name: POSTGRES_DB
              value: "xfinity_ai"
            - name: POSTGRES_USER
              valueFrom:
                secretKeyRef:
                  name: database-creds
                  key: username
            - name: POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: database-creds
                  key: password
          ports:
            - containerPort: 5432
          volumeMounts:
            - name: postgres-storage
              mountPath: /var/lib/postgresql/data
          resources:
            requests:
              memory: "1Gi"
              cpu: "500m"
            limits:
              memory: "2Gi"
              cpu: "1000m"
```

## 📊 Monitoring & Observability

### **Prometheus Configuration**

```yaml
# kubernetes/monitoring/prometheus.yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "/etc/prometheus/rules/*.yml"

scrape_configs:
  - job_name: "xfinity-backend"
    static_configs:
      - targets: ["backend-service:8000"]
    metrics_path: "/metrics"
    scrape_interval: 30s

  - job_name: "postgres-exporter"
    static_configs:
      - targets: ["postgres-exporter:9187"]

  - job_name: "node-exporter"
    kubernetes_sd_configs:
      - role: endpoints
    relabel_configs:
      - source_labels: [__meta_kubernetes_service_name]
        target_label: __meta_kubernetes_service_name
        regex: node-exporter
```

### **Grafana Dashboard Provisioning**

```yaml
# kubernetes/monitoring/grafana-dashboards.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-dashboards
  namespace: xfinity-ai
data:
  dashboard-provider.yaml: |
    apiVersion: 1
    providers:
    - name: 'default'
      orgId: 1
      folder: ''
      type: file
      disableDeletion: false
      updateIntervalSeconds: 10
      options:
        path: /var/lib/grafana/dashboards
```

## 🔒 Security & Compliance

### **Network Policies**

```yaml
# kubernetes/rbac/network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: xfinity-ai-network-policy
  namespace: xfinity-ai
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: ingress-nginx
      ports:
        - protocol: TCP
          port: 8000
  egress:
    - to: []
      ports:
        - protocol: TCP
          port: 443
        - protocol: TCP
          port: 5432
```

### **RBAC Configuration**

```yaml
# kubernetes/rbac/service-accounts.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: xfinity-ai-backend
  namespace: xfinity-ai
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: xfinity-ai-role
  namespace: xfinity-ai
rules:
  - apiGroups: [""]
    resources: ["configmaps", "secrets"]
    verbs: ["get", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: xfinity-ai-binding
  namespace: xfinity-ai
subjects:
  - kind: ServiceAccount
    name: xfinity-ai-backend
    namespace: xfinity-ai
roleRef:
  kind: Role
  name: xfinity-ai-role
  apiGroup: rbac.authorization.k8s.io
```

## 🚀 Scaling & Performance

### **Horizontal Pod Autoscaling**

```yaml
# kubernetes/autoscaling/backend-hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
  namespace: xfinity-ai
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

### **Load Balancing**

```yaml
# kubernetes/ingress/main-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: xfinity-ai-ingress
  namespace: xfinity-ai
  annotations:
    kubernetes.io/ingress.class: "nginx"
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
spec:
  tls:
    - hosts:
        - api.xfinity-ai.com
        - app.xfinity-ai.com
      secretName: tls-secret
  rules:
    - host: api.xfinity-ai.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: backend-service
                port:
                  number: 8000
    - host: app.xfinity-ai.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: frontend-service
                port:
                  number: 80
```

## 🔧 Operational Commands

### **Local Development**

```bash
# Start full stack
docker-compose up --build

# Scale specific services
docker-compose up --scale backend=3

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Database operations
docker-compose exec postgres psql -U user -d xfinity_ai

# Redis operations
docker-compose exec redis redis-cli
```

### **Kubernetes Operations**

```bash
# Apply configurations
kubectl apply -f kubernetes/

# Check pod status
kubectl get pods -n xfinity-ai -w

# View logs
kubectl logs -f deployment/backend -n xfinity-ai
kubectl logs -f deployment/frontend -n xfinity-ai

# Execute commands in pods
kubectl exec -it deployment/backend -n xfinity-ai -- /bin/bash

# Port forwarding for debugging
kubectl port-forward service/backend-service 8000:8000 -n xfinity-ai
kubectl port-forward service/grafana 3001:3000 -n xfinity-ai

# Scale deployments
kubectl scale deployment backend --replicas=5 -n xfinity-ai

# Update rolling deployment
kubectl set image deployment/backend backend=xfinity-ai:v2.0.0 -n xfinity-ai
```

### **Cloud Operations**

```bash
# Terraform operations
cd infrastructure/terraform/
terraform plan -var-file="environments/production.tfvars"
terraform apply -var-file="environments/production.tfvars"
terraform destroy -var-file="environments/production.tfvars"

# AWS specific
aws eks update-kubeconfig --region us-west-2 --name xfinity-ai-cluster
aws logs describe-log-groups --log-group-name-prefix="/aws/eks/xfinity-ai"

# GCP specific
gcloud container clusters get-credentials xfinity-ai-cluster --zone us-central1-a
gcloud logging logs list --filter="resource.type=k8s_container"

# Azure specific
az aks get-credentials --resource-group xfinity-ai-rg --name xfinity-ai-cluster
az monitor log-analytics query --workspace xfinity-ai-workspace
```

## 🧪 Testing & Validation

### **Infrastructure Testing**

```bash
# Test Docker Compose setup
docker-compose config
docker-compose up --dry-run

# Validate Kubernetes manifests
kubectl apply --dry-run=client -f kubernetes/
kubectl apply --dry-run=server -f kubernetes/

# Terraform validation
terraform validate
terraform plan -detailed-exitcode
```

### **Load Testing**

```bash
# Install k6 for load testing
brew install k6

# Run load tests
k6 run infrastructure/tests/load-test.js

# Monitor during load test
kubectl top pods -n xfinity-ai
kubectl get hpa -n xfinity-ai -w
```

## 🛠️ Troubleshooting

### **Common Issues**

1. **Pod Startup Issues**

   ```bash
   kubectl describe pod <pod-name> -n xfinity-ai
   kubectl logs <pod-name> -n xfinity-ai --previous
   ```

2. **Network Connectivity**

   ```bash
   kubectl exec -it <pod-name> -n xfinity-ai -- nslookup backend-service
   kubectl get networkpolicy -n xfinity-ai
   ```

3. **Resource Constraints**

   ```bash
   kubectl top nodes
   kubectl top pods -n xfinity-ai
   kubectl describe nodes
   ```

4. **Storage Issues**
   ```bash
   kubectl get pv,pvc -n xfinity-ai
   kubectl describe pvc <pvc-name> -n xfinity-ai
   ```

### **Monitoring Alerts**

```yaml
# kubernetes/monitoring/alert-rules.yaml
groups:
  - name: xfinity-ai-alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors per second"

      - alert: DatabaseConnectionFailure
        expr: up{job="postgres-exporter"} == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Database connection failure"
          description: "PostgreSQL is not responding"
```

---

## 📞 Support & Maintenance

### **Backup & Recovery**

```bash
# Database backup
kubectl exec deployment/postgres -n xfinity-ai -- pg_dump -U user xfinity_ai > backup.sql

# Restore database
kubectl exec -i deployment/postgres -n xfinity-ai -- psql -U user xfinity_ai < backup.sql

# Grafana dashboard backup
kubectl cp xfinity-ai/grafana-pod:/var/lib/grafana/grafana.db ./grafana-backup.db
```

### **Updates & Maintenance**

```bash
# Rolling update backend
kubectl set image deployment/backend backend=xfinity-ai:v2.1.0 -n xfinity-ai
kubectl rollout status deployment/backend -n xfinity-ai

# Rollback if needed
kubectl rollout undo deployment/backend -n xfinity-ai

# Update configurations
kubectl apply -f kubernetes/configmaps/
kubectl rollout restart deployment/backend -n xfinity-ai
```

For additional support, see the [main documentation](../docs/README.md) and [monitoring guide](../monitoring/README.md).
