"""Redis-backed LLM cost guard."""
import time

from fastapi import HTTPException
from redis import RedisError

from app.config import settings
from app.storage import storage


PRICE_PER_1K_INPUT_TOKENS = 0.00015
PRICE_PER_1K_OUTPUT_TOKENS = 0.0006


class RedisCostGuard:
    def __init__(self, daily_budget_usd: float):
        self.daily_budget_usd = daily_budget_usd

    def _key(self, user_id: str) -> str:
        today = time.strftime("%Y-%m-%d")
        return f"cost:{today}:{user_id}"

    def check_budget(self, user_id: str):
        client = storage.require()
        try:
            current = float(client.hget(self._key(user_id), "cost_usd") or 0)
        except RedisError as exc:
            raise HTTPException(status_code=503, detail="Cost guard unavailable") from exc

        if current >= self.daily_budget_usd:
            raise HTTPException(
                status_code=402,
                detail={
                    "error": "Daily budget exceeded",
                    "used_usd": round(current, 6),
                    "budget_usd": self.daily_budget_usd,
                },
            )

    def record_usage(self, user_id: str, input_tokens: int, output_tokens: int) -> dict:
        client = storage.require()
        cost = (
            input_tokens / 1000 * PRICE_PER_1K_INPUT_TOKENS
            + output_tokens / 1000 * PRICE_PER_1K_OUTPUT_TOKENS
        )
        key = self._key(user_id)
        try:
            pipe = client.pipeline()
            pipe.hincrby(key, "input_tokens", input_tokens)
            pipe.hincrby(key, "output_tokens", output_tokens)
            pipe.hincrby(key, "request_count", 1)
            pipe.hincrbyfloat(key, "cost_usd", cost)
            pipe.expire(key, 60 * 60 * 48)
            pipe.execute()
            usage = client.hgetall(key)
        except RedisError as exc:
            raise HTTPException(status_code=503, detail="Cost guard unavailable") from exc

        return {
            "user_id": user_id,
            "input_tokens": int(usage.get("input_tokens", 0)),
            "output_tokens": int(usage.get("output_tokens", 0)),
            "request_count": int(usage.get("request_count", 0)),
            "cost_usd": round(float(usage.get("cost_usd", 0)), 6),
            "budget_usd": self.daily_budget_usd,
        }


cost_guard = RedisCostGuard(settings.daily_budget_usd)
