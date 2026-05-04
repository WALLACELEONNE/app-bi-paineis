from datetime import datetime
from pydantic import Field
from app.schemas.tenant import BaseSchema


class ProdutoRead(BaseSchema):
    id: int
    tenant_id: int
    codigo: str
    nome: str
    tipo: str
    unidade: str
    cultura: str | None = None
    ativo: bool
    criado_em: datetime


class ProdutoCreate(BaseSchema):
    tenant_id: int
    codigo: str
    nome: str
    tipo: str = Field(description="grao, insumo ou servico")
    unidade: str = Field(description="sc, ton, kg, lt")
    cultura: str | None = None
    ativo: bool = True


class ProdutoUpdate(BaseSchema):
    nome: str | None = None
    tipo: str | None = None
    unidade: str | None = None
    cultura: str | None = None
    ativo: bool | None = None


class ClienteFornecedorRead(BaseSchema):
    id: int
    tenant_id: int
    tipo: str
    razao_social: str
    cnpj_cpf: str | None = None
    ie: str | None = None
    ativo: bool
    criado_em: datetime


class ClienteFornecedorCreate(BaseSchema):
    tenant_id: int
    tipo: str = Field(
        pattern=r"^[CFA]$", description="C=cliente, F=fornecedor, A=ambos"
    )
    razao_social: str
    cnpj_cpf: str | None = None
    ie: str | None = None
    ativo: bool = True


class ClienteFornecedorUpdate(BaseSchema):
    razao_social: str | None = None
    tipo: str | None = None
    cnpj_cpf: str | None = None
    ie: str | None = None
    ativo: bool | None = None


class FazendaRead(BaseSchema):
    id: int
    tenant_id: int
    codigo: str
    nome: str
    area_total: float | None = None
    municipio: str | None = None
    uf: str | None = None
    ativo: bool
    criado_em: datetime


class FazendaCreate(BaseSchema):
    tenant_id: int
    codigo: str
    nome: str
    area_total: float | None = None
    municipio: str | None = None
    uf: str | None = None
    ativo: bool = True


class FazendaUpdate(BaseSchema):
    nome: str | None = None
    area_total: float | None = None
    municipio: str | None = None
    uf: str | None = None
    ativo: bool | None = None


class ArmazemRead(BaseSchema):
    id: int
    tenant_id: int
    codigo: str
    nome: str
    capacidade: float | None = None
    unidade: str | None = None
    ativo: bool
    criado_em: datetime


class ArmazemCreate(BaseSchema):
    tenant_id: int
    codigo: str
    nome: str
    capacidade: float | None = None
    unidade: str | None = None
    ativo: bool = True


class ArmazemUpdate(BaseSchema):
    nome: str | None = None
    capacidade: float | None = None
    unidade: str | None = None
    ativo: bool | None = None


class SafraRead(BaseSchema):
    id: int
    tenant_id: int
    codigo: str
    ano_inicio: int
    ano_fim: int
    ativo: bool
    criado_em: datetime


class SafraCreate(BaseSchema):
    tenant_id: int
    codigo: str
    ano_inicio: int
    ano_fim: int
    ativo: bool = True


class SafraUpdate(BaseSchema):
    codigo: str | None = None
    ano_inicio: int | None = None
    ano_fim: int | None = None
    ativo: bool | None = None
