import datetime
from sqlalchemy import (
    String,
    Integer,
    Numeric,
    Date,
    DateTime,
    ForeignKey,
    CheckConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, BIGINT
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class Transacao(Base):
    __tablename__ = "transacoes"

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    tenant_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tenants.id"), nullable=False
    )
    departamento_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("departamentos.id"), nullable=False
    )
    lote_importacao_id: Mapped[int] = mapped_column(Integer, nullable=False)
    data_competencia: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    data_lancamento: Mapped[datetime.date | None] = mapped_column(Date, nullable=True)

    plano_contas_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("plano_contas.id"), nullable=True
    )
    centro_custo_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("centros_custo.id"), nullable=True
    )
    produto_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("produtos.id"), nullable=True
    )
    cliente_fornecedor_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("clientes_fornecedores.id"), nullable=True
    )
    fazenda_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("fazendas.id"), nullable=True
    )
    armazem_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("armazens.id"), nullable=True
    )
    safra_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("safras.id"), nullable=True
    )

    valor: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    quantidade: Mapped[float | None] = mapped_column(Numeric(18, 6), nullable=True)
    unidade: Mapped[str | None] = mapped_column(String(10), nullable=True)
    atributos_extra: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    criado_em: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "((plano_contas_id IS NOT NULL)::int + (centro_custo_id IS NOT NULL)::int + "
            "(produto_id IS NOT NULL)::int + (cliente_fornecedor_id IS NOT NULL)::int + "
            "(fazenda_id IS NOT NULL)::int + (armazem_id IS NOT NULL)::int + "
            "(safra_id IS NOT NULL)::int) <= 1",
            name="chk_entidade",
        ),
    )
