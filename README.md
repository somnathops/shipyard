<<<<<<< HEAD
# Expense Tracker

A full-stack expense tracking application built with FastAPI, Streamlit, and PostgreSQL. Originally deployed with Docker Compose, then migrated to Kubernetes without any data loss.

---

## Tech Stack

| Layer     | Technology              |
|-----------|-------------------------|
| Frontend  | Streamlit (Python)      |
| Backend   | FastAPI (Python)        |
| Database  | PostgreSQL 15           |
| Container | Docker                  |
| Orchestration | Kubernetes (kind)   |

---

## Architecture

### Application Flow

```
Browser
  │
  │  http://localhost:8502 (Docker) or NodePort 30080 (k8s)
  ▼
┌─────────────────────────────┐
│         Frontend            │
│        (Streamlit)          │
│         Port 8501           │
│                             │
│  - Dashboard                │
│  - Add Expense              │
│  - History                  │
│  - Analytics                │
└─────────────┬───────────────┘
              │
              │  http://backend:8080 (Docker)
              │  http://expense-tracker-backend-service:8080 (k8s)
              ▼
┌─────────────────────────────┐
│         Backend             │
│         (FastAPI)           │
│         Port 8080           │
│                             │
│  GET  /health               │
│  GET  /categories           │
│  POST /expenses             │
│  GET  /expenses             │
│  DEL  /expenses/{id}        │
│  GET  /summary              │
│  GET  /monthly-trend        │
└─────────────┬───────────────┘
              │
              │  postgresql://postgres:5432 (Docker)
              │  postgresql://postgres-service:5432 (k8s)
              ▼
┌─────────────────────────────┐
│         Database            │
│       (PostgreSQL 15)       │
│         Port 5432           │
│                             │
│  Table: expenses            │
│  - id                       │
│  - amount                   │
│  - category                 │
│  - description              │
│  - date                     │
│  - created_at               │
└─────────────────────────────┘
```

### Kubernetes Architecture

```
                         kind Cluster
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   ┌─────────────────────────────────────────────────┐   │
│   │              secret.yaml                        │   │
│   │         (postgres credentials)                  │   │
│   └──────────────────┬──────────────────────────────┘   │
│                      │ used by                          │
│   ┌──────────────────▼──────────────────────────────┐   │
│   │           postgres-pvc.yaml                     │   │
│   │            (1Gi storage)                        │   │
│   └──────────────────┬──────────────────────────────┘   │
│                      │ mounted by                       │
│   ┌──────────────────▼──────────────────────────────┐   │
│   │          postgres-deploy.yaml                   │   │
│   │    Deployment (replicas: 1) + ClusterIP Service │   │
│   │           postgres-service:5432                 │   │
│   └──────────────────┬──────────────────────────────┘   │
│                      │ DATABASE_URL                     │
│   ┌──────────────────▼──────────────────────────────┐   │
│   │          backend-deploy.yaml                    │   │
│   │    Deployment (replicas: 2) + ClusterIP Service │   │
│   │    expense-tracker-backend-service:8080         │   │
│   └──────────────────┬──────────────────────────────┘   │
│                      │ API_URL                          │
│   ┌──────────────────▼──────────────────────────────┐   │
│   │          frontend-deploy.yaml                   │   │
│   │    Deployment (replicas: 2) + NodePort Service  │   │
│   │           localhost:30080                       │   │
│   └─────────────────────────────────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
          ▲
          │ kubectl port-forward or NodePort 30080
          │
       Browser
```

---

## Project Structure

