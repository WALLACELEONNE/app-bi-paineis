import csv
import io
import structlog
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models import TemplateImportacao, Pipeline
from app.models import Usuario
from app.schemas.lote import (
    TemplateImportacaoRead,
    TemplateImportacaoCreate,
    TemplateImportacaoUpdate,
    PipelineRead,
    PipelineCreate,
    PipelineUpdate,
)
from app.pipelines.field_catalog import DEPARTMENT_FIELDS
from app.api.deps import get_current_user, get_current_tenant_id

logger = structlog.get_logger()
router = APIRouter(prefix="/import-config", tags=["Configuração de Importação"])


# ── CRUD Templates ──


@router.get("/templates", response_model=list[TemplateImportacaoRead])
async def list_templates(
    tenant_id: int = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    r = await db.execute(
        select(TemplateImportacao)
        .where(TemplateImportacao.tenant_id == tenant_id)
        .order_by(TemplateImportacao.id)
    )
    return r.scalars().all()


@router.post("/templates", response_model=TemplateImportacaoRead, status_code=201)
async def create_template(
    data: TemplateImportacaoCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    obj = TemplateImportacao(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.put("/templates/{tmpl_id}", response_model=TemplateImportacaoRead)
async def update_template(
    tmpl_id: int,
    data: TemplateImportacaoUpdate,
    tenant_id: int = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    r = await db.execute(
        select(TemplateImportacao).where(
            TemplateImportacao.id == tmpl_id, TemplateImportacao.tenant_id == tenant_id
        )
    )
    obj = r.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Template não encontrado")
    for f, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, f, v)
        if f == "json_schema":
            obj.versao += 1
    await db.commit()
    await db.refresh(obj)
    return obj


@router.delete("/templates/{tmpl_id}", status_code=204)
async def delete_template(
    tmpl_id: int,
    tenant_id: int = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    r = await db.execute(
        select(TemplateImportacao).where(
            TemplateImportacao.id == tmpl_id, TemplateImportacao.tenant_id == tenant_id
        )
    )
    obj = r.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Template não encontrado")
    await db.delete(obj)
    await db.commit()


# ── CRUD Pipelines ──


@router.get("/pipelines", response_model=list[PipelineRead])
async def list_pipelines(
    tenant_id: int = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    r = await db.execute(
        select(Pipeline).where(Pipeline.tenant_id == tenant_id).order_by(Pipeline.id)
    )
    return r.scalars().all()


@router.post("/pipelines", response_model=PipelineRead, status_code=201)
async def create_pipeline(
    data: PipelineCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    obj = Pipeline(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


@router.put("/pipelines/{pipe_id}", response_model=PipelineRead)
async def update_pipeline(
    pipe_id: int,
    data: PipelineUpdate,
    tenant_id: int = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    r = await db.execute(
        select(Pipeline).where(Pipeline.id == pipe_id, Pipeline.tenant_id == tenant_id)
    )
    obj = r.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Pipeline não encontrado")
    for f, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, f, v)
        if f == "config_yaml":
            obj.versao += 1
    await db.commit()
    await db.refresh(obj)
    return obj


@router.delete("/pipelines/{pipe_id}", status_code=204)
async def delete_pipeline(
    pipe_id: int,
    tenant_id: int = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    r = await db.execute(
        select(Pipeline).where(Pipeline.id == pipe_id, Pipeline.tenant_id == tenant_id)
    )
    obj = r.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Pipeline não encontrado")
    await db.delete(obj)
    await db.commit()


# ── Assistente De-Para ──


@router.post("/analyze")
async def analyze_file(file: UploadFile = File(...)):
    content = await file.read()
    headers = []
    sample_rows = []
    total_rows = 0

    filename = file.filename or "arquivo"
    if filename.lower().endswith(".csv"):
        text = content.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))
        headers = reader.fieldnames or []
        for i, row in enumerate(reader):
            total_rows += 1
            if i < 5:
                sample_rows.append({k: row.get(k, "") for k in headers})
    elif filename.lower().endswith(".xlsx"):
        try:
            import openpyxl

            wb = openpyxl.load_workbook(io.BytesIO(content), data_only=True)
            ws = wb.active
            rows_iter = ws.iter_rows(min_row=1, values_only=True)
            headers = [
                str(c) if c is not None else f"coluna_{i}"
                for i, c in enumerate(next(rows_iter))
            ]

            for i, row in enumerate(rows_iter):
                total_rows += 1
                if i < 5:
                    sample_rows.append(
                        {
                            h: str(v) if v is not None else ""
                            for h, v in zip(headers, row)
                        }
                    )
        except ImportError:
            raise HTTPException(400, "XLSX não suportado — instale openpyxl")
    else:
        raise HTTPException(400, "Formato não suportado. Use CSV ou XLSX.")

    suggestions = _suggest_mappings(headers, sample_rows)

    return {
        "filename": filename,
        "headers": headers,
        "total_rows": total_rows,
        "sample_rows": sample_rows,
        "suggested_mappings": suggestions,
    }


@router.get("/field-mapping/{departamento_id}")
async def get_field_mapping(departamento_id: int):
    if departamento_id not in DEPARTMENT_FIELDS:
        raise HTTPException(404, f"Departamento {departamento_id} não encontrado")
    dept = DEPARTMENT_FIELDS[departamento_id]
    return {
        "departamento_id": departamento_id,
        "departamento_nome": dept["name"],
        "target_fields": dept["fields"],
    }


def _suggest_mappings(headers: list[str], sample_rows: list[dict]) -> list[dict]:
    suggestions = []
    matchers = {
        "data_competencia": [
            "data",
            "dt",
            "date",
            "dia",
            "competencia",
            "emissao",
            "lancamento",
        ],
        "descricao": [
            "descricao",
            "desc",
            "historico",
            "observacao",
            "obs",
            "texto",
            "nome",
        ],
        "codigo_reduzido": [
            "codigo_reduzido",
            "conta",
            "cod_conta",
            "codigo_conta",
            "plano_conta",
            "cod_plano",
        ],
        "codigo_centro_custo": [
            "centro_custo",
            "cc",
            "custo",
            "cod_cc",
            "centro_custo_codigo",
        ],
        "debito": ["debito", "deb", "valor_debito", "saida", "despesa"],
        "credito": ["credito", "cred", "valor_credito", "entrada", "receita"],
        "valor": ["valor", "total", "montante", "vr", "vlr", "valor_total", "saldo"],
        "cliente_cnpj": [
            "cliente",
            "cnpj",
            "cpf",
            "cliente_cnpj",
            "cod_cliente",
            "cliente_codigo",
        ],
        "fornecedor_cnpj": [
            "fornecedor",
            "cnpj_for",
            "forn",
            "cod_fornecedor",
            "fornecedor_cnpj",
        ],
        "produto_codigo": [
            "produto",
            "cod_produto",
            "codigo_produto",
            "item",
            "material",
            "insumo",
            "grao",
        ],
        "fazenda_codigo": ["fazenda", "faz", "cod_fazenda", "propriedade", "talhao"],
        "armazem_codigo": ["armazem", "arm", "cod_armazem", "deposito", "silo"],
        "safra": ["safra", "ano_safra", "colheita", "ciclo"],
        "quantidade_sc": [
            "quantidade",
            "qtd",
            "qtd_sc",
            "sacas",
            "sc",
            "volume",
            "peso",
        ],
        "quantidade_ton": ["ton", "tonelada", "toneladas", "peso_ton"],
        "valor_unitario": ["unitario", "preco", "preco_unitario", "preco_sc", "pu"],
        "area_plantada": ["area", "hectare", "ha", "area_ha", "area_total"],
        "distancia_km": ["distancia", "km", "percurso", "quilometro"],
        "valor_frete": ["frete", "valor_frete", "custo_frete", "transporte"],
        "tipo": ["tipo", "natureza", "operacao", "entrada_saida"],
    }

    for header in headers:
        header_lower = header.lower().strip().replace(" ", "_").replace("-", "_")
        best_match = None
        best_score = 0
        for target_key, keywords in matchers.items():
            for kw in keywords:
                if kw in header_lower or header_lower in kw:
                    score = len(kw)
                    if score > best_score:
                        best_match = target_key
                        best_score = score

        suggestion = {
            "source_column": header,
            "suggested_target": best_match,
            "confidence": "alta"
            if best_score > 4
            else "media"
            if best_match
            else "baixa",
        }
        suggestions.append(suggestion)

    return suggestions
