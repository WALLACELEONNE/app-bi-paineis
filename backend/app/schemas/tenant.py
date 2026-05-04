from pydantic import BaseModel, ConfigDict
from datetime import datetime


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class TimestampSchema(BaseSchema):
    criado_em: datetime
    atualizado_em: datetime | None = None


class TenantRead(BaseSchema):
    id: int
    nome: str
    slug: str
    ativo: bool
    criado_em: datetime


class TenantCreate(BaseSchema):
    nome: str
    slug: str
    ativo: bool = True


class TenantUpdate(BaseSchema):
    nome: str | None = None
    ativo: bool | None = None


class DepartamentoRead(BaseSchema):
    id: int
    tenant_id: int
    nome: str
    slug: str
    ativo: bool
    criado_em: datetime


class DepartamentoCreate(BaseSchema):
    tenant_id: int
    nome: str
    slug: str
    ativo: bool = True


class DepartamentoUpdate(BaseSchema):
    nome: str | None = None
    ativo: bool | None = None
