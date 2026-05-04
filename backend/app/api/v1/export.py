from datetime import date
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.export_service import exportar_excel
from app.api.deps import get_current_user, get_current_tenant_id
from app.models import Usuario
import io

router = APIRouter(prefix="/export", tags=["Exportação"])


@router.get("/excel")
async def export_excel(
    data_inicio: date | None = Query(None),
    data_fim: date | None = Query(None),
    departamento_id: int | None = Query(None),
    limit: int = Query(5000, ge=1, le=50000),
    db: AsyncSession = Depends(get_db),
    tenant_id: int = Depends(get_current_tenant_id),
    _: Usuario = Depends(get_current_user),
):
    params = {
        "data_inicio": data_inicio,
        "data_fim": data_fim,
        "departamento_id": departamento_id,
        "limit": limit,
    }
    params = {k: v for k, v in params.items() if v is not None}
    content = await exportar_excel(db, tenant_id, params, "export_transacoes.xlsx")
    return StreamingResponse(
        io.BytesIO(content),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=transacoes.xlsx"},
    )
