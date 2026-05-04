import csv
import io
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import get_db
from app.api.deps import get_current_user, get_current_tenant_id
from app.models import Usuario
import structlog

logger = structlog.get_logger()
router = APIRouter(prefix="/dados-mestres", tags=["Dados Mestres - Importação"])

ENTITIES = {
    "plano-contas": {
        "table": "plano_contas",
        "columns": [
            "tenant_id",
            "codigo_reduzido",
            "codigo_estruturado",
            "descricao",
            "nivel",
            "natureza",
            "grupo",
            "ativo",
        ],
        "required": ["codigo_reduzido", "descricao", "nivel"],
        "defaults": {"ativo": True},
    },
    "centros-custo": {
        "table": "centros_custo",
        "columns": ["tenant_id", "codigo", "descricao", "ativo"],
        "required": ["codigo", "descricao"],
        "defaults": {"ativo": True},
    },
    "produtos": {
        "table": "produtos",
        "columns": [
            "tenant_id",
            "codigo",
            "nome",
            "tipo",
            "unidade",
            "cultura",
            "ativo",
        ],
        "required": ["codigo", "nome", "tipo", "unidade"],
        "defaults": {"ativo": True},
    },
    "clientes-fornecedores": {
        "table": "clientes_fornecedores",
        "columns": ["tenant_id", "tipo", "razao_social", "cnpj_cpf", "ie", "ativo"],
        "required": ["tipo", "razao_social"],
        "defaults": {"ativo": True},
    },
    "fazendas": {
        "table": "fazendas",
        "columns": [
            "tenant_id",
            "codigo",
            "nome",
            "area_total",
            "municipio",
            "uf",
            "ativo",
        ],
        "required": ["codigo", "nome"],
        "defaults": {"ativo": True},
    },
    "armazens": {
        "table": "armazens",
        "columns": ["tenant_id", "codigo", "nome", "capacidade", "unidade", "ativo"],
        "required": ["codigo", "nome"],
        "defaults": {"ativo": True},
    },
    "safras": {
        "table": "safras",
        "columns": ["tenant_id", "codigo", "ano_inicio", "ano_fim", "ativo"],
        "required": ["codigo", "ano_inicio", "ano_fim"],
        "defaults": {"ativo": True},
    },
}


@router.post("/import/{entity}")
async def importar_csv(
    entity: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    tenant_id: int = Depends(get_current_tenant_id),
    _: Usuario = Depends(get_current_user),
):
    if entity not in ENTITIES:
        raise HTTPException(
            400, f"Entidade '{entity}' inválida. Opções: {', '.join(ENTITIES.keys())}"
        )

    config = ENTITIES[entity]
    content = (await file.read()).decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(content))

    if not reader.fieldnames:
        raise HTTPException(400, "CSV vazio ou sem cabeçalho")

    rows = list(reader)
    if not rows:
        raise HTTPException(400, "CSV sem linhas de dados")

    valid_cols = [c for c in config["columns"] if c != "tenant_id"]
    unknown = set(reader.fieldnames) - set(valid_cols)
    if unknown:
        raise HTTPException(
            400,
            f"Colunas não reconhecidas: {', '.join(sorted(unknown))}. Colunas aceitas: {', '.join(valid_cols)}",
        )

    col_placeholders = []
    col_names = []
    values_dict = {}
    defaults = config.get("defaults", {})
    for i, col in enumerate(config["columns"]):
        if col == "tenant_id":
            values_dict[f"p{i}"] = tenant_id
        elif col in reader.fieldnames:
            values_dict[f"p{i}"] = None
        elif col in defaults:
            values_dict[f"p{i}"] = defaults[col]
        else:
            values_dict[f"p{i}"] = None
        col_names.append(col)
        in_csv = col in reader.fieldnames or col == "tenant_id"
        has_default = col in defaults
        col_placeholders.append(f":p{i}" if (in_csv or has_default) else "NULL")

    insert_sql = f"INSERT INTO {config['table']} ({', '.join(col_names)}) VALUES ({', '.join(col_placeholders)}) ON CONFLICT DO NOTHING"

    ok = 0
    erros = 0
    for row in rows:
        params = {}
        skip = False
        for i, col in enumerate(config["columns"]):
            if col == "tenant_id":
                params[f"p{i}"] = tenant_id
            elif col in row:
                val = row[col].strip() if row[col] else None
                if col in config["required"] and not val:
                    skip = True
                    break
                col_type = _infer_type(col, val)
                if col_type == "int":
                    try:
                        params[f"p{i}"] = int(val) if val else None
                    except ValueError:
                        skip = True
                        break
                elif col_type == "float":
                    try:
                        params[f"p{i}"] = float(val.replace(",", ".")) if val else None
                    except ValueError:
                        skip = True
                        break
                elif col_type == "bool":
                    params[f"p{i}"] = (
                        val.lower() in ("true", "t", "1", "sim", "s") if val else True
                    )
                else:
                    params[f"p{i}"] = val
            elif col in defaults:
                params[f"p{i}"] = defaults[col]
            else:
                params[f"p{i}"] = None
        if skip:
            erros += 1
            continue
        try:
            await db.execute(text(insert_sql), params)
            ok += 1
        except Exception:
            erros += 1

    await db.commit()
    logger.info(
        "dados_mestres_import", entity=entity, ok=ok, erros=erros, tenant_id=tenant_id
    )
    return {
        "entity": entity,
        "table": config["table"],
        "ok": ok,
        "erros": erros,
        "total": len(rows),
    }


def _infer_type(col: str, val: str | None) -> str:
    if col in ("nivel", "ano_inicio", "ano_fim"):
        return "int"
    if col in ("area_total", "capacidade"):
        return "float"
    return "str"
