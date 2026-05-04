import io
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models import LoteImportacao, TemplateImportacao, Pipeline
from app.schemas.lote import LoteImportacaoRead
from app.services.minio_service import upload_to_minio, compute_sha256
from app.tasks.importacao import processar_importacao
from app.api.deps import get_current_user
from app.models import Usuario
import structlog

logger = structlog.get_logger()
router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post(
    "/", response_model=LoteImportacaoRead, status_code=status.HTTP_202_ACCEPTED
)
async def upload_arquivo(
    file: UploadFile = File(...),
    template_id: int = Form(...),
    pipeline_id: int = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Nome de arquivo inválido")

    # Validar template e pipeline
    tmpl = (
        await db.execute(
            select(TemplateImportacao).where(
                TemplateImportacao.id == template_id,
                TemplateImportacao.tenant_id == current_user.tenant_id,
            )
        )
    ).scalar_one_or_none()
    if not tmpl:
        raise HTTPException(status_code=404, detail="Template não encontrado")

    pipe = (
        await db.execute(
            select(Pipeline).where(
                Pipeline.id == pipeline_id,
                Pipeline.tenant_id == current_user.tenant_id,
            )
        )
    ).scalar_one_or_none()
    if not pipe:
        raise HTTPException(status_code=404, detail="Pipeline não encontrado")

    content = await file.read()
    hash_sha256 = compute_sha256(content)

    # Idempotência: verificar se já existe lote com mesmo hash concluído
    existente = (
        await db.execute(
            select(LoteImportacao).where(
                LoteImportacao.tenant_id == current_user.tenant_id,
                LoteImportacao.hash_sha256 == hash_sha256,
                LoteImportacao.status == "concluido",
            )
        )
    ).scalar_one_or_none()
    if existente:
        logger.info("upload_duplicado", lote_id=existente.id, hash=hash_sha256)
        return existente

    storage_path = upload_to_minio(content, file.filename, current_user.tenant_id)

    lote = LoteImportacao(
        tenant_id=current_user.tenant_id,
        departamento_id=tmpl.departamento_id,
        template_id=template_id,
        pipeline_id=pipeline_id,
        usuario_id=current_user.id,
        nome_arquivo=file.filename,
        hash_sha256=hash_sha256,
        tamanho_bytes=len(content),
        storage_path=storage_path,
        status="pendente",
    )
    db.add(lote)
    await db.commit()
    await db.refresh(lote)

    processar_importacao.delay(lote.id, current_user.tenant_id)
    logger.info("upload_enfileirado", lote_id=lote.id, arquivo=file.filename)

    return lote


@router.get("/{lote_id}", response_model=LoteImportacaoRead)
async def status_upload(
    lote_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    lote = (
        await db.execute(
            select(LoteImportacao).where(
                LoteImportacao.id == lote_id,
                LoteImportacao.tenant_id == current_user.tenant_id,
            )
        )
    ).scalar_one_or_none()
    if not lote:
        raise HTTPException(status_code=404, detail="Lote não encontrado")
    return lote


@router.get("/", response_model=list[LoteImportacaoRead])
async def listar_lotes(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    result = await db.execute(
        select(LoteImportacao)
        .where(
            LoteImportacao.tenant_id == current_user.tenant_id,
        )
        .order_by(LoteImportacao.criado_em.desc())
        .limit(50)
    )
    return result.scalars().all()
