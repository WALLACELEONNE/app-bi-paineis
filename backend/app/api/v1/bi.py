from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.bi_service import fetch_bi_data
from app.api.deps import get_current_user, get_current_tenant_id
from app.models import Usuario

router = APIRouter(prefix="/bi", tags=["BI / Dashboards"])


@router.get("/{widget}")
async def bi_widget_data(
    widget: str,
    departamento_id: int | None = Query(None),
    data_inicio: date | None = Query(None),
    data_fim: date | None = Query(None),
    centro_custo_id: str | None = Query(None, description="IDs separados por vírgula"),
    produto_id: int | None = Query(None),
    fazenda_id: int | None = Query(None),
    safra_id: int | None = Query(None),
    agrupamento: str = Query("mensal", pattern=r"^(diario|mensal|anual)$"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    tenant_id: int = Depends(get_current_tenant_id),
    _: Usuario = Depends(get_current_user),
):
    params: dict = {
        "departamento_id": departamento_id,
        "data_inicio": data_inicio,
        "data_fim": data_fim,
        "centro_custo_id": [
            int(x) for x in centro_custo_id.split(",") if x.strip().isdigit()
        ]
        if centro_custo_id
        else None,
        "produto_id": produto_id,
        "fazenda_id": fazenda_id,
        "safra_id": safra_id,
        "agrupamento": agrupamento,
        "limit": limit,
        "offset": offset,
    }
    params = {k: v for k, v in params.items() if v is not None}
    return await fetch_bi_data(db, tenant_id, widget, params)
