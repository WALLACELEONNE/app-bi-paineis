import datetime
from pydantic import Field
from app.schemas.tenant import BaseSchema


class TransacaoRead(BaseSchema):
    id: int
    tenant_id: int
    departamento_id: int
    lote_importacao_id: int
    data_competencia: datetime.date
    data_lancamento: datetime.date | None = None
    plano_contas_id: int | None = None
    centro_custo_id: int | None = None
    produto_id: int | None = None
    cliente_fornecedor_id: int | None = None
    fazenda_id: int | None = None
    armazem_id: int | None = None
    safra_id: int | None = None
    valor: float | None = None
    quantidade: float | None = None
    unidade: str | None = None
    atributos_extra: dict | None = None
    criado_em: datetime.datetime


class TransacaoCreate(BaseSchema):
    departamento_id: int
    lote_importacao_id: int
    data_competencia: datetime.date
    data_lancamento: datetime.date | None = None
    plano_contas_id: int | None = None
    centro_custo_id: int | None = None
    produto_id: int | None = None
    cliente_fornecedor_id: int | None = None
    fazenda_id: int | None = None
    armazem_id: int | None = None
    safra_id: int | None = None
    valor: float | None = None
    quantidade: float | None = None
    unidade: str | None = None
    atributos_extra: dict | None = None


class TransacaoListParams(BaseSchema):
    data_inicio: datetime.date | None = None
    data_fim: datetime.date | None = None
    departamento_id: int | None = None
    centro_custo_id: int | None = None
    produto_id: int | None = None
    fazenda_id: int | None = None
    safra_id: int | None = None
    plano_contas_id: int | None = None
    limit: int = Field(default=1000, ge=1, le=100000)
    offset: int = Field(default=0, ge=0)
