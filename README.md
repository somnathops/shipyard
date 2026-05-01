# Shipyard

A collection of real-world applications built and deployed using modern DevOps practices. Each project is independently containerized, versioned, and deployed — first with Docker Compose for local development, then migrated to Kubernetes for production-grade orchestration.

---

## What is Shipyard?

Shipyard is a personal platform engineering lab. Every app here follows the same production-like workflow:

```
Code → Dockerfile → Docker Compose (local) → Kubernetes (prod-like)
```

Each project demonstrates:
- Containerization with Docker
- Multi-service orchestration with Docker Compose
- Kubernetes deployment with zero downtime rolling updates
- Persistent storage, secrets management, and service discovery
- Image versioning and release workflow

---

## Projects

| Project | Stack | Status |
|---------|-------|--------|
| [expense-tracker](./expense-tracker/) | FastAPI + Streamlit + PostgreSQL | ✅ Deployed on k8s |

---

## Repository Structure

```
shipyard/
├── expense-tracker/        ← project 1
│   ├── backend/
│   ├── frontend/
│   ├── k8s/
│   ├── docker-compose.yml
│   ├── Makefile
│   ├── VERSION
│   └── README.md
├── next-app/               ← project 2 (coming soon)
│   └── ...
└── README.md               ← you are here
```

Each project is self-contained with its own Dockerfile, docker-compose, k8s manifests, Makefile and VERSION file.

---

## Architecture Pattern

Every project in Shipyard follows this deployment architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                        kind Cluster                         │
│                                                             │
│  secret.yaml          ← credentials (never hardcoded)      │
│       │                                                     │
│  postgres-pvc.yaml    ← persistent storage (data safe)      │
│       │                                                     │
│  postgres-deploy.yaml ← Deployment (1 replica)             │
│       │                  ClusterIP Service                  │
│       │ DATABASE_URL                                        │
│  backend-deploy.yaml  ← Deployment (2 replicas)            │
│       │                  ClusterIP Service (internal only)  │
│       │ API_URL                                             │
│  frontend-deploy.yaml ← Deployment (2 replicas)            │
│                          NodePort Service                   │
│                               │                            │
└───────────────────────────────┼────────────────────────────┘
                                │ NodePort / port-forward
                             Browser
```

### Why 2 replicas for backend and frontend?

```
1 replica → pod update = downtime
2 replicas → rolling update = zero downtime

strategy:
  maxUnavailable: 0   ← never kill old pod before new is ready
  maxSurge: 1         ← spin up one extra pod during update
```

### Why ClusterIP for backend and database?

```
Database  → ClusterIP   never expose DB to the internet
Backend   → ClusterIP   API only reachable inside the cluster
Frontend  → NodePort    browser needs to reach the UI
```

---

## Deployment Flow

```
Developer writes code
        │
        ▼
  make build              ← builds versioned Docker image
        │
        ▼
  make push               ← pushes to Docker Hub
        │
        ├─────────────────────────────┐
        ▼                             ▼
Docker Compose                  Kubernetes
(local dev)                     (prod-like)
        │                             │
docker-compose up -d          kubectl apply -f k8s/
        │                             │
All services running           Pods running with
with .env config               Secrets + PVC + Services
```

---

## Release & Rollback Workflow

```bash
# bump version
echo "1.1" > VERSION
sed -i '' 's/IMAGE_TAG=.*/IMAGE_TAG=1.1/' .env

# build + push
make ship

# deploy to k8s (rolling update — zero downtime)
kubectl set image deployment/<app>-backend  <container>=mycloudhub/<app>-backend:1.1
kubectl set image deployment/<app>-frontend <container>=mycloudhub/<app>-frontend:1.1

# rollback if something breaks
kubectl rollout undo deployment/<app>-backend
kubectl rollout undo deployment/<app>-frontend
```

---

## Tools & Technologies

| Category | Tool |
|----------|------|
| Containerization | Docker |
| Local Orchestration | Docker Compose |
| Production Orchestration | Kubernetes (kind) |
| Image Registry | Docker Hub |
| Build Automation | Makefile |
| Version Control | Git + GitHub |
| Languages | Python |

---

## Local Setup

### Prerequisites
```
Docker Desktop
kind
kubectl
make
```

### Run any project locally
```bash
cd <project-name>
cp .env.example .env     # fill in your values
make build
docker-compose up -d
```

### Deploy any project to Kubernetes
```bash
cd <project-name>
make ship
kubectl apply -f k8s/
kubectl get pods -w
```

---

## Upcoming Projects

- URL Shortener
- Task Manager
- Monitoring Stack (Prometheus + Grafana)
- API Gateway pattern
