from datetime import datetime
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, text
from sqlalchemy.dialects.postgresql import JSONB, BIGINT
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class TemplateImportacao(Base):
    __tablename__ = "templates_importacao"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tenants.id"), nullable=False
    )
    departamento_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("departamentos.id"), nullable=False
    )
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    versao: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    json_schema: Mapped[dict] = mapped_column("schema_json", JSONB, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), nullable=False
    )


class Pipeline(Base):
    __tablename__ = "pipelines"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tenants.id"), nullable=False
    )
    departamento_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("departamentos.id"), nullable=False
    )
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    versao: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    config_yaml: Mapped[str] = mapped_column(Text, nullable=False)
    ativo: Mapped[bool] = mapped_column(default=True, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), nullable=False
    )


class LoteImportacao(Base):
    __tablename__ = "lotes_importacao"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tenants.id"), nullable=False
    )
    departamento_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("departamentos.id"), nullable=False
    )
    template_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("templates_importacao.id"), nullable=False
    )
    pipeline_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("pipelines.id"), nullable=False
    )
    usuario_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id"), nullable=False
    )
    nome_arquivo: Mapped[str] = mapped_column(String(500), nullable=False)
    hash_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    tamanho_bytes: Mapped[int | None] = mapped_column(BIGINT, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pendente", nullable=False)
    total_linhas: Mapped[int | None] = mapped_column(Integer, nullable=True)
    linhas_ok: Mapped[int | None] = mapped_column(Integer, default=0, nullable=True)
    linhas_erro: Mapped[int | None] = mapped_column(Integer, default=0, nullable=True)
    erro_mensagem: Mapped[str | None] = mapped_column(Text, nullable=True)
    storage_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    iniciado_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    concluido_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), nullable=False
    )


class LinhagemDados(Base):
    __tablename__ = "linhagem_dados"

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tenants.id"), nullable=False
    )
    transacao_id: Mapped[int] = mapped_column(BIGINT, nullable=False)
    lote_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("lotes_importacao.id"), nullable=False
    )
    pipeline_step: Mapped[str] = mapped_column(String(100), nullable=False)
    linha_arquivo: Mapped[int | None] = mapped_column(Integer, nullable=True)
    dados_originais: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), nullable=False
    )
