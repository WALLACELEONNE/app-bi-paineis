from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models import Dashboard, Widget
from app.schemas.dashboard import (
    DashboardRead,
    DashboardCreate,
    DashboardUpdate,
    WidgetRead,
    WidgetCreate,
    WidgetUpdate,
)
from app.api.deps import get_current_user, get_current_tenant_id
from app.models import Usuario

router = APIRouter(prefix="/dashboards", tags=["Dashboards"])


@router.get("/", response_model=list[DashboardRead])
async def list_dashboards(
    tenant_id: int = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    r = await db.execute(
        select(Dashboard).where(Dashboard.tenant_id == tenant_id).order_by(Dashboard.id)
    )
    return r.scalars().all()


@router.post("/", response_model=DashboardRead, status_code=201)
async def create_dashboard(
    data: DashboardCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    obj = Dashboard(tenant_id=current_user.tenant_id, **data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.put("/{dash_id}", response_model=DashboardRead)
async def update_dashboard(
    dash_id: int,
    data: DashboardUpdate,
    tenant_id: int = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    r = await db.execute(
        select(Dashboard).where(
            Dashboard.id == dash_id, Dashboard.tenant_id == tenant_id
        )
    )
    obj = r.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Dashboard não encontrado")
    for f, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, f, v)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.get("/{dash_id}/widgets", response_model=list[WidgetRead])
async def list_widgets(
    dash_id: int,
    tenant_id: int = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    r = await db.execute(
        select(Widget)
        .where(
            Widget.dashboard_id == dash_id,
            Widget.usuario_id == current_user.id,
        )
        .order_by(Widget.posicao_y, Widget.posicao_x)
    )
    return r.scalars().all()


@router.post("/{dash_id}/widgets", response_model=WidgetRead, status_code=201)
async def create_widget(
    dash_id: int,
    data: WidgetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    obj = Widget(
        dashboard_id=dash_id,
        usuario_id=current_user.id,
        **data.model_dump(exclude={"dashboard_id", "usuario_id"}),
    )
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.put("/{dash_id}/widgets/{widget_id}", response_model=WidgetRead)
async def update_widget(
    dash_id: int,
    widget_id: int,
    data: WidgetUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    r = await db.execute(
        select(Widget).where(
            Widget.id == widget_id,
            Widget.dashboard_id == dash_id,
            Widget.usuario_id == current_user.id,
        )
    )
    obj = r.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Widget não encontrado")
    for f, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, f, v)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.delete("/{dash_id}/widgets/{widget_id}", status_code=204)
async def delete_widget(
    dash_id: int,
    widget_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    r = await db.execute(
        select(Widget).where(
            Widget.id == widget_id,
            Widget.dashboard_id == dash_id,
            Widget.usuario_id == current_user.id,
        )
    )
    obj = r.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Widget não encontrado")
    await db.delete(obj)
    await db.commit()
