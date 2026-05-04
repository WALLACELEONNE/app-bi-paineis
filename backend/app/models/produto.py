from sqlalchemy import String, Numeric, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin


class Produto(Base, TimestampMixin):
    __tablename__ = "produtos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    codigo: Mapped[str] = mapped_column(String(30), nullable=False)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    tipo: Mapped[str] = mapped_column(String(30), nullable=False)
    unidade: Mapped[str] = mapped_column(String(10), nullable=False)
    cultura: Mapped[str | None] = mapped_column(String(50), nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class ClienteFornecedor(Base, TimestampMixin):
    __tablename__ = "clientes_fornecedores"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    tipo: Mapped[str] = mapped_column(String(1), nullable=False)
    razao_social: Mapped[str] = mapped_column(String(300), nullable=False)
    cnpj_cpf: Mapped[str | None] = mapped_column(String(14), nullable=True)
    ie: Mapped[str | None] = mapped_column(String(20), nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Fazenda(Base, TimestampMixin):
    __tablename__ = "fazendas"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    codigo: Mapped[str] = mapped_column(String(20), nullable=False)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    area_total: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True)
    municipio: Mapped[str | None] = mapped_column(String(100), nullable=True)
    uf: Mapped[str | None] = mapped_column(String(2), nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Armazem(Base, TimestampMixin):
    __tablename__ = "armazens"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    codigo: Mapped[str] = mapped_column(String(20), nullable=False)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    capacidade: Mapped[float | None] = mapped_column(Numeric(18, 4), nullable=True)
    unidade: Mapped[str | None] = mapped_column(String(10), nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Safra(Base, TimestampMixin):
    __tablename__ = "safras"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    codigo: Mapped[str] = mapped_column(String(20), nullable=False)
    ano_inicio: Mapped[int] = mapped_column(nullable=False)
    ano_fim: Mapped[int] = mapped_column(nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
