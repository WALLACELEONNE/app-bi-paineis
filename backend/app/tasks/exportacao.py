from app.tasks.celery_app import celery_app
import structlog

logger = structlog.get_logger()


@celery_app.task(bind=True, name="gerar_relatorio_agendado")
def gerar_relatorio_agendado(self, exportacao_id: int, tenant_id: int):
    logger.info("exportacao_iniciada", exportacao_id=exportacao_id, tenant_id=tenant_id)
    return {"status": "concluido", "exportacao_id": exportacao_id}
