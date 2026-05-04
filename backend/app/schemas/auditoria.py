import datetime
from app.schemas.tenant import BaseSchema


class AuditLogRead(BaseSchema):
    id: int
    tenant_id: int
    usuario_id: int | None = None
    acao: str
    entidade: str | None = None
    entidade_id: int | None = None
    detalhes: dict | None = None
    ip: str | None = None
    criado_em: datetime.datetime
