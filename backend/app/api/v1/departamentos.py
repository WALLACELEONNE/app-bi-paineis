from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models import Departamento
from app.schemas.tenant import DepartamentoRead, DepartamentoCreate, DepartamentoUpdate
from app.api.deps import get_current_user, get_current_tenant_id

router = APIRouter(prefix="/departamentos", tags=["Departamentos"])


@router.get("/", response_model=list[DepartamentoRead])
async def listar(
    tenant_id: int = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    result = await db.execute(
        select(Departamento)
        .where(Departamento.tenant_id == tenant_id)
        .order_by(Departamento.id)
    )
    return result.scalars().all()


@router.get("/{dept_id}", response_model=DepartamentoRead)
async def obter(
    dept_id: int,
    tenant_id: int = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    result = await db.execute(
        select(Departamento).where(
            Departamento.id == dept_id, Departamento.tenant_id == tenant_id
        )
    )
    dept = result.scalar_one_or_none()
    if not dept:
        raise HTTPException(status_code=404, detail="Departamento não encontrado")
    return dept


@router.post("/", response_model=DepartamentoRead, status_code=status.HTTP_201_CREATED)
async def criar(
    data: DepartamentoCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    dept = Departamento(
        tenant_id=data.tenant_id, nome=data.nome, slug=data.slug, ativo=data.ativo
    )
    db.add(dept)
    await db.commit()
    await db.refresh(dept)
    return dept


@router.put("/{dept_id}", response_model=DepartamentoRead)
async def atualizar(
    dept_id: int,
    data: DepartamentoUpdate,
    tenant_id: int = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    result = await db.execute(
        select(Departamento).where(
            Departamento.id == dept_id, Departamento.tenant_id == tenant_id
        )
    )
    dept = result.scalar_one_or_none()
    if not dept:
        raise HTTPException(status_code=404, detail="Departamento não encontrado")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(dept, field, value)
    await db.commit()
    await db.refresh(dept)
    return dept


@router.delete("/{dept_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deletar(
    dept_id: int,
    tenant_id: int = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    result = await db.execute(
        select(Departamento).where(
            Departamento.id == dept_id, Departamento.tenant_id == tenant_id
        )
    )
    dept = result.scalar_one_or_none()
    if not dept:
        raise HTTPException(status_code=404, detail="Departamento não encontrado")
    await db.delete(dept)
    await db.commit()
