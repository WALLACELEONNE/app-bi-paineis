import datetime
from app.schemas.tenant import BaseSchema


class UsuarioRead(BaseSchema):
    id: int
    tenant_id: int
    email: str
    nome: str
    role: str
    ativo: bool
    ultimo_login: datetime.datetime | None = None
    criado_em: datetime.datetime


class UsuarioCreate(BaseSchema):
    tenant_id: int
    email: str
    senha: str
    nome: str
    role: str = "visualizador"


class UsuarioUpdate(BaseSchema):
    email: str | None = None
    nome: str | None = None
    role: str | None = None
    ativo: bool | None = None


class UsuarioLogin(BaseSchema):
    email: str
    senha: str


class TokenResponse(BaseSchema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseSchema):
    refresh_token: str


class PermissaoDepartamentoRead(BaseSchema):
    id: int
    usuario_id: int
    departamento_id: int
    pode_importar: bool
    pode_visualizar: bool
    pode_exportar: bool


class PermissaoDepartamentoCreate(BaseSchema):
    usuario_id: int
    departamento_id: int
    pode_importar: bool = False
    pode_visualizar: bool = True
    pode_exportar: bool = False


class PermissaoDepartamentoUpdate(BaseSchema):
    pode_importar: bool | None = None
    pode_visualizar: bool | None = None
    pode_exportar: bool | None = None
