import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from app.core.config import settings
from app.api.v1.router import api_router
from app.core.middleware import RateLimitMiddleware
from app.core.audit_middleware import AuditMiddleware

structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.dev.ConsoleRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.add_middleware(RateLimitMiddleware)
app.add_middleware(AuditMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

Instrumentator().instrument(app).expose(
    app, endpoint="/metrics", include_in_schema=False
)


@app.get("/health/live")
async def liveness():
    return {"status": "ok"}


@app.get("/health/ready")
async def readiness():
    status = {"status": "ready", "version": settings.VERSION, "checks": {}}
    try:
        from app.core.database import AsyncSessionLocal
        from sqlalchemy import text

        async with AsyncSessionLocal() as s:
            await s.execute(text("SELECT 1"))
        status["checks"]["database"] = "ok"
    except Exception as e:
        status["checks"]["database"] = f"error: {e}"
        status["status"] = "degraded"
    try:
        import redis.asyncio as aioredis

        r = aioredis.from_url(settings.REDIS_URL)
        await r.ping()
        await r.aclose()
        status["checks"]["redis"] = "ok"
    except Exception as e:
        status["checks"]["redis"] = f"error: {e}"
        status["status"] = "degraded"
    try:
        from app.services.minio_service import get_minio

        get_minio()
        status["checks"]["minio"] = "ok"
    except Exception as e:
        status["checks"]["minio"] = f"error: {e}"
        status["status"] = "degraded"
    return status


@app.on_event("startup")
async def startup():
    logger.info("startup_begin", environment=settings.ENVIRONMENT)
    from app.tasks.celery_app import celery_app

    await _setup_rls()
    logger.info("startup_complete")


@app.on_event("shutdown")
async def shutdown():
    logger.info("shutdown")


async def _setup_rls():
    from app.core.database import AsyncSessionLocal
    from sqlalchemy import text

    try:
        async with AsyncSessionLocal() as session:
            await session.execute(
                text("ALTER TABLE transacoes ENABLE ROW LEVEL SECURITY")
            )
            await session.execute(
                text("""
                DROP POLICY IF EXISTS tenant_isolation ON transacoes
            """)
            )
            await session.execute(
                text("""
                CREATE POLICY tenant_isolation ON transacoes
                    USING (tenant_id = COALESCE(NULLIF(current_setting('app.current_tenant_id', true), ''), '0')::int)
            """)
            )
            await session.commit()
    except Exception as e:
        logger.warning("rls_setup_skipped", error=str(e))
