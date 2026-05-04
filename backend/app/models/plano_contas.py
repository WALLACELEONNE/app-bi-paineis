from sqlalchemy import String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin


class PlanoContas(Base, TimestampMixin):
    __tablename__ = "plano_contas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    codigo_reduzido: Mapped[str] = mapped_column(String(20), nullable=False)
    codigo_estruturado: Mapped[str | None] = mapped_column(String(50), nullable=True)
    descricao: Mapped[str] = mapped_column(String(300), nullable=False)
    nivel: Mapped[int] = mapped_column(Integer, nullable=False)
    natureza: Mapped[str | None] = mapped_column(String(10), nullable=True)
    grupo: Mapped[str | None] = mapped_column(String(50), nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class CentroCusto(Base, TimestampMixin):
    __tablename__ = "centros_custo"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    codigo: Mapped[str] = mapped_column(String(20), nullable=False)
    descricao: Mapped[str] = mapped_column(String(300), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
