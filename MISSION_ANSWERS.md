# Day 12 Lab - Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found

1. Hardcoded configuration such as host, port, model names, and secrets.
2. Secrets stored directly in source code instead of environment variables.
3. No health check or readiness endpoint for cloud platforms.
4. No structured logging, making production debugging difficult.
5. No input validation for API requests.
6. No authentication, so anyone can call the public endpoint.
7. Stateful in-memory data, which breaks when scaling to multiple instances.
8. No graceful shutdown handling for deploys or container termination.

### Exercise 1.2: Basic version

The basic version is in `01-localhost-vs-production/develop`. It demonstrates a local-only agent that can answer requests but does not meet production requirements.

Run:

```bash
cd 01-localhost-vs-production/develop
pip install -r requirements.txt
python app.py
```

Test:

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Hello"}'
```

Verification note: the production version in `01-localhost-vs-production/production` was run in a Python container and returned `200` for both `/health` and `/ask`.

### Exercise 1.3: Comparison table

| Feature | Develop | Production | Why Important? |
|---|---|---|---|
| Config | Hardcoded/default local values | Environment variables | Cloud platforms inject config at runtime |
| Secrets | May be in code or local shell | Stored in env/secrets manager | Prevents leaking API keys |
| Logging | Basic print/log output | Structured JSON logs | Easier debugging and monitoring |
| Health | Usually missing | `/health` and `/ready` | Required for restart and traffic routing |
| Security | No auth | API key/JWT | Prevents unauthorized use |
| State | In process memory | Redis/external store | Allows horizontal scaling |
| Shutdown | Ctrl+C only | SIGTERM/graceful shutdown | Safer deploys and restarts |

## Part 2: Docker

### Exercise 2.1: Dockerfile questions

1. Base image: `python:3.11-slim`, chosen because it is smaller than the full Python image.
2. Working directory: `/app`, where the application code runs.
3. Copying `requirements.txt` first improves Docker layer caching.
4. `pip install --no-cache-dir` avoids keeping package cache in the image.
5. `CMD` starts the FastAPI app through Uvicorn.

### Exercise 2.2: Build and run

```bash
cd 02-docker/develop
docker build -t day12-agent-basic .
docker run -p 8000:8000 day12-agent-basic
```

### Exercise 2.3: Image size comparison

Actual local Docker image sizes:

```text
day12-02-develop:     1.66GB
day12-02-production:  239MB
```

The production multi-stage image is much smaller because it uses `python:3.11-slim`, copies only runtime dependencies, and runs as a non-root user.

### Exercise 2.4: Docker Compose stack

Architecture:

```text
Client -> Nginx/load balancer -> Agent containers -> Redis
```

Redis stores shared state so any agent instance can serve the next request.

## Part 3: Cloud Deployment

### Exercise 3.1: Railway deployment

Target folder: `06-lab-complete`.

```bash
railway login
railway init
railway variables set ENVIRONMENT=production
railway variables set AGENT_API_KEY=<real-secret>
railway variables set JWT_SECRET=<real-secret>
railway variables set REDIS_URL=<redis-url>
railway up
railway domain
```

Public URL: https://ai-agent-production-djyv.onrender.com

Local verification: `03-cloud-deployment/railway` was run in a Python container and returned `200` for `/health` and `/ask`.

### Exercise 3.2: Render deployment

Render can use `06-lab-complete/render.yaml`. The blueprint defines a web service and Redis service, and injects `REDIS_URL` into the app.

Public Render verification:

```text
GET /health -> 200
GET /ready -> 200
POST /ask without API key -> 401
POST /ask with API key -> 200
Rate limit test -> 200 for the first 10 requests, then 429
```

### Exercise 3.3: GCP Cloud Run

Cloud Run packages the container image, deploys it as a managed service, and uses health checks plus environment variables for production configuration.

## Part 4: API Security

### Exercise 4.1: API Key authentication

The final app requires `X-API-Key` on protected endpoints. Missing or invalid keys return `401`.

Local verification for `04-api-gateway/develop`:

```text
POST /ask without X-API-Key -> 401
POST /ask with X-API-Key    -> 200
```

### Exercise 4.2: JWT authentication

The lab demonstrates JWT in `04-api-gateway/production/auth.py`. JWT is stateless because the token contains signed claims such as user id, role, issue time, and expiry.

Local verification for `04-api-gateway/production`:

```text
POST /auth/token with student/demo123 -> token returned
POST /ask with Bearer token           -> 200
```

### Exercise 4.3: Rate limiting

The final app implements Redis sliding-window rate limiting in `06-lab-complete/app/rate_limiter.py`. The default limit is `10` requests per minute.

### Exercise 4.4: Cost guard

The final app implements Redis-backed daily cost tracking in `06-lab-complete/app/cost_guard.py`. It estimates input/output tokens and blocks requests once the daily budget is exceeded.

## Part 5: Scaling & Reliability

### Exercise 5.1: Health checks

`GET /health` returns liveness information. `GET /ready` verifies the app is ready and Redis is reachable when `REQUIRE_REDIS=true`.

### Exercise 5.2: Graceful shutdown

The final app handles `SIGTERM` and uses Uvicorn graceful shutdown timeout, so cloud platforms can stop containers without abruptly killing in-flight work.

### Exercise 5.3: Stateless design

Conversation history, rate limit counters, and cost counters are stored in Redis. This allows multiple app instances to share state.

### Exercise 5.4: Load balancing

Run multiple app replicas behind Docker Compose and Nginx:

```bash
docker compose up --build --scale agent=3
```

### Exercise 5.5: Test stateless

Send requests with the same `session_id`, stop one instance, then continue sending requests. The history remains available because it is stored in Redis, not in process memory.

Local verification for `05-scaling-reliability/production`:

```text
docker compose up -d --scale agent=3
test_stateless.py saw 3 different instances
conversation history count: 10 messages
history preserved through Redis
```

## Part 6: Final Project

Final source code is in `06-lab-complete` and includes:

- Multi-stage Dockerfile
- Docker Compose stack with Redis
- API key authentication
- Redis rate limiting
- Redis cost guard
- Health and readiness checks
- Graceful shutdown
- Stateless conversation history
- Railway and Render config

Final verification for `06-lab-complete`:

```text
docker compose up -d --scale agent=3
Nginx healthy on localhost:8000
3 agent containers healthy
Redis healthy
Auth required: 401 without key
Auth success: 200 with key
Rate limit: 429 after limit
Failover: request succeeded after stopping one agent
check_production_ready.py: 20/20
Final image size: 247MB
```
