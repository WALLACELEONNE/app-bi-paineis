from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.departamentos import router as dept_router
from app.api.v1.dados_mestres import router as dados_router
from app.api.v1.import_config import router as config_router
from app.api.v1.usuarios import router as usuarios_router
from app.api.v1.upload_api import router as upload_router
from app.api.v1.bi import router as bi_router
from app.api.v1.dashboards_api import router as dashboards_router
from app.api.v1.export import router as export_router
from app.api.v1.dados_mestres_import import router as dm_import_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(dept_router)
api_router.include_router(dados_router)
api_router.include_router(config_router)
api_router.include_router(usuarios_router)
api_router.include_router(upload_router)
api_router.include_router(bi_router)
api_router.include_router(dashboards_router)
api_router.include_router(export_router)
api_router.include_router(dm_import_router)


@api_router.get("/")
async def api_root():
    return {"message": "BI Agro Platform API", "version": "1.0.0"}
