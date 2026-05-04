import asyncio
import structlog
from celery import shared_task
from app.tasks.celery_app import celery_app

logger = structlog.get_logger()


@celery_app.task(
    bind=True,
    name="processar_importacao",
    max_retries=3,
    default_retry_delay=60,
)
def processar_importacao(self, lote_id: int, tenant_id: int):
    logger.info("importacao_iniciada", lote_id=lote_id, tenant_id=tenant_id)
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(_async_process(lote_id, tenant_id))


async def _async_process(lote_id: int, tenant_id: int):
    from app.core.database import AsyncSessionLocal
    from app.models import LoteImportacao
    from app.services.import_service import processar_lote

    async with AsyncSessionLocal() as session:
        lote = await session.get(LoteImportacao, lote_id)
        if not lote:
            logger.error("lote_nao_encontrado", lote_id=lote_id)
            return {"status": "erro", "detail": "Lote não encontrado"}

    return await processar_lote(lote)
