from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models import Usuario, PermissaoDepartamento
from app.schemas.usuario import (
    UsuarioRead,
    UsuarioCreate,
    UsuarioUpdate,
    PermissaoDepartamentoRead,
    PermissaoDepartamentoCreate,
    PermissaoDepartamentoUpdate,
)
from app.core.security import get_password_hash
from app.api.deps import get_current_user, get_current_tenant_id, require_role

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


@router.get("/", response_model=list[UsuarioRead])
async def listar(
    tenant_id: int = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("admin")),
):
    r = await db.execute(
        select(Usuario).where(Usuario.tenant_id == tenant_id).order_by(Usuario.id)
    )
    return r.scalars().all()


@router.get("/{user_id}", response_model=UsuarioRead)
async def obter(
    user_id: int,
    tenant_id: int = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("admin")),
):
    r = await db.execute(
        select(Usuario).where(Usuario.id == user_id, Usuario.tenant_id == tenant_id)
    )
    u = r.scalar_one_or_none()
    if not u:
        raise HTTPException(404, "Usuário não encontrado")
    return u


@router.post("/", response_model=UsuarioRead, status_code=201)
async def criar(
    data: UsuarioCreate,
    tenant_id: int = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("admin")),
):
    from app.services.auth_service import AuthService

    auth = AuthService(db)
    result = await db.execute(
        select(Usuario).where(
            Usuario.email == data.email, Usuario.tenant_id == tenant_id
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(400, "Email já cadastrado neste tenant")
    data.tenant_id = tenant_id
    return await auth.register(data)


@router.put("/{user_id}", response_model=UsuarioRead)
async def atualizar(
    user_id: int,
    data: UsuarioUpdate,
    tenant_id: int = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("admin")),
):
    r = await db.execute(
        select(Usuario).where(Usuario.id == user_id, Usuario.tenant_id == tenant_id)
    )
    u = r.scalar_one_or_none()
    if not u:
        raise HTTPException(404, "Usuário não encontrado")
    for f, v in data.model_dump(exclude_unset=True).items():
        setattr(u, f, v)
    await db.commit()
    await db.refresh(u)
    return u


@router.delete("/{user_id}", status_code=204)
async def deletar(
    user_id: int,
    tenant_id: int = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("admin")),
):
    r = await db.execute(
        select(Usuario).where(Usuario.id == user_id, Usuario.tenant_id == tenant_id)
    )
    u = r.scalar_one_or_none()
    if not u:
        raise HTTPException(404, "Usuário não encontrado")
    await db.delete(u)
    await db.commit()


@router.get("/{user_id}/permissoes", response_model=list[PermissaoDepartamentoRead])
async def listar_permissoes(
    user_id: int, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)
):
    r = await db.execute(
        select(PermissaoDepartamento).where(PermissaoDepartamento.usuario_id == user_id)
    )
    return r.scalars().all()


@router.post(
    "/{user_id}/permissoes", response_model=PermissaoDepartamentoRead, status_code=201
)
async def criar_permissao(
    user_id: int,
    data: PermissaoDepartamentoCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("admin")),
):
    data.usuario_id = user_id
    obj = PermissaoDepartamento(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.put("/{user_id}/permissoes/{perm_id}", response_model=PermissaoDepartamentoRead)
async def atualizar_permissao(
    user_id: int,
    perm_id: int,
    data: PermissaoDepartamentoUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("admin")),
):
    r = await db.execute(
        select(PermissaoDepartamento).where(
            PermissaoDepartamento.id == perm_id,
            PermissaoDepartamento.usuario_id == user_id,
        )
    )
    obj = r.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Permissão não encontrada")
    for f, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, f, v)
    await db.commit()
    await db.refresh(obj)
    return obj
