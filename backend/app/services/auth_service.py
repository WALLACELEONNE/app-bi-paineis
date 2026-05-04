from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Usuario
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.schemas.usuario import UsuarioCreate, TokenResponse
from jose import JWTError


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def authenticate(self, email: str, password: str) -> Usuario | None:
        result = await self.db.execute(
            select(Usuario).where(Usuario.email == email, Usuario.ativo.is_(True))
        )
        user = result.scalar_one_or_none()
        if not user or not verify_password(password, user.senha_hash):
            return None
        return user

    async def register(self, data: UsuarioCreate) -> Usuario:
        user = Usuario(
            tenant_id=data.tenant_id,
            email=data.email,
            senha_hash=get_password_hash(data.senha),
            nome=data.nome,
            role=data.role,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def get_user_by_id(self, user_id: int) -> Usuario | None:
        result = await self.db.execute(
            select(Usuario).where(Usuario.id == user_id, Usuario.ativo.is_(True))
        )
        return result.scalar_one_or_none()

    def create_tokens(self, user: Usuario) -> TokenResponse:
        payload = {"sub": str(user.id), "tenant_id": user.tenant_id, "role": user.role}
        access_token = create_access_token(payload)
        refresh_token = create_refresh_token(payload)
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    async def refresh_access_token(self, refresh_token: str) -> TokenResponse | None:
        try:
            payload = decode_token(refresh_token)
            if payload.get("type") != "refresh":
                return None
            user_id = int(payload["sub"])
            user = await self.get_user_by_id(user_id)
            if not user:
                return None
            return self.create_tokens(user)
        except JWTError:
            return None