```
expense-tracker/
├── backend/
│   ├── Dockerfile
│   ├── main.py              # FastAPI app — all API routes
│   └── requirements.txt
├── frontend/
│   ├── Dockerfile
│   ├── app.py               # Streamlit entry point
│   ├── api.py               # backend API calls
│   ├── requirements.txt
│   └── pages/
│       ├── dashboard.py     # monthly summary + recent transactions
│       ├── add_expense.py   # expense form
│       ├── history.py       # filterable expense list
│       └── analytics.py     # charts and trends
├── k8s/
│   ├── secret.yaml          # DB credentials (base64 encoded)
│   ├── postgres-pvc.yaml    # persistent storage for postgres
│   ├── postgres-deploy.yaml # postgres Deployment + ClusterIP Service
│   ├── backend-deploy.yaml  # backend Deployment + ClusterIP Service
│   └── frontend-deploy.yaml # frontend Deployment + NodePort Service
├── .env                     # local secrets (never commit)
├── .gitignore
├── docker-compose.yml       # local development
├── Makefile                 # build, push, ship commands
├── VERSION                  # current image version
└── README.md
```

---

## Running Locally with Docker Compose

### Prerequisites
- Docker Desktop running
- Docker Hub account

### Setup

**1. Create `.env` file:**
```bash
cp .env.example .env
# edit .env with your values
```

**2. Build images:**
```bash
make build
```

**3. Start all services:**
```bash
docker-compose up -d
```

**4. Access the app:**
```
Frontend:  http://localhost:8502
Backend:   http://localhost:8000
API Docs:  http://localhost:8000/docs
```

**5. Stop services:**
```bash
docker-compose down
```

### Release a new version

```bash
# bump version
echo "1.1" > VERSION
sed -i '' 's/IMAGE_TAG=.*/IMAGE_TAG=1.1/' .env

# build, tag, push
make ship

# restart with new version
docker-compose pull
docker-compose up -d
```

### Rollback

```bash
# change .env to previous version
sed -i '' 's/IMAGE_TAG=.*/IMAGE_TAG=1.0/' .env

docker-compose pull
docker-compose up -d
```

---

## Deploying to Kubernetes

### Prerequisites
- kind installed
- kubectl installed
- Images pushed to Docker Hub (`make ship`)

### Create kind cluster

```bash
kind create cluster --name control-plane --config kind-cluster.yaml
```

### Apply manifests

```bash
# apply in order (or all at once)
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/postgres-pvc.yaml
kubectl apply -f k8s/postgres-deploy.yaml
kubectl apply -f k8s/backend-deploy.yaml
kubectl apply -f k8s/frontend-deploy.yaml

# or all at once
kubectl apply -f k8s/
```

### Verify everything is running

```bash
kubectl get pods
kubectl get svc
```

Expected output:
```
NAME                                      READY   STATUS    RESTARTS
expense-tracker-backend-xxx               1/1     Running   0
expense-tracker-backend-yyy               1/1     Running   0
expense-tracker-frontend-xxx              1/1     Running   0
expense-tracker-frontend-yyy              1/1     Running   0
postgres-xxx                              1/1     Running   0
```

### Access the app

```bash
kubectl port-forward svc/expense-tracker-frontend-service 8080:80
```

Open browser at `http://localhost:8080`

### Deploy a new version

```bash
# update image in deployment
kubectl set image deployment/expense-tracker-backend \
  expense-tracker-backend=mycloudhub/expense-backend:1.1

kubectl set image deployment/expense-tracker-frontend \
  expense-tracker-frontend=mycloudhub/expense-frontend:1.1
```

Kubernetes performs a rolling update — zero downtime.

### Rollback in Kubernetes

```bash
kubectl rollout undo deployment/expense-tracker-backend
kubectl rollout undo deployment/expense-tracker-frontend
```

---

## Migration — Docker Compose to Kubernetes

This app was originally running on Docker Compose with live data in a postgres container. The goal was to migrate everything to Kubernetes without any data loss.

### Migration Architecture

```
BEFORE (Docker Compose)                AFTER (Kubernetes)

docker-compose.yml                     k8s/ manifests
  ├── postgres container       →         ├── postgres-deploy.yaml
  │     └── named volume       →         ├── postgres-pvc.yaml (1Gi PVC)
  ├── backend container        →         ├── backend-deploy.yaml
  └── frontend container       →         └── frontend-deploy.yaml

localhost:8502 (frontend)              NodePort 30080 (frontend)
localhost:8000 (backend)               ClusterIP (internal only)
localhost:5432 (postgres)              ClusterIP (internal only)
```

