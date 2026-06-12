"""Redis sliding-window rate limiter."""
import time

from fastapi import HTTPException
from redis import RedisError

from app.config import settings
from app.storage import storage


class RedisRateLimiter:
    def __init__(self, max_requests: int, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    def check(self, identity: str) -> dict:
        client = storage.require()
        now = time.time()
        key = f"rate:{identity}"
        try:
            pipe = client.pipeline()
            pipe.zremrangebyscore(key, 0, now - self.window_seconds)
            pipe.zcard(key)
            _, current = pipe.execute()

            if current >= self.max_requests:
                oldest_items = client.zrange(key, 0, 0, withscores=True)
                retry_after = self.window_seconds
                if oldest_items:
                    retry_after = max(1, int(oldest_items[0][1] + self.window_seconds - now))
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded",
                    headers={
                        "Retry-After": str(retry_after),
                        "X-RateLimit-Limit": str(self.max_requests),
                        "X-RateLimit-Remaining": "0",
                    },
                )

            member = f"{now}:{identity}"
            pipe = client.pipeline()
            pipe.zadd(key, {member: now})
            pipe.expire(key, self.window_seconds)
            pipe.execute()
            return {
                "limit": self.max_requests,
                "remaining": self.max_requests - current - 1,
                "window_seconds": self.window_seconds,
            }
        except RedisError as exc:
            raise HTTPException(status_code=503, detail="Rate limiter unavailable") from exc


rate_limiter = RedisRateLimiter(settings.rate_limit_per_minute)
