from fastapi import Request
from fastapi.responses import JSONResponse
from jose import JWTError
from app.core.security import decode_token
from app.core.config import settings
import redis.asyncio as aioredis
import structlog

logger = structlog.get_logger()
_redis_rate: aioredis.Redis | None = None

RATE_LIMITS = {
    "default": {"max": 100, "window": 60},
    "upload": {"max": 10, "window": 60},
    "upload_get": {"max": 30, "window": 60},
}


async def _get_redis_rate() -> aioredis.Redis:
    global _redis_rate
    if _redis_rate is None:
        _redis_rate = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis_rate


class RateLimitMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        request = Request(scope)
        try:
            path = request.url.path
            if "/upload" in path and request.method == "GET":
                limit_cfg = RATE_LIMITS["upload_get"]
            elif "/upload" in path:
                limit_cfg = RATE_LIMITS["upload"]
            else:
                limit_cfg = RATE_LIMITS["default"]

            tenant_id = "anon"
            auth = request.headers.get("authorization", "")
            if auth.startswith("Bearer "):
                try:
                    payload = decode_token(auth[7:])
                    tenant_id = str(payload.get("tenant_id", "anon"))
                except (JWTError, KeyError):
                    pass

            redis = await _get_redis_rate()
            key = f"rl:{tenant_id}:{limit_cfg['window']}"
            count = await redis.incr(key)
            if count == 1:
                await redis.expire(key, limit_cfg["window"])
            if count > limit_cfg["max"]:
                response = JSONResponse(
                    status_code=429, content={"detail": "Muitas requisições. Aguarde."}
                )
                await response(scope, receive, send)
                return
        except Exception as e:
            logger.warning("rate_limit_skip", error=str(e))

        await self.app(scope, receive, send)
