import csv
import io
from datetime import datetime, date
from typing import Optional
from sqlalchemy import text
from app.core.database import AsyncSessionLocal
from app.models import LoteImportacao, Transacao
from app.schemas.transacao import TransacaoCreate
from app.services.minio_service import get_file_from_minio
from app.pipelines.engine import PipelineEngine
import structlog

logger = structlog.get_logger()


async def processar_lote(lote: LoteImportacao) -> dict:
    logger.info("importacao_processando", lote_id=lote.id)

    # Marcar como processando
    async with AsyncSessionLocal() as session:
        lote_db = await session.get(LoteImportacao, lote.id)
        lote_db.status = "processando"
        lote_db.iniciado_em = datetime.utcnow()
        await session.commit()

    try:
        # Buscar template e pipeline
        async with AsyncSessionLocal() as session:
            from app.models import TemplateImportacao, Pipeline

            tmpl = await session.get(TemplateImportacao, lote.template_id)
            pipe = await session.get(Pipeline, lote.pipeline_id)
            template_schema = tmpl.json_schema
            pipeline_yaml = pipe.config_yaml

        # Ler arquivo do MinIO
        file_content = get_file_from_minio(lote.storage_path)
        raw_data = _parse_csv(file_content, template_schema)

        # Executar pipeline
        engine = PipelineEngine(pipeline_yaml, template_schema)
        processed, results = engine.execute(raw_data)

        # Inserir no banco
        total_ok = 0
        async with AsyncSessionLocal() as session:
            for row in processed:
                trans = Transacao(
                    tenant_id=lote.tenant_id,
                    departamento_id=lote.departamento_id,
                    lote_importacao_id=lote.id,
                    data_competencia=_parse_date(
                        row.get("data_competencia") or row.get("data")
                    ),
                    data_lancamento=_parse_date(row.get("data_lancamento")),
                    plano_contas_id=row.get("plano_contas_id"),
                    centro_custo_id=row.get("centro_custo_id"),
                    produto_id=row.get("produto_id"),
                    cliente_fornecedor_id=row.get("cliente_fornecedor_id"),
                    fazenda_id=row.get("fazenda_id"),
                    armazem_id=row.get("armazem_id"),
                    safra_id=row.get("safra_id"),
                    valor=row.get("valor") or row.get("saldo_total"),
                    quantidade=row.get("quantidade"),
                    unidade=row.get("unidade"),
                    atributos_extra={
                        k: v
                        for k, v in row.items()
                        if k
                        not in {
                            "data_competencia",
                            "data_lancamento",
                            "data",
                            "plano_contas_id",
                            "centro_custo_id",
                            "produto_id",
                            "cliente_fornecedor_id",
                            "fazenda_id",
                            "armazem_id",
                            "safra_id",
                            "valor",
                            "saldo_total",
                            "quantidade",
                            "unidade",
                        }
                    },
                )
                session.add(trans)
                total_ok += 1
            await session.commit()

        # Atualizar lote como concluído
        async with AsyncSessionLocal() as session:
            lote_db = await session.get(LoteImportacao, lote.id)
            lote_db.status = "concluido"
            lote_db.concluido_em = datetime.utcnow()
            lote_db.total_linhas = len(raw_data)
            lote_db.linhas_ok = total_ok
            lote_db.linhas_erro = len(raw_data) - len(processed)
            await session.commit()

        logger.info("importacao_concluida", lote_id=lote.id, linhas=total_ok)
        return {
            "status": "concluido",
            "lote_id": lote.id,
            "linhas_processadas": total_ok,
        }

    except Exception as e:
        async with AsyncSessionLocal() as session:
            lote_db = await session.get(LoteImportacao, lote.id)
            lote_db.status = "erro"
            lote_db.erro_mensagem = str(e)
            await session.commit()
        logger.error("importacao_falhou", lote_id=lote.id, error=str(e))
        raise


def _parse_csv(content: bytes, template_schema: dict) -> list[dict]:
    colunas = template_schema.get("colunas", [])
    col_names = [c["nome"] for c in colunas]
    reader = csv.DictReader(io.StringIO(content.decode("utf-8-sig")))
    rows = []
    for row in reader:
        filtered = {}
        for name in col_names:
            if name in row:
                filtered[name] = row[name]
        # Mapear colunas extras
        for key, value in row.items():
            if key not in filtered:
                filtered[key] = value
        rows.append(filtered)
    return rows


def _parse_date(value: Optional[str]) -> date | None:
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(str(value).strip(), fmt).date()
        except (ValueError, TypeError):
            continue
    return None
