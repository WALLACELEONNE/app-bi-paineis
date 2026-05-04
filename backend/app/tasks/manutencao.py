from app.tasks.celery_app import celery_app
from app.services.partition_service import garantir_particoes
import asyncio
import structlog

logger = structlog.get_logger()


@celery_app.task(name="manutencao_criar_particoes")
def manutencao_criar_particoes():
    logger.info("manutencao_criar_particoes_iniciada")
    asyncio.get_event_loop().run_until_complete(garantir_particoes())
    return {"status": "concluido"}
