from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class Dashboard(Base):
    __tablename__ = "dashboards"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tenants.id"), nullable=False
    )
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(50), nullable=False)
    departamento_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("departamentos.id"), nullable=True
    )
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Widget(Base):
    __tablename__ = "widgets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    dashboard_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("dashboards.id", ondelete="CASCADE"), nullable=False
    )
    usuario_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id"), nullable=False
    )
    tipo: Mapped[str] = mapped_column(String(50), nullable=False)
    titulo: Mapped[str | None] = mapped_column(String(200), nullable=True)
    config: Mapped[dict] = mapped_column(JSONB, nullable=False)
    posicao_x: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    posicao_y: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    largura: Mapped[int] = mapped_column(Integer, default=4, nullable=False)
    altura: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), nullable=False
    )
    atualizado_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class ExportacaoAgendada(Base):
    __tablename__ = "exportacoes_agendadas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tenants.id"), nullable=False
    )
    usuario_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id"), nullable=False
    )
    dashboard_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("dashboards.id"), nullable=False
    )
    formato: Mapped[str] = mapped_column(String(10), default="pdf", nullable=False)
    cron_expression: Mapped[str] = mapped_column(String(50), nullable=False)
    destinatarios: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    ultima_execucao: Mapped[datetime | None] = mapped_column(nullable=True)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), nullable=False
    )
