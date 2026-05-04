from sqlalchemy import String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin


class Tenant(Base, TimestampMixin):
    __tablename__ = "tenants"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    departamentos: Mapped[list["Departamento"]] = relationship(
        back_populates="tenant", lazy="selectin"
    )


class Departamento(Base, TimestampMixin):
    __tablename__ = "departamentos"
    __table_args__ = (UniqueConstraint("tenant_id", "slug"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(50), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    tenant: Mapped["Tenant"] = relationship(back_populates="departamentos")
