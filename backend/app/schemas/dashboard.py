import datetime
from pydantic import Field
from app.schemas.tenant import BaseSchema


class DashboardRead(BaseSchema):
    id: int
    tenant_id: int
    nome: str
    slug: str
    departamento_id: int | None = None
    ativo: bool


class DashboardCreate(BaseSchema):
    tenant_id: int
    nome: str
    slug: str
    departamento_id: int | None = None
    ativo: bool = True


class DashboardUpdate(BaseSchema):
    nome: str | None = None
    ativo: bool | None = None


class WidgetRead(BaseSchema):
    id: int
    dashboard_id: int
    usuario_id: int
    tipo: str
    titulo: str | None = None
    config: dict
    posicao_x: int
    posicao_y: int
    largura: int
    altura: int
    criado_em: datetime.datetime
    atualizado_em: datetime.datetime | None = None


class WidgetCreate(BaseSchema):
    dashboard_id: int
    usuario_id: int
    tipo: str = Field(
        description="bar_chart, line_chart, pie_chart, kpi_card, data_table, heatmap"
    )
    titulo: str | None = None
    config: dict
    posicao_x: int = 0
    posicao_y: int = 0
    largura: int = 4
    altura: int = 3


class WidgetUpdate(BaseSchema):
    titulo: str | None = None
    config: dict | None = None
    posicao_x: int | None = None
    posicao_y: int | None = None
    largura: int | None = None
    altura: int | None = None


class ExportacaoAgendadaRead(BaseSchema):
    id: int
    tenant_id: int
    usuario_id: int
    dashboard_id: int
    formato: str
    cron_expression: str
    destinatarios: dict | None = None
    ativo: bool
    ultima_execucao: datetime.datetime | None = None
    criado_em: datetime.datetime


class ExportacaoAgendadaCreate(BaseSchema):
    tenant_id: int
    usuario_id: int
    dashboard_id: int
    formato: str = "pdf"
    cron_expression: str
    destinatarios: dict | None = None
    ativo: bool = True


class ExportacaoAgendadaUpdate(BaseSchema):
    formato: str | None = None
    cron_expression: str | None = None
    destinatarios: dict | None = None
    ativo: bool | None = None
