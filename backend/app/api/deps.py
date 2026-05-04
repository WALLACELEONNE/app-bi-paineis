from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from jose import JWTError
from app.core.database import get_db
from app.core.security import decode_token
from app.services.auth_service import AuthService

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token ausente"
        )
    try:
        payload = decode_token(credentials.credentials)
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tipo de token inválido",
            )
        user_id = int(payload["sub"])
        tenant_id = int(payload["tenant_id"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
        )
    await db.execute(text(f"SET app.current_tenant_id = '{tenant_id}'"))
    auth_service = AuthService(db)
    user = await auth_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado"
        )
    return user


async def get_current_tenant_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token ausente"
        )
    try:
        payload = decode_token(credentials.credentials)
        tenant_id = int(payload["tenant_id"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido"
        )
    await db.execute(text(f"SET app.current_tenant_id = '{tenant_id}'"))
    return tenant_id


def require_role(*roles: str):
    async def role_checker(user=Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Permissão insuficiente"
            )
        return user

    return role_checker
