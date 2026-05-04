from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.api.deps import get_current_user, get_current_tenant_id
from app.models import (
    PlanoContas,
    CentroCusto,
    Produto,
    ClienteFornecedor,
    Fazenda,
    Armazem,
    Safra,
    Tenant,
)
from app.schemas.plano_contas import (
    PlanoContasRead,
    PlanoContasCreate,
    PlanoContasUpdate,
    CentroCustoRead,
    CentroCustoCreate,
    CentroCustoUpdate,
)
from app.schemas.produto import (
    ProdutoRead,
    ProdutoCreate,
    ProdutoUpdate,
    ClienteFornecedorRead,
    ClienteFornecedorCreate,
    ClienteFornecedorUpdate,
    FazendaRead,
    FazendaCreate,
    FazendaUpdate,
    ArmazemRead,
    ArmazemCreate,
    ArmazemUpdate,
    SafraRead,
    SafraCreate,
    SafraUpdate,
)

router = APIRouter(prefix="/dados-mestres", tags=["Dados Mestres"])


def _crud_endpoints(prefix: str, model, read_schema, create_schema, update_schema):
    sub = APIRouter(prefix=f"/{prefix}", tags=[prefix])

    @sub.get("/", response_model=list[read_schema])
    async def _list(
        tenant_id: int = Depends(get_current_tenant_id),
        db: AsyncSession = Depends(get_db),
        _=Depends(get_current_user),
    ):
        result = await db.execute(
            select(model).where(model.tenant_id == tenant_id).order_by(model.id)
        )
        return result.scalars().all()

    @sub.get("/{item_id}", response_model=read_schema)
    async def _get(
        item_id: int,
        tenant_id: int = Depends(get_current_tenant_id),
        db: AsyncSession = Depends(get_db),
        _=Depends(get_current_user),
    ):
        r = await db.execute(
            select(model).where(model.id == item_id, model.tenant_id == tenant_id)
        )
        obj = r.scalar_one_or_none()
        if not obj:
            raise HTTPException(status_code=404, detail="Registro não encontrado")
        return obj

    @sub.post("/", response_model=read_schema, status_code=status.HTTP_201_CREATED)
    async def _create(
        data: create_schema,
        db: AsyncSession = Depends(get_db),
        _=Depends(get_current_user),
    ):
        obj = model(**data.model_dump())
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj

    @sub.put("/{item_id}", response_model=read_schema)
    async def _update(
        item_id: int,
        data: update_schema,
        tenant_id: int = Depends(get_current_tenant_id),
        db: AsyncSession = Depends(get_db),
        _=Depends(get_current_user),
    ):
        r = await db.execute(
            select(model).where(model.id == item_id, model.tenant_id == tenant_id)
        )
        obj = r.scalar_one_or_none()
        if not obj:
            raise HTTPException(status_code=404, detail="Registro não encontrado")
        for f, v in data.model_dump(exclude_unset=True).items():
            setattr(obj, f, v)
        await db.commit()
        await db.refresh(obj)
        return obj

    @sub.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def _delete(
        item_id: int,
        tenant_id: int = Depends(get_current_tenant_id),
        db: AsyncSession = Depends(get_db),
        _=Depends(get_current_user),
    ):
        r = await db.execute(
            select(model).where(model.id == item_id, model.tenant_id == tenant_id)
        )
        obj = r.scalar_one_or_none()
        if not obj:
            raise HTTPException(status_code=404, detail="Registro não encontrado")
        await db.delete(obj)
        await db.commit()

    return sub


router.include_router(
    _crud_endpoints(
        "plano-contas",
        PlanoContas,
        PlanoContasRead,
        PlanoContasCreate,
        PlanoContasUpdate,
    )
)
router.include_router(
    _crud_endpoints(
        "centros-custo",
        CentroCusto,
        CentroCustoRead,
        CentroCustoCreate,
        CentroCustoUpdate,
    )
)
router.include_router(
    _crud_endpoints("produtos", Produto, ProdutoRead, ProdutoCreate, ProdutoUpdate)
)
router.include_router(
    _crud_endpoints(
        "clientes-fornecedores",
        ClienteFornecedor,
        ClienteFornecedorRead,
        ClienteFornecedorCreate,
        ClienteFornecedorUpdate,
    )
)
router.include_router(
    _crud_endpoints("fazendas", Fazenda, FazendaRead, FazendaCreate, FazendaUpdate)
)
router.include_router(
    _crud_endpoints("armazens", Armazem, ArmazemRead, ArmazemCreate, ArmazemUpdate)
)
router.include_router(
    _crud_endpoints("safras", Safra, SafraRead, SafraCreate, SafraUpdate)
)
