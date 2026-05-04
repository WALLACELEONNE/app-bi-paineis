from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tenants.id"), nullable=False
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    role: Mapped[str] = mapped_column(
        String(20), default="visualizador", nullable=False
    )
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    ultimo_login: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), nullable=False
    )


class PermissaoDepartamento(Base):
    __tablename__ = "permissoes_departamento"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id"), nullable=False
    )
    departamento_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("departamentos.id"), nullable=False
    )
    pode_importar: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    pode_visualizar: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    pode_exportar: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
