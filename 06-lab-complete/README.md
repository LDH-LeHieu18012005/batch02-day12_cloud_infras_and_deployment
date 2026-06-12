# Lab 12 - Complete Production Agent

This folder contains the final Day 12 production-ready AI agent.

## Features

- FastAPI agent endpoint: `POST /ask`
- API key authentication with `X-API-Key`
- Redis-backed sliding-window rate limiting
- Redis-backed daily cost guard
- Redis-backed conversation history for stateless scaling
- Health and readiness probes
- Structured JSON logs
- Graceful shutdown handling
- Multi-stage Dockerfile running as a non-root user
- Docker Compose stack with Nginx + agent + Redis
- Railway and Render deployment config

## Project Structure

```text
06-lab-complete/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── auth.py
│   ├── rate_limiter.py
│   ├── cost_guard.py
│   └── storage.py
├── utils/
│   └── mock_llm.py
├── Dockerfile
├── docker-compose.yml
├── nginx.conf
├── railway.toml
├── render.yaml
├── .env.example
├── .dockerignore
└── requirements.txt
```

## Run Locally With Docker Compose

```bash
docker compose up --build
```

Scale the stateless agent behind Nginx:

```bash
docker compose up -d --scale agent=3
```

Test health:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/ready
```

Test authentication:

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"user_id":"student1","question":"Hello"}'
```

Expected: `401 Unauthorized`.

Test with API key:

```bash
curl -X POST http://localhost:8000/ask \
  -H "X-API-Key: dev-key-change-me-in-production" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"student1","question":"What is Docker?"}'
```

Test conversation history:

```bash
curl http://localhost:8000/chat/<SESSION_ID>/history \
  -H "X-API-Key: dev-key-change-me-in-production"
```

Test rate limiting:

```bash
for i in {1..15}; do
  curl -s -o /dev/null -w "%{http_code}\n" \
    -X POST http://localhost:8000/ask \
    -H "X-API-Key: dev-key-change-me-in-production" \
    -H "Content-Type: application/json" \
    -d '{"user_id":"student1","question":"rate limit test"}'
done
```

Expected: requests eventually return `429`.

## Required Environment Variables

```text
PORT
ENVIRONMENT
AGENT_API_KEY
JWT_SECRET
REDIS_URL
RATE_LIMIT_PER_MINUTE
DAILY_BUDGET_USD
ALLOWED_ORIGINS
```

## Deploy Notes

For Railway or Render, create a Redis service/add-on and set `REDIS_URL`.
Set `AGENT_API_KEY` and `JWT_SECRET` as secrets on the platform.
Do not commit `.env.local` or real API keys.
