from datetime import datetime
from sqlalchemy import DateTime, func, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    atualizado_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )


class TenantMixin:
    tenant_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tenants.id"), nullable=False
    )
