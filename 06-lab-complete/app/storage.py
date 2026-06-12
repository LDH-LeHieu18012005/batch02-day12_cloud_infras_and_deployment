"""Redis-backed storage for stateless deployments."""
import json
from datetime import datetime, timezone

import redis
from fastapi import HTTPException

from app.config import settings


class RedisStorage:
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.client = redis.from_url(redis_url, decode_responses=True) if redis_url else None

    def ping(self) -> bool:
        if not self.client:
            return False
        try:
            return bool(self.client.ping())
        except redis.RedisError:
            return False

    def require(self):
        if not self.client:
            raise HTTPException(status_code=503, detail="REDIS_URL is required")
        return self.client

    def append_message(self, session_id: str, role: str, content: str):
        client = self.require()
        key = f"session:{session_id}:history"
        payload = json.dumps(
            {
                "role": role,
                "content": content,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
        pipe = client.pipeline()
        pipe.rpush(key, payload)
        pipe.ltrim(key, -settings.max_history_messages, -1)
        pipe.expire(key, settings.session_ttl_seconds)
        pipe.execute()

    def get_history(self, session_id: str) -> list[dict]:
        client = self.require()
        items = client.lrange(f"session:{session_id}:history", 0, -1)
        return [json.loads(item) for item in items]

    def delete_session(self, session_id: str):
        client = self.require()
        client.delete(f"session:{session_id}:history")

    def status(self) -> dict:
        return {
            "type": "redis",
            "configured": bool(self.client),
            "connected": self.ping(),
        }


storage = RedisStorage(settings.redis_url)
