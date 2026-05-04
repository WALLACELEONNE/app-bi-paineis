from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.auth_service import AuthService
from app.schemas.usuario import (
    UsuarioLogin,
    TokenResponse,
    RefreshTokenRequest,
    UsuarioCreate,
    UsuarioRead,
)
from app.api.deps import get_current_user, require_role
from app.models import Usuario

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login", response_model=TokenResponse)
async def login(data: UsuarioLogin, db: AsyncSession = Depends(get_db)):
    auth = AuthService(db)
    user = await auth.authenticate(data.email, data.senha)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Email ou senha inválidos"
        )
    user.ultimo_login = datetime.utcnow()
    await db.commit()
    return auth.create_tokens(user)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    auth = AuthService(db)
    result = await auth.refresh_access_token(data.refresh_token)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido ou expirado",
        )
    return result


@router.post(
    "/register", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED
)
async def register(
    data: UsuarioCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_role("admin")),
):
    auth = AuthService(db)
    existing = await auth.authenticate(data.email, "dummy")
    from sqlalchemy import select

    result = await db.execute(select(Usuario).where(Usuario.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email já cadastrado"
        )
    user = await auth.register(data)
    return user


@router.get("/me", response_model=UsuarioRead)
async def me(current_user=Depends(get_current_user)):
    return current_user
