from datetime import datetime
from sqlalchemy import String, Integer, DateTime, text
from sqlalchemy.dialects.postgresql import JSONB, BIGINT
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(Integer, nullable=False)
    usuario_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    acao: Mapped[str] = mapped_column(String(50), nullable=False)
    entidade: Mapped[str | None] = mapped_column(String(100), nullable=True)
    entidade_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    detalhes: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), nullable=False
    )
