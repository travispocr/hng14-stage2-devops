# HNG Stage 2 — Job Processing Microservices

A containerized job processing system built with three services: a Node.js frontend, a Python/FastAPI backend, and a Python worker, connected via Redis.

## Architecture

```
frontend (Node.js :3000)
    └── HTTP → api (FastAPI :8000)
                    └── Redis queue
                              └── worker (Python)
```

## Prerequisites

- Docker >= 24.0
- Docker Compose >= 2.0
- Git

## Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/travispocr/hng14-stage2-devops.git
cd hng14-stage2-devops
```

### 2. Set up environment variables
```bash
cp .env.example .env
# Edit .env and set a strong REDIS_PASSWORD
```

### 3. Build and start all services
```bash
docker compose up --build
```

### 4. Verify startup
You should see:
```
redis-1    | Ready to accept connections tcp
api-1      | Uvicorn running on http://0.0.0.0:8000
frontend-1 | Frontend running on port 3000
```

### 5. Open the dashboard
Visit http://localhost:3000 in your browser.

Click **Submit New Job** — the job should go from `queued` to `completed` within a few seconds.

## Endpoints

### Frontend (port 3000)
| Method | Path | Description |
|--------|------|-------------|
| GET | / | Job dashboard UI |
| POST | /submit | Submit a new job |
| GET | /status/:id | Get job status |

### API (port 8000)
| Method | Path | Description |
|--------|------|-------------|
| POST | /jobs | Create a new job |
| GET | /jobs/:id | Get job status |

## Environment Variables

See `.env.example` for all required variables:

| Variable | Description | Default |
|----------|-------------|---------|
| REDIS_PASSWORD | Redis auth password | required |
| REDIS_HOST | Redis hostname | redis |
| REDIS_PORT | Redis port | 6379 |
| API_URL | API base URL for frontend | http://api:8000 |
| QUEUE_NAME | Redis queue name | jobs |

## Stopping the stack
```bash
docker compose down
```

To remove volumes as well:
```bash
docker compose down -v
```

## Running Tests
```bash
cd api
pip install -r requirements.txt pytest pytest-cov
pytest tests/ -v --cov=main --cov-report=term-missing
```

## CI/CD Pipeline

The GitHub Actions pipeline runs on every push with these stages in order:
`lint → test → build → security scan → integration test → deploy`

## Bugs Fixed

See [FIXES.md](./FIXES.md) for a full list of all 12 bugs found and fixed.