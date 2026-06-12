# Deployment Information

## Public URL

Fill this in after deploying with your own Railway or Render account:

```text
https://your-agent-url.example
```

## Platform

Recommended: Render Blueprint or Railway.

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

Replace `$URL` and `$KEY` with the real deployment values.

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

Place real deployment screenshots here after deployment:

- `screenshots/dashboard.png`
- `screenshots/running.png`
- `screenshots/test.png`
