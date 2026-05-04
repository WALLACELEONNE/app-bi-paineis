import datetime
from app.schemas.tenant import BaseSchema


class TemplateImportacaoRead(BaseSchema):
    id: int
    tenant_id: int
    departamento_id: int
    nome: str
    versao: int
    json_schema: dict
    criado_em: datetime.datetime


class TemplateImportacaoCreate(BaseSchema):
    tenant_id: int
    departamento_id: int
    nome: str
    json_schema: dict


class TemplateImportacaoUpdate(BaseSchema):
    nome: str | None = None
    json_schema: dict | None = None


class PipelineRead(BaseSchema):
    id: int
    tenant_id: int
    departamento_id: int
    nome: str
    versao: int
    config_yaml: str
    ativo: bool
    criado_em: datetime.datetime


class PipelineCreate(BaseSchema):
    tenant_id: int
    departamento_id: int
    nome: str
    config_yaml: str


class PipelineUpdate(BaseSchema):
    nome: str | None = None
    config_yaml: str | None = None
    ativo: bool | None = None


class LoteImportacaoRead(BaseSchema):
    id: int
    tenant_id: int
    departamento_id: int
    template_id: int
    pipeline_id: int
    usuario_id: int
    nome_arquivo: str
    hash_sha256: str
    tamanho_bytes: int | None = None
    status: str
    total_linhas: int | None = None
    linhas_ok: int | None = None
    linhas_erro: int | None = None
    erro_mensagem: str | None = None
    storage_path: str | None = None
    iniciado_em: datetime.datetime | None = None
    concluido_em: datetime.datetime | None = None
    criado_em: datetime.datetime


class LinhagemDadosRead(BaseSchema):
    id: int
    tenant_id: int
    transacao_id: int
    lote_id: int
    pipeline_step: str
    linha_arquivo: int | None = None
    dados_originais: dict | None = None
    criado_em: datetime.datetime
