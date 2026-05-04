import calendar
from datetime import date, datetime
from sqlalchemy import text
from app.core.database import AsyncSessionLocal
import structlog

logger = structlog.get_logger()


async def garantir_particoes(meses_futuros: int = 3):
    hoje = date.today()
    meses_necessarios = set()
    for i in range(-1, meses_futuros + 1):
        ano = hoje.year + (hoje.month + i - 1) // 12
        mes = (hoje.month + i - 1) % 12 + 1
        meses_necessarios.add((ano, mes))

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
            SELECT
                (regexp_matches(relname, 'transacoes_(\d{4})_(\d{2})'))[1]::int as ano,
                (regexp_matches(relname, 'transacoes_(\d{4})_(\d{2})'))[2]::int as mes
            FROM pg_class WHERE relname ~ 'transacoes_\d{4}_\d{2}'
        """)
        )
        existentes = {(r.ano, r.mes) for r in result}

        for ano, mes in sorted(meses_necessarios - existentes):
            nome = f"transacoes_{ano}_{mes:02d}"
            inicio = date(ano, mes, 1)
            _, ultimo_dia = calendar.monthrange(ano, mes)
            fim = date(ano, mes, ultimo_dia)
            proximo_mes = date(ano + (mes // 12), (mes % 12) + 1, 1)

            await session.execute(
                text(f"""
                CREATE TABLE IF NOT EXISTS {nome}
                PARTITION OF transacoes
                FOR VALUES FROM (DATE '{inicio}') TO (DATE '{proximo_mes}')
            """)
            )
            await session.execute(
                text(f"""
                CREATE INDEX IF NOT EXISTS idx_{nome}_competencia
                ON {nome} (data_competencia)
            """)
            )
            await session.execute(
                text(f"""
                CREATE INDEX IF NOT EXISTS idx_{nome}_tenant_dep
                ON {nome} (tenant_id, departamento_id)
            """)
            )
            await session.commit()
            logger.info(
                "particao_criada", nome=nome, inicio=str(inicio), fim=str(proximo_mes)
            )
