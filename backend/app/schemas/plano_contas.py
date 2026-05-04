from datetime import datetime
from app.schemas.tenant import BaseSchema


class PlanoContasRead(BaseSchema):
    id: int
    tenant_id: int
    codigo_reduzido: str
    codigo_estruturado: str | None = None
    descricao: str
    nivel: int
    natureza: str | None = None
    grupo: str | None = None
    ativo: bool
    criado_em: datetime


class PlanoContasCreate(BaseSchema):
    tenant_id: int
    codigo_reduzido: str
    codigo_estruturado: str | None = None
    descricao: str
    nivel: int
    natureza: str | None = None
    grupo: str | None = None
    ativo: bool = True


class PlanoContasUpdate(BaseSchema):
    descricao: str | None = None
    natureza: str | None = None
    grupo: str | None = None
    ativo: bool | None = None


class CentroCustoRead(BaseSchema):
    id: int
    tenant_id: int
    codigo: str
    descricao: str
    ativo: bool
    criado_em: datetime


class CentroCustoCreate(BaseSchema):
    tenant_id: int
    codigo: str
    descricao: str
    ativo: bool = True


class CentroCustoUpdate(BaseSchema):
    descricao: str | None = None
    ativo: bool | None = None
