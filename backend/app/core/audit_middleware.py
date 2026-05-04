from app.services.audit_service import registrar_auditoria
from app.core.security import decode_token
from fastapi import Request
from jose import JWTError
import structlog

logger = structlog.get_logger()

METODOS_AUDITAVEIS = {"POST", "PUT", "PATCH", "DELETE"}
CAMINHOS_IGNORADOS = {
    "/health/live",
    "/health/ready",
    "/api/docs",
    "/api/redoc",
    "/api/openapi.json",
}


class AuditMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        request = Request(scope)
        auditar = (
            request.method in METODOS_AUDITAVEIS
            and not request.url.path.startswith(tuple(CAMINHOS_IGNORADOS))
        )

        token_data = {}
        if auditar:
            auth = request.headers.get("authorization", "")
            if auth.startswith("Bearer "):
                try:
                    token_data = decode_token(auth[7:])
                except (JWTError, KeyError):
                    pass

        await self.app(scope, receive, send)

        if auditar:
            tenant_id = token_data.get("tenant_id")
            usuario_id = token_data.get("sub")
            if usuario_id:
                usuario_id = int(usuario_id)
            if tenant_id:
                try:
                    acao_padrao = f"{request.method}:{request.url.path}"[:50]
                    await registrar_auditoria(
                        tenant_id=tenant_id,
                        acao=acao_padrao,
                        usuario_id=usuario_id,
                        ip=request.client.host if request.client else None,
                    )
                except Exception:
                    pass
