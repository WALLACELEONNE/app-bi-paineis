import json
import hashlib
from datetime import date, datetime
from typing import Optional
from sqlalchemy import select, func, text, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Transacao, PlanoContas, CentroCusto, Produto, Fazenda
import redis.asyncio as aioredis
from app.core.config import settings
import structlog

logger = structlog.get_logger()

_redis_pool: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = aioredis.from_url(
            settings.REDIS_CACHE_URL, decode_responses=False
        )
    return _redis_pool


def _to_serializable(val):
    from datetime import date as dt_date, datetime as dt_datetime
    from decimal import Decimal

    if isinstance(val, (dt_date, dt_datetime)):
        return val.isoformat()
    if isinstance(val, Decimal):
        return float(val)
    return val


def _serialize_row(row, colunas):
    return {
        c: _to_serializable(row[c] if isinstance(row, dict) else getattr(row, c))
        for c in colunas
    }


def _cache_key(tenant_id: int, widget: str, params: dict) -> str:
    raw = json.dumps({"t": tenant_id, "w": widget, "p": params}, sort_keys=True)
    return f"bi:{hashlib.md5(raw.encode()).hexdigest()}"


async def _cached_or_fetch(
    db: AsyncSession, tenant_id: int, widget: str, params: dict, fetcher, ttl: int = 300
):
    redis = await get_redis()
    key = _cache_key(tenant_id, widget, params)
    cached = await redis.get(key)
    if cached:
        logger.debug("bi_cache_hit", widget=widget)
        return json.loads(cached)
    data = await fetcher(db, tenant_id, params)
    await redis.setex(key, ttl, json.dumps(data, default=str))
    return data


def _filter_transacoes(query, tenant_id: int, params: dict):
    query = query.where(Transacao.tenant_id == tenant_id)
    if params.get("departamento_id"):
        query = query.where(Transacao.departamento_id == params["departamento_id"])
    if params.get("data_inicio"):
        query = query.where(Transacao.data_competencia >= params["data_inicio"])
    if params.get("data_fim"):
        query = query.where(Transacao.data_competencia <= params["data_fim"])
    if params.get("centro_custo_id"):
        ids = params["centro_custo_id"]
        if isinstance(ids, list):
            query = query.where(Transacao.centro_custo_id.in_(ids))
        else:
            query = query.where(Transacao.centro_custo_id == ids)
    if params.get("produto_id"):
        query = query.where(Transacao.produto_id == params["produto_id"])
    if params.get("fazenda_id"):
        query = query.where(Transacao.fazenda_id == params["fazenda_id"])
    if params.get("safra_id"):
        query = query.where(Transacao.safra_id == params["safra_id"])
    return query


async def _fetch_series_temporal(db: AsyncSession, tenant_id: int, params: dict):
    group = params.get("agrupamento", "mensal")
    fmt = {"diario": "YYYY-MM-DD", "mensal": "YYYY-MM", "anual": "YYYY"}[group]
    label_expr = func.to_char(Transacao.data_competencia, fmt)

    query = select(
        label_expr.label("label"),
        func.coalesce(func.sum(Transacao.valor), 0).label("valor"),
    )
    query = _filter_transacoes(query, tenant_id, params)
    query = query.group_by(label_expr).order_by(label_expr)

    result = await db.execute(query)
    rows = result.all()
    return {
        "widget_tipo": "bar_chart",
        "categorias": [str(r.label) for r in rows],
        "series": [{"nome": "Valor", "valores": [float(r.valor or 0) for r in rows]}],
    }


async def _fetch_kpi(db: AsyncSession, tenant_id: int, params: dict):
    query = select(
        func.coalesce(func.sum(Transacao.valor), 0).label("total"),
        func.count(Transacao.id).label("count"),
    )
    query = _filter_transacoes(query, tenant_id, params)
    result = await db.execute(query)
    row = result.one()
    return {
        "widget_tipo": "kpi_card",
        "total": float(row.total),
        "registros": row.count,
    }


async def _fetch_tabela(db: AsyncSession, tenant_id: int, params: dict):
    limit = min(params.get("limit", 50), 500)
    offset = params.get("offset", 0)
    query = select(Transacao)
    query = _filter_transacoes(query, tenant_id, params)
    query = (
        query.order_by(Transacao.data_competencia.desc()).offset(offset).limit(limit)
    )
    result = await db.execute(query)
    rows = result.scalars().all()
    colunas = [
        "id",
        "data_competencia",
        "departamento_id",
        "valor",
        "quantidade",
        "unidade",
    ]
    return {
        "widget_tipo": "data_table",
        "colunas": colunas,
        "linhas": [_serialize_row(r, colunas) for r in rows],
    }


async def _fetch_por_departamento(db: AsyncSession, tenant_id: int, params: dict):
    query = select(
        Transacao.departamento_id.label("label"),
        func.sum(Transacao.valor).label("valor"),
    )
    query = _filter_transacoes(query, tenant_id, params)
    query = query.where(Transacao.departamento_id.isnot(None))
    query = query.group_by(Transacao.departamento_id).order_by(
        func.sum(Transacao.valor).desc()
    )

    result = await db.execute(query)
    rows = result.all()
    dept_names = {
        1: "Contabilidade",
        2: "Financeiro",
        3: "Vendas",
        4: "Compras",
        5: "Produção",
        6: "Logística",
    }

    return {
        "widget_tipo": "pie_chart",
        "categorias": [dept_names.get(r.label, f"Dept {r.label}") for r in rows],
        "series": [{"nome": "Valor", "valores": [float(r.valor or 0) for r in rows]}],
    }


async def fetch_bi_data(
    db: AsyncSession,
    tenant_id: int,
    widget: str,
    params: dict,
) -> dict:
    fetchers = {
        "series_temporal": (_fetch_series_temporal, 300),
        "kpi": (_fetch_kpi, 120),
        "tabela": (_fetch_tabela, 60),
        "por_departamento": (_fetch_por_departamento, 300),
    }
    if widget not in fetchers:
        return {"widget_tipo": "error", "message": f"Widget '{widget}' não encontrado"}

    fetcher, ttl = fetchers[widget]
    return await _cached_or_fetch(db, tenant_id, widget, params, fetcher, ttl)


async def invalidate_bi_cache(tenant_id: int):
    redis = await get_redis()
    pattern = f"bi:*"
    cursor = 0
    while True:
        cursor, keys = await redis.scan(cursor, match=pattern, count=100)
        if keys:
            await redis.delete(*keys)
        if cursor == 0:
            break
    logger.info("bi_cache_invalidated", tenant_id=tenant_id)
