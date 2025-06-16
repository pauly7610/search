# Infrastructure & Deployment

This directory contains all infrastructure-as-code and deployment configuration for the Xfinity Agentic AI Demo Platform.

## Components

- **Docker Compose:** For local development and demo (`docker-compose.yml`)
- **Kubernetes:** Manifests for backend, frontend, and Postgres (`kubernetes/`)
- **Terraform:** Cloud infrastructure as code (cloud-agnostic, see `terraform/`)

## How to Use

### Local Development

```bash
docker-compose -f infrastructure/docker-compose.yml up --build
```

### Kubernetes (example)

```bash
kubectl apply -f infrastructure/kubernetes/
```

### Terraform (cloud)

- Edit variables in `terraform/variables.tf`
- Run `terraform init && terraform apply` in `infrastructure/terraform/`

## Extending

- Add new services to Compose or K8s as needed
- Add cloud resources in Terraform

---

See the root README and docs for more.
