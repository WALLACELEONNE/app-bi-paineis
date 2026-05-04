from sqlalchemy.ext.asyncio import AsyncSession
from app.models import AuditLog
from app.core.database import AsyncSessionLocal
import structlog

logger = structlog.get_logger()


async def registrar_auditoria(
    tenant_id: int,
    acao: str,
    entidade: str | None = None,
    entidade_id: int | None = None,
    usuario_id: int | None = None,
    detalhes: dict | None = None,
    ip: str | None = None,
):
    try:
        async with AsyncSessionLocal() as session:
            session.add(
                AuditLog(
                    tenant_id=tenant_id,
                    usuario_id=usuario_id,
                    acao=acao,
                    entidade=entidade,
                    entidade_id=entidade_id,
                    detalhes=detalhes,
                    ip=ip,
                )
            )
            await session.commit()
    except Exception as e:
        logger.error("auditoria_falhou", acao=acao, error=str(e))
