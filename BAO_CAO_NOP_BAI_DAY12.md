# Bao Cao Nop Bai Day 12 - Cloud Infrastructure and Deployment

## Thong Tin Sinh Vien

- Ho va ten: Lê Dương Hiếu
- Ma sinh vien: 2A202600635
- Ngay nop: 12/06/2026
- Repository: https://github.com/LDH-LeHieu18012005/batch02-day12_cloud_infras_and_deployment
- Public URL: https://ai-agent-production-djyv.onrender.com

## 1. Mission Answers

File tra loi bai tap:

- `MISSION_ANSWERS.md`

Noi dung da hoan thanh:

- Part 1: Phan tich su khac nhau giua localhost va production.
- Part 2: Docker, Dockerfile, image size comparison, Docker Compose.
- Part 3: Cloud deployment voi public URL tren Render.
- Part 4: API security gom API key, JWT, rate limiting, cost guard.
- Part 5: Scaling va reliability gom health check, readiness, graceful shutdown, stateless Redis, load balancing.
- Part 6: Final production-ready AI agent.

## 2. Source Code Final

Source code production chinh nam trong:

- `06-lab-complete`

Thanh phan chinh:

- `app/main.py`: FastAPI application va API routes.
- `app/config.py`: cau hinh bang environment variables.
- `app/auth.py`: API key authentication.
- `app/rate_limiter.py`: Redis-backed rate limiting.
- `app/cost_guard.py`: daily cost protection.
- `app/storage.py`: Redis-backed conversation history.
- `Dockerfile`: multi-stage production Docker image.
- `docker-compose.yml`: stack gom Nginx, Agent replicas va Redis.
- `render.yaml`: Render deployment blueprint.

## 3. Deployment

File thong tin deployment:

- `DEPLOYMENT.md`

Nen tang deploy:

- Render Blueprint
- Web service: `ai-agent-production`
- Redis/Key Value service: dung cho shared state, rate limit va history

Public endpoints:

- Base URL: https://ai-agent-production-djyv.onrender.com
- Health: https://ai-agent-production-djyv.onrender.com/health
- Readiness: https://ai-agent-production-djyv.onrender.com/ready

## 4. Ket Qua Kiem Thu Public URL

Da kiem thu public deployment ngay 12/06/2026:

```text
GET /health -> 200 OK
GET /ready -> 200 OK
POST /ask without X-API-Key -> 401 Unauthorized
POST /ask with X-API-Key -> 200 OK
Rate limit test -> 10 request dau tra ve 200, cac request tiep theo tra ve 429
```

## 5. Screenshots

Thu muc anh bang chung:

- `screenshots/dashboard.png`: Render dashboard/service deploy live.
- `screenshots/running.png`: Public service dang chay.
- `screenshots/test.png`: Ket qua test public endpoint.
- `screenshots/test-evidence.md`: Log test dang text.

## 6. Checklist Truoc Khi Nop

- [x] Repository co source code day du.
- [x] `MISSION_ANSWERS.md` da tra loi cac phan bai lab.
- [x] `DEPLOYMENT.md` co public URL that.
- [x] Public URL truy cap duoc.
- [x] Health check va readiness check thanh cong.
- [x] API key authentication hoat dong.
- [x] Rate limiting hoat dong.
- [x] Stateless design su dung Redis.
- [x] Multi-stage Dockerfile va image production nho hon 500MB.
- [x] Khong commit file `.env`.
- [x] Co screenshots bang chung trong thu muc `screenshots`.

## 7. Link Nop Bai

```text
https://github.com/LDH-LeHieu18012005/batch02-day12_cloud_infras_and_deployment
```
