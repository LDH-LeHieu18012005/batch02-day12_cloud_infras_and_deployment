# Deployment Information

## Public URL

```text
https://ai-agent-production-djyv.onrender.com
```

## Platform

Render Blueprint with a Render Key Value Redis-compatible service.

## Required Environment Variables

- `PORT`
- `ENVIRONMENT=production`
- `REDIS_URL`
- `AGENT_API_KEY`
- `JWT_SECRET`
- `RATE_LIMIT_PER_MINUTE=10`
- `DAILY_BUDGET_USD=10.0`
- `OPENAI_API_KEY` optional because the project uses a mock LLM by default

## Test Commands

Use:

```bash
URL=https://ai-agent-production-djyv.onrender.com
KEY=<AGENT_API_KEY from Render Environment>
```

### Health Check

```bash
curl $URL/health
```

Expected: response includes `"status":"ok"`.

### Readiness Check

```bash
curl $URL/ready
```

Expected: response includes `"ready":true`.

### Authentication Required

```bash
curl -X POST $URL/ask \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","question":"Hello"}'
```

Expected: `401 Unauthorized`.

### API Test With Authentication

```bash
curl -X POST $URL/ask \
  -H "X-API-Key: $KEY" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test","question":"What is deployment?"}'
```

Expected: `200 OK` with an answer and `session_id`.

### Rate Limiting

```bash
for i in {1..15}; do
  curl -s -o /dev/null -w "%{http_code}\n" \
    -X POST $URL/ask \
    -H "X-API-Key: $KEY" \
    -H "Content-Type: application/json" \
    -d '{"user_id":"test","question":"rate limit"}'
done
```

Expected: requests eventually return `429`.

## Screenshots

Deployment evidence:

- `screenshots/dashboard.png`
- `screenshots/running.png`
- `screenshots/test.png`

## Verified Results

Public deployment was tested on 2026-06-12:

- `GET /health` -> `200 OK`
- `GET /ready` -> `200 OK`
- `POST /ask` without `X-API-Key` -> `401 Unauthorized`
- `POST /ask` with `X-API-Key` -> `200 OK`
- Rate limit test -> first 10 authenticated requests returned `200`, then requests returned `429`
