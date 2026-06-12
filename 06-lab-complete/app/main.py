"""Production-ready AI agent for Day 12 final lab."""
import json
import logging
import os
import signal
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.auth import verify_api_key
from app.config import settings
from app.cost_guard import cost_guard
from app.rate_limiter import rate_limiter
from app.storage import storage
from utils.mock_llm import ask as llm_ask


logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format='{"ts":"%(asctime)s","level":"%(levelname)s","message":"%(message)s"}',
)
logger = logging.getLogger(__name__)

START_TIME = time.time()
INSTANCE_ID = os.getenv("INSTANCE_ID", f"agent-{uuid.uuid4().hex[:8]}")
_is_ready = False
_request_count = 0
_error_count = 0


def log_event(event: str, **fields):
    logger.info(json.dumps({"event": event, **fields}))


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _is_ready
    log_event(
        "startup",
        app=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
        instance_id=INSTANCE_ID,
        redis_configured=bool(settings.redis_url),
    )
    _is_ready = True
    yield
    _is_ready = False
    log_event("shutdown", instance_id=INSTANCE_ID)


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs" if settings.environment != "production" else None,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-API-Key"],
)


@app.middleware("http")
async def request_middleware(request: Request, call_next):
    global _request_count, _error_count
    start = time.time()
    _request_count += 1
    try:
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Instance-ID"] = INSTANCE_ID
        duration_ms = round((time.time() - start) * 1000, 1)
        log_event(
            "request",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration_ms=duration_ms,
        )
        return response
    except Exception:
        _error_count += 1
        raise


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    user_id: str = Field(default="anonymous", min_length=1, max_length=128)
    session_id: str | None = Field(default=None, max_length=128)


class AskResponse(BaseModel):
    user_id: str
    session_id: str
    question: str
    answer: str
    model: str
    served_by: str
    timestamp: str


@app.get("/", tags=["Info"])
def root():
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "instance_id": INSTANCE_ID,
        "endpoints": {
            "ask": "POST /ask (requires X-API-Key)",
            "health": "GET /health",
            "ready": "GET /ready",
            "metrics": "GET /metrics (requires X-API-Key)",
        },
    }


@app.post("/ask", response_model=AskResponse, tags=["Agent"])
async def ask_agent(
    body: AskRequest,
    request: Request,
    api_key: str = Depends(verify_api_key),
):
    session_id = body.session_id or f"{body.user_id}:{uuid.uuid4().hex}"
    rate_identity = f"{api_key[:12]}:{body.user_id}"

    rate_limiter.check(rate_identity)
    cost_guard.check_budget(body.user_id)

    input_tokens = estimate_tokens(body.question)
    storage.append_message(session_id, "user", body.question)

    log_event(
        "agent_call",
        user_id=body.user_id,
        session_id=session_id,
        question_length=len(body.question),
        client=str(request.client.host) if request.client else "unknown",
    )

    answer = llm_ask(body.question)
    output_tokens = estimate_tokens(answer)

    storage.append_message(session_id, "assistant", answer)
    cost_guard.record_usage(body.user_id, input_tokens, output_tokens)

    return AskResponse(
        user_id=body.user_id,
        session_id=session_id,
        question=body.question,
        answer=answer,
        model=settings.llm_model,
        served_by=INSTANCE_ID,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@app.get("/chat/{session_id}/history", tags=["Agent"])
def get_history(session_id: str, _api_key: str = Depends(verify_api_key)):
    history = storage.get_history(session_id)
    if not history:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"session_id": session_id, "messages": history, "count": len(history)}


@app.delete("/chat/{session_id}", tags=["Agent"])
def delete_history(session_id: str, _api_key: str = Depends(verify_api_key)):
    storage.delete_session(session_id)
    return {"deleted": session_id}


@app.get("/health", tags=["Operations"])
def health():
    redis_ok = storage.ping()
    return {
        "status": "ok",
        "version": settings.app_version,
        "environment": settings.environment,
        "instance_id": INSTANCE_ID,
        "uptime_seconds": round(time.time() - START_TIME, 1),
        "total_requests": _request_count,
        "checks": {
            "llm": "mock" if not settings.openai_api_key else "openai",
            "redis": "ok" if redis_ok else "unavailable",
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/ready", tags=["Operations"])
def ready():
    if not _is_ready:
        raise HTTPException(status_code=503, detail="Application is not ready")
    if settings.require_redis and not storage.ping():
        raise HTTPException(status_code=503, detail="Redis is not ready")
    return {"ready": True, "instance_id": INSTANCE_ID}


@app.get("/metrics", tags=["Operations"])
def metrics(_api_key: str = Depends(verify_api_key)):
    return {
        "uptime_seconds": round(time.time() - START_TIME, 1),
        "total_requests": _request_count,
        "error_count": _error_count,
        "storage": storage.status(),
        "rate_limit_per_minute": settings.rate_limit_per_minute,
        "daily_budget_usd": settings.daily_budget_usd,
    }


def estimate_tokens(text: str) -> int:
    return max(1, len(text.split()) * 2)


def _handle_signal(signum, _frame):
    log_event("signal_received", signum=signum, instance_id=INSTANCE_ID)


signal.signal(signal.SIGTERM, _handle_signal)
if hasattr(signal, "SIGINT"):
    signal.signal(signal.SIGINT, _handle_signal)


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        timeout_graceful_shutdown=30,
    )
