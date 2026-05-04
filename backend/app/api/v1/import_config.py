from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models import TemplateImportacao, Pipeline
from app.schemas.lote import (
    TemplateImportacaoRead,
    TemplateImportacaoCreate,
    TemplateImportacaoUpdate,
    PipelineRead,
    PipelineCreate,
    PipelineUpdate,
)
from app.api.deps import get_current_user, get_current_tenant_id

router = APIRouter(prefix="/import-config", tags=["Configuração de Importação"])


@router.get("/templates", response_model=list[TemplateImportacaoRead])
async def list_templates(
    tenant_id: int = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    r = await db.execute(
        select(TemplateImportacao)
        .where(TemplateImportacao.tenant_id == tenant_id)
        .order_by(TemplateImportacao.id)
    )
    return r.scalars().all()


@router.post("/templates", response_model=TemplateImportacaoRead, status_code=201)
async def create_template(
    data: TemplateImportacaoCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    obj = TemplateImportacao(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.put("/templates/{tmpl_id}", response_model=TemplateImportacaoRead)
async def update_template(
    tmpl_id: int,
    data: TemplateImportacaoUpdate,
    tenant_id: int = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    r = await db.execute(
        select(TemplateImportacao).where(
            TemplateImportacao.id == tmpl_id, TemplateImportacao.tenant_id == tenant_id
        )
    )
    obj = r.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Template não encontrado")
    for f, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, f, v)
        if f == "json_schema":
            obj.versao += 1
    await db.commit()
    await db.refresh(obj)
    return obj


@router.delete("/templates/{tmpl_id}", status_code=204)
async def delete_template(
    tmpl_id: int,
    tenant_id: int = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    r = await db.execute(
        select(TemplateImportacao).where(
            TemplateImportacao.id == tmpl_id, TemplateImportacao.tenant_id == tenant_id
        )
    )
    obj = r.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Template não encontrado")
    await db.delete(obj)
    await db.commit()


@router.get("/pipelines", response_model=list[PipelineRead])
async def list_pipelines(
    tenant_id: int = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    r = await db.execute(
        select(Pipeline).where(Pipeline.tenant_id == tenant_id).order_by(Pipeline.id)
    )
    return r.scalars().all()


@router.post("/pipelines", response_model=PipelineRead, status_code=201)
async def create_pipeline(
    data: PipelineCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    obj = Pipeline(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.put("/pipelines/{pipe_id}", response_model=PipelineRead)
async def update_pipeline(
    pipe_id: int,
    data: PipelineUpdate,
    tenant_id: int = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    r = await db.execute(
        select(Pipeline).where(Pipeline.id == pipe_id, Pipeline.tenant_id == tenant_id)
    )
    obj = r.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Pipeline não encontrado")
    for f, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, f, v)
        if f == "config_yaml":
            obj.versao += 1
    await db.commit()
    await db.refresh(obj)
    return obj


@router.delete("/pipelines/{pipe_id}", status_code=204)
async def delete_pipeline(
    pipe_id: int,
    tenant_id: int = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    r = await db.execute(
        select(Pipeline).where(Pipeline.id == pipe_id, Pipeline.tenant_id == tenant_id)
    )
    obj = r.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Pipeline não encontrado")
    await db.delete(obj)
    await db.commit()