### Why migration was needed

Docker Compose runs everything on a single machine with no high availability. Moving to Kubernetes gives:
- **Zero downtime deployments** via rolling updates
- **Auto restart** if a pod crashes
- **Multiple replicas** for backend and frontend
- **Persistent storage** via PVC that survives pod restarts

### Step by step migration

**Step 1 — Inspect existing data before touching anything**
```bash
# exec into running Docker postgres and verify data
docker exec -it expense-db psql -U admin -d expenses

# inside postgres shell
\dt                                          # list tables
SELECT COUNT(*) FROM expenses;               # count records
SELECT * FROM expenses LIMIT 5;             # preview data
\q                                           # exit
```

**Step 2 — Take a full SQL backup from Docker**
```bash
# pg_dump exports entire database as SQL statements
# saves to backup.sql on your local machine
docker exec expense-db pg_dump -U admin expenses > backup.sql

# verify backup was created and has content
cat backup.sql | head -20
```

**Step 3 — Apply all Kubernetes manifests**
```bash
kubectl apply -f k8s/secret.yaml          # credentials first
kubectl apply -f k8s/postgres-pvc.yaml    # storage before database
kubectl apply -f k8s/postgres-deploy.yaml # database before backend
kubectl apply -f k8s/backend-deploy.yaml  # backend before frontend
kubectl apply -f k8s/frontend-deploy.yaml # frontend last
```

**Step 4 — Wait for postgres pod to be ready**
```bash
kubectl get pods -w    # watch until postgres shows 1/1 Running
```

**Step 5 — Copy backup into the postgres pod**
```bash
# get the exact postgres pod name
kubectl get pods | grep postgres

# copy backup.sql from your machine into the pod
kubectl cp backup.sql <postgres-pod-name>:/tmp/backup.sql
```

**Step 6 — Restore data into Kubernetes postgres**
```bash
# psql -f replays all SQL statements from the backup file
kubectl exec <postgres-pod-name> -- psql -U admin -d expenses -f /tmp/backup.sql
```

> Note: You may see errors like `relation "expenses" already exists` — this is expected.
> The backend's `init_db()` already created the empty table on startup.
> The important line is `COPY N` which confirms your rows were inserted successfully.

**Step 7 — Verify data is intact**
```bash
kubectl exec <postgres-pod-name> -- psql -U admin -d expenses -c "SELECT COUNT(*) FROM expenses;"
kubectl exec <postgres-pod-name> -- psql -U admin -d expenses -c "SELECT * FROM expenses LIMIT 5;"
```

**Step 8 — Access the migrated app**
```bash
kubectl port-forward svc/expense-tracker-frontend-service 8080:80
# open http://localhost:8080 — all your data should be there
```

**Step 9 — Stop Docker Compose (once verified)**
```bash
docker-compose down
```

---

## API Endpoints

| Method | Endpoint          | Description                        |
|--------|-------------------|------------------------------------|
| GET    | /health           | Health check                       |
| GET    | /categories       | List expense categories            |
| POST   | /expenses         | Add a new expense                  |
| GET    | /expenses         | List expenses (filter by month/category) |
| DELETE | /expenses/{id}    | Delete an expense                  |
| GET    | /summary          | Monthly total + category breakdown |
| GET    | /monthly-trend    | Last 6 months spending trend       |

Full interactive docs available at `http://localhost:8000/docs`

---

## Environment Variables

| Variable      | Description              | Default                                           |
|---------------|--------------------------|---------------------------------------------------|
| DATABASE_URL  | PostgreSQL connection    | postgresql://admin:secret@localhost:5432/expenses |
| API_URL       | Backend API URL          | http://localhost:8000                             |
| IMAGE_TAG     | Docker image version     | 1.0                                               |
| TZ            | Timezone                 | Asia/Kolkata                                      |

---

## Makefile Commands

```bash
make build   # build docker images
make push    # push images to Docker Hub
make ship    # build + push (release)
```
=======
# shipyard
>>>>>>> a04ab8740c0a8dbf5c211b463477b105a441c720
