# Projeto: Painel de BI Multi-Departamental para Agronegócio (Grãos)

**Versão:** 3.0 (Arquitetura robusta e escalável)
**Data:** 04/05/2026

**Visão Geral:**
Plataforma web multi-tenant para importação de dados de diversas áreas (contabilidade, finanças, vendas, compras, produção, logística), processamento inteligente com regras de negócio configuráveis e exibição de dashboards de BI. O foco inicial é o setor de grãos (agronegócio), mas a arquitetura é modular e escalável para qualquer segmento.

---

## 1. Objetivos e Escopo

- **Upload multi-formato**: aceitar CSV, XLSX, e integração com APIs externas.
- **Processamento flexível**: cada departamento define templates de importação, validações e pipelines de transformação (receitas, regras de negócio).
- **Dados mestres**: plano de contas, centros de custo, tabelas de produtos/grãos, clientes, fornecedores, fazendas, armazéns.
- **Multi-tenancy nativa**: isolamento lógico por tenant via `tenant_id` em todas as tabelas + Row-Level Security no PostgreSQL.
- **Dashboards interativos**: gráficos (ECharts), tabelas dinâmicas (AG Grid), filtros por período, centro de custo, cultura, fazenda. Layout persistido por usuário.
- **Auditoria completa**: toda importação, alteração em dados mestres e acesso a relatórios é registrado com usuário, timestamp e IP.
- **Versionamento de API**: prefixo `/api/v1/`, `/api/v2/` para evolução sem quebra.
- **Arquitetura escalável**: processamento assíncrono, cache, materialized views, particionamento nativo, streaming para grandes volumes, possibilidade de migrar para ClickHouse no futuro.

---

## 2. Arquitetura Geral

```
[Frontend React + TypeScript + Ant Design]
        |
[API Gateway (FastAPI)] ─── [Redis: cache de consultas]
        |
[Redis: fila de tarefas]
        |
[Workers Celery] ─── [Engine de Processamento Configurável (Polars)]
        |                    |
        |              [MinIO / S3]: armazenamento de arquivos
        |
[PostgreSQL] ← Dados processados e agregados
        |
[ClickHouse] (futuro / opcional) para consultas analíticas pesadas

Observabilidade: Prometheus + Grafana | OpenTelemetry | Flower (Celery)
```

**Fluxo de importação:**

1. Usuário faz upload do arquivo → armazenado no MinIO com hash SHA-256.
2. API enfileira tarefa no Redis → retorna `job_id` para polling de progresso.
3. Worker Celery lê o arquivo do MinIO → valida contra o template JSON Schema do departamento.
4. Engine Polars processa em modo streaming/lazy o pipeline YAML.
5. Resultados inseridos em lote no PostgreSQL dentro de uma transação atômica.
6. Linhagem registrada (arquivo → pipeline → linhas geradas).
7. Materialized views refrescadas ao final do lote.
8. Progresso publicado via Redis Pub/Sub para atualização em tempo real no frontend.

**Principais módulos:**

### a) Módulo de Dados Mestres (Core)
- **Planos de contas** (base inicial: `Tran447`).
- **Centros de custo** (base inicial fornecida).
- **Entidades de negócio**: produtos (grãos/insumos/serviços), clientes/fornecedores, fazendas, armazéns, safras.
- **Tabelas de domínio dinâmico** (parâmetros configuráveis por departamento e tenant).

### b) Módulo de Importação e Processamento
- **Templates de layout** por departamento (JSON Schema com validação rigorosa).
- **Validação** (tipos, obrigatoriedade, integridade referencial, regras customizadas).
- **Pipeline configurável** (sequência de transformações atômicas com rollback).
- **Motor de regras**: expressões matemáticas, agrupamentos, condicionais, joins com dados mestres.
- **Idempotência**: hash SHA-256 do arquivo impede reprocessamento duplicado.
- **Chunked/streaming processing**: Polars lazy frames + streaming CSV para arquivos que excedem a RAM.
- **Linhagem de dados**: rastreabilidade completa de cada linha até o arquivo de origem e pipeline aplicado.

### c) Módulo de Dashboards
- **Widget Registry**: catálogo de componentes registráveis (gráfico de barras, linha, pizza, KPI card, tabela dinâmica, mapa de calor).
- **Layout persistido**: cada usuário salva seu arranjo de widgets por dashboard.
- **Cache inteligente**: Redis com TTL por consulta e invalidação seletiva.
- **Drill-down** e exportação (PDF, Excel, CSV).
- **Exportação agendada**: relatórios automáticos via Celery Beat (diário, semanal, mensal).

### d) Módulo de Administração
- Cadastro de tenants, departamentos, templates, pipelines, dashboards.
- Gestão de usuários e permissões (RBAC com escopo por departamento).

### e) Módulo de Segurança e Governança
- Autenticação JWT (access + refresh tokens).
- RBAC com papéis: `admin`, `gestor`, `analista`, `visualizador`.
- Permissões granulares por departamento e por widget.
- Multi-tenancy via `tenant_id` + Row-Level Security no PostgreSQL.
- Auditoria completa (`audit_log`) em todas as operações sensíveis.
- Rate limiting por tenant e por usuário.

---

## 3. Modelagem de Dados

### 3.1 Tabelas de Multi-Tenancy

```sql
CREATE TABLE tenants (
    id          serial PRIMARY KEY,
    nome        varchar(200) NOT NULL,
    slug        varchar(50)  NOT NULL UNIQUE,
    ativo       boolean      NOT NULL DEFAULT true,
    criado_em   timestamptz  NOT NULL DEFAULT now()
);
```

### 3.2 Tabelas de Domínio e Configuração

```sql
CREATE TABLE departamentos (
    id          serial PRIMARY KEY,
    tenant_id   int         NOT NULL REFERENCES tenants(id),
    nome        varchar(100) NOT NULL,
    slug        varchar(50)  NOT NULL,
    ativo       boolean      NOT NULL DEFAULT true,
    UNIQUE (tenant_id, slug)
);

CREATE TABLE templates_importacao (
    id              serial PRIMARY KEY,
    tenant_id       int          NOT NULL REFERENCES tenants(id),
    departamento_id int          NOT NULL REFERENCES departamentos(id),
    nome            varchar(100) NOT NULL,
    versao          int          NOT NULL DEFAULT 1,
    schema_json     jsonb        NOT NULL,  -- JSON Schema com colunas, tipos, obrigatoriedade, mapeamento
    criado_em       timestamptz  NOT NULL DEFAULT now()
);

CREATE TABLE pipelines (
    id              serial PRIMARY KEY,
    tenant_id       int          NOT NULL REFERENCES tenants(id),
    departamento_id int          NOT NULL REFERENCES departamentos(id),
    nome            varchar(100) NOT NULL,
    versao          int          NOT NULL DEFAULT 1,
    config_yaml     text         NOT NULL,  -- Pipeline de steps (validate → transform → aggregate → materialize)
    ativo           boolean      NOT NULL DEFAULT true,
    criado_em       timestamptz  NOT NULL DEFAULT now()
);
```

### 3.3 Tabelas Mestres (todas com `tenant_id`)

```sql
CREATE TABLE plano_contas (
    id               serial PRIMARY KEY,
    tenant_id        int          NOT NULL REFERENCES tenants(id),
    codigo_reduzido  varchar(20)  NOT NULL,
    codigo_estruturado varchar(50),
    descricao        varchar(300) NOT NULL,
    nivel            int          NOT NULL,
    natureza         varchar(10),           -- 'credora' / 'devedora'
    grupo            varchar(50),
    ativo            boolean      NOT NULL DEFAULT true,
    UNIQUE (tenant_id, codigo_reduzido)
);

CREATE TABLE centros_custo (
    id          serial PRIMARY KEY,
    tenant_id   int          NOT NULL REFERENCES tenants(id),
    codigo      varchar(20)  NOT NULL,
    descricao   varchar(300) NOT NULL,
    ativo       boolean      NOT NULL DEFAULT true,
    UNIQUE (tenant_id, codigo)
);

CREATE TABLE produtos (
    id          serial PRIMARY KEY,
    tenant_id   int          NOT NULL REFERENCES tenants(id),
    codigo      varchar(30)  NOT NULL,
    nome        varchar(200) NOT NULL,
    tipo        varchar(30)  NOT NULL,       -- 'grao', 'insumo', 'servico'
    unidade     varchar(10)  NOT NULL,       -- 'sc', 'ton', 'kg', 'lt'
    cultura     varchar(50),                 -- 'soja', 'milho', 'trigo', etc.
    ativo       boolean      NOT NULL DEFAULT true,
    UNIQUE (tenant_id, codigo)
);

CREATE TABLE clientes_fornecedores (
    id           serial PRIMARY KEY,
    tenant_id    int          NOT NULL REFERENCES tenants(id),
    tipo         varchar(1)   NOT NULL,       -- 'C' = cliente, 'F' = fornecedor, 'A' = ambos
    razao_social varchar(300) NOT NULL,
    cnpj_cpf     varchar(14),
    ie           varchar(20),
    ativo        boolean      NOT NULL DEFAULT true
);

CREATE TABLE fazendas (
    id          serial PRIMARY KEY,
    tenant_id   int          NOT NULL REFERENCES tenants(id),
    codigo      varchar(20)  NOT NULL,
    nome        varchar(200) NOT NULL,
    area_total  numeric(18,4),
    municipio   varchar(100),
    uf          varchar(2),
    ativo       boolean      NOT NULL DEFAULT true,
    UNIQUE (tenant_id, codigo)
);

CREATE TABLE armazens (
    id          serial PRIMARY KEY,
    tenant_id   int      NOT NULL REFERENCES tenants(id),
    codigo      varchar(20)  NOT NULL,
    nome        varchar(200) NOT NULL,
    capacidade  numeric(18,4),
    unidade     varchar(10),           -- 'ton', 'sc'
    ativo       boolean NOT NULL DEFAULT true,
    UNIQUE (tenant_id, codigo)
);

CREATE TABLE safras (
    id          serial PRIMARY KEY,
    tenant_id   int      NOT NULL REFERENCES tenants(id),
    codigo      varchar(20)  NOT NULL,  -- ex: '23/24', '24/25'
    ano_inicio  int      NOT NULL,
    ano_fim     int      NOT NULL,
    ativo       boolean  NOT NULL DEFAULT true,
    UNIQUE (tenant_id, codigo)
);
```

### 3.4 Tabelas Transacionais (Modelo com FK específica e Particionamento)

Substitui-se a abordagem genérica `entidade_tipo`/`entidade_id` (sem FK real) pelo padrão de **colunas FK explícitas com CHECK constraint**, garantindo integridade referencial. A tabela é particionada por `data_competencia` (mensal) desde o início.

```sql
CREATE TABLE transacoes (
    id                  bigserial,
    tenant_id           int             NOT NULL REFERENCES tenants(id),
    departamento_id     int             NOT NULL REFERENCES departamentos(id),
    lote_importacao_id  int             NOT NULL,               -- FK para lote (rastreabilidade)
    data_competencia    date            NOT NULL,
    data_lancamento     date,
    -- FKs específicas por entidade (CHECK garante que apenas uma seja preenchida)
    plano_contas_id     int             REFERENCES plano_contas(id),
    centro_custo_id     int             REFERENCES centros_custo(id),
    produto_id          int             REFERENCES produtos(id),
    cliente_fornecedor_id int           REFERENCES clientes_fornecedores(id),
    fazenda_id          int             REFERENCES fazendas(id),
    armazem_id          int             REFERENCES armazens(id),
    safra_id            int             REFERENCES safras(id),
    -- Valores
    valor               numeric(18,2),
    quantidade           numeric(18,6),
    unidade             varchar(10),
    -- Metadados flexíveis (apenas para campos verdadeiramente variáveis)
    atributos_extra     jsonb,
    -- Controle
    criado_em           timestamptz     NOT NULL DEFAULT now(),
    CONSTRAINT chk_entidade CHECK (
        (plano_contas_id IS NOT NULL)::int +
        (centro_custo_id IS NOT NULL)::int +
        (produto_id IS NOT NULL)::int +
        (cliente_fornecedor_id IS NOT NULL)::int +
        (fazenda_id IS NOT NULL)::int +
        (armazem_id IS NOT NULL)::int +
        (safra_id IS NOT NULL)::int <= 1
    )
) PARTITION BY RANGE (data_competencia);

-- Partições mensais (criadas automaticamente via scheduler ou trigger)
CREATE TABLE transacoes_2026_05 PARTITION OF transacoes
    FOR VALUES FROM ('2026-05-01') TO ('2026-06-01');

-- Índices
CREATE INDEX idx_transacoes_tenant_dep   ON transacoes (tenant_id, departamento_id);
CREATE INDEX idx_transacoes_competencia  ON transacoes (data_competencia);
CREATE INDEX idx_transacoes_plano_contas ON transacoes (plano_contas_id)   WHERE plano_contas_id IS NOT NULL;
CREATE INDEX idx_transacoes_centro_custo ON transacoes (centro_custo_id)   WHERE centro_custo_id IS NOT NULL;
CREATE INDEX idx_transacoes_produto      ON transacoes (produto_id)        WHERE produto_id IS NOT NULL;
CREATE INDEX idx_transacoes_lote         ON transacoes (lote_importacao_id);
```

### 3.5 Tabelas de Importação, Linhagem e Auditoria

```sql
CREATE TABLE lotes_importacao (
    id              serial PRIMARY KEY,
    tenant_id       int           NOT NULL REFERENCES tenants(id),
    departamento_id int           NOT NULL REFERENCES departamentos(id),
    template_id     int           NOT NULL REFERENCES templates_importacao(id),
    pipeline_id     int           NOT NULL REFERENCES pipelines(id),
    usuario_id      int           NOT NULL,                         -- FK para users
    nome_arquivo    varchar(500)  NOT NULL,
    hash_sha256     varchar(64)   NOT NULL,                         -- Idempotência
    tamanho_bytes   bigint,
    status          varchar(20)   NOT NULL DEFAULT 'pendente',      -- pendente, processando, concluido, erro, parcial
    total_linhas    int,
    linhas_ok       int           DEFAULT 0,
    linhas_erro     int           DEFAULT 0,
    erro_mensagem   text,
    storage_path    varchar(1000),                                  -- Caminho no MinIO
    iniciado_em     timestamptz,
    concluido_em    timestamptz,
    criado_em       timestamptz   NOT NULL DEFAULT now(),
    UNIQUE (tenant_id, hash_sha256)
);

CREATE TABLE linhagem_dados (
    id              bigserial PRIMARY KEY,
    tenant_id       int           NOT NULL REFERENCES tenants(id),
    transacao_id    bigint        NOT NULL,                         -- FK postergada (particionada)
    lote_id         int           NOT NULL REFERENCES lotes_importacao(id),
    pipeline_step   varchar(100)  NOT NULL,                         -- qual step gerou esta linha
    linha_arquivo   int,                                            -- número da linha no arquivo original
    dados_originais jsonb,                                          -- snapshot da linha antes das transformações
    criado_em       timestamptz   NOT NULL DEFAULT now()
);

CREATE TABLE audit_log (
    id          bigserial PRIMARY KEY,
    tenant_id   int           NOT NULL,
    usuario_id  int,
    acao        varchar(50)   NOT NULL,   -- 'importacao', 'login', 'alteracao_template', 'exportacao_relatorio', etc.
    entidade    varchar(100),             -- 'lotes_importacao', 'plano_contas', etc.
    entidade_id int,
    detalhes    jsonb,                    -- snapshot do que foi alterado
    ip          varchar(45),
    criado_em   timestamptz  NOT NULL DEFAULT now()
);

CREATE INDEX idx_audit_tenant_entidade ON audit_log (tenant_id, entidade, entidade_id);
CREATE INDEX idx_audit_criado_em       ON audit_log (criado_em);
```

### 3.6 Tabelas de Usuários, Permissões e Dashboards

```sql
CREATE TABLE usuarios (
    id              serial PRIMARY KEY,
    tenant_id       int           NOT NULL REFERENCES tenants(id),
    email           varchar(255)  NOT NULL,
    senha_hash      varchar(255)  NOT NULL,
    nome            varchar(200)  NOT NULL,
    role            varchar(20)   NOT NULL DEFAULT 'visualizador',  -- admin, gestor, analista, visualizador
    ativo           boolean       NOT NULL DEFAULT true,
    ultimo_login    timestamptz,
    criado_em       timestamptz   NOT NULL DEFAULT now(),
    UNIQUE (tenant_id, email)
);

CREATE TABLE permissoes_departamento (
    id              serial PRIMARY KEY,
    usuario_id      int           NOT NULL REFERENCES usuarios(id),
    departamento_id int           NOT NULL REFERENCES departamentos(id),
    pode_importar   boolean       NOT NULL DEFAULT false,
    pode_visualizar boolean       NOT NULL DEFAULT true,
    pode_exportar   boolean       NOT NULL DEFAULT false,
    UNIQUE (usuario_id, departamento_id)
);

CREATE TABLE dashboards (
    id          serial PRIMARY KEY,
    tenant_id   int           NOT NULL REFERENCES tenants(id),
    nome        varchar(200)  NOT NULL,
    slug        varchar(50)   NOT NULL,
    departamento_id int       REFERENCES departamentos(id),  -- null = multi-departamental
    ativo       boolean       NOT NULL DEFAULT true,
    UNIQUE (tenant_id, slug)
);

CREATE TABLE widgets (
    id              serial PRIMARY KEY,
    dashboard_id    int           NOT NULL REFERENCES dashboards(id) ON DELETE CASCADE,
    usuario_id      int           NOT NULL REFERENCES usuarios(id),
    tipo            varchar(50)   NOT NULL,  -- 'bar_chart', 'line_chart', 'pie_chart', 'kpi_card', 'data_table', 'heatmap'
    titulo          varchar(200),
    config          jsonb         NOT NULL,  -- endpoint, parametros, eixo x/y, cores, refresh_interval
    posicao_x       int           NOT NULL DEFAULT 0,
    posicao_y       int           NOT NULL DEFAULT 0,
    largura         int           NOT NULL DEFAULT 4,
    altura          int           NOT NULL DEFAULT 3,
    criado_em       timestamptz   NOT NULL DEFAULT now(),
    atualizado_em   timestamptz
);

CREATE TABLE exportacoes_agendadas (
    id              serial PRIMARY KEY,
    tenant_id       int           NOT NULL REFERENCES tenants(id),
    usuario_id      int           NOT NULL REFERENCES usuarios(id),
    dashboard_id    int           NOT NULL REFERENCES dashboards(id),
    formato         varchar(10)   NOT NULL DEFAULT 'pdf',   -- 'pdf', 'excel', 'csv'
    cron_expression varchar(50)   NOT NULL,                  -- '0 8 * * 1' (toda segunda 8h)
    destinatarios   jsonb,                                   -- lista de emails
    ativo           boolean       NOT NULL DEFAULT true,
    ultima_execucao timestamptz,
    criado_em       timestamptz   NOT NULL DEFAULT now()
);
```

---

## 4. Mecanismo de Templates e Processamento

### 4.1 Template de Importação (JSON Schema)

Cada departamento cadastra um schema que descreve as colunas esperadas no arquivo. O schema é versionado (`templates_importacao.versao`) para evolução sem quebra de lotes já processados.

Exemplo para **Compras de Grãos**:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "departamento": "compras",
  "versao": 1,
  "colunas": [
    {"nome": "data",           "tipo": "date",    "obrigatorio": true,  "formato": "DD/MM/YYYY"},
    {"nome": "fornecedor_cnpj","tipo": "string",  "obrigatorio": true,  "regex": "^\\d{14}$"},
    {"nome": "produto_codigo", "tipo": "string",  "obrigatorio": true},
    {"nome": "quantidade_sc",  "tipo": "float",   "obrigatorio": true,  "min": 0},
    {"nome": "valor_total",    "tipo": "float",   "obrigatorio": true,  "min": 0},
    {"nome": "safra",          "tipo": "string",  "obrigatorio": false}
  ],
  "mapeamento": {
    "fornecedor_cnpj":  {"entidade": "cliente_fornecedor", "campo_busca": "cnpj_cpf", "fk_destino": "cliente_fornecedor_id"},
    "produto_codigo":   {"entidade": "produto",            "campo_busca": "codigo",     "fk_destino": "produto_id"},
    "safra":            {"entidade": "safras",             "campo_busca": "codigo",     "fk_destino": "safra_id"}
  },
  "validacoes_customizadas": [
    {"regra": "valor_total / quantidade_sc <= 200", "mensagem": "Preço por saca excede R$ 200,00 — verificar"}
  ]
}
```

### 4.2 Pipeline de Regras (YAML)

Após a validação, o worker aplica um pipeline definido para o departamento. Cada step é atômico: se falhar no step N, os steps 1..(N-1) são preservados, e o erro é registrado no lote com o step exato que falhou.

```yaml
pipeline_contabil:
  steps:
    - validate_referencial:
        regras:
          - campo_arquivo: codigo_reduzido
            tabela_ref: plano_contas
            campo_ref: codigo_reduzido
            on_missing: error
          - campo_arquivo: centro_custo
            tabela_ref: centros_custo
            campo_ref: codigo
            on_missing: warn

    - transform:
        - add_column:
            nome: grupo_conta
            from: join(plano_contas, on=codigo_reduzido, select=grupo)
        - calcular:
            nome: saldo_movimento
            formula: |
              if natureza == "credora":
                  credito - debito
              else:
                  debito - credito

    - aggregate:
        - source: dados_transformados
          group_by: [data_competencia, centro_custo_id, grupo_conta]
          aggregations:
            saldo_total: sum(saldo_movimento)
            valor_debito: sum(debito)
            valor_credito: sum(credito)
          output: agregado_balancete

    - materialize:
        view: balancete_sintetico
        source: agregado_balancete
        refresh: on_commit   # ou 'scheduled' para views grandes
```

### 4.3 Motor de Execução (Polars + Celery)

```python
# Pseudocódigo do worker de processamento

class PipelineEngine:
    def __init__(self, pipeline_config: dict, template_schema: dict):
        self.steps = pipeline_config['steps']
        self.schema = template_schema

    def execute(self, file_path: str, lote_id: int, tenant_id: int) -> dict:
        # 1. Carregar arquivo em modo lazy/streaming (não carrega tudo em RAM)
        df = pl.scan_csv(file_path, schema_overrides=self._infer_dtypes())
            # ou pl.read_csv_batched() para streaming em chunks

        # 2. Para cada step do pipeline
        resultados_intermediarios = {}
        for step in self.steps:
            try:
                df = self._apply_step(step, df, resultados_intermediarios)
                resultados_intermediarios[step_name] = {'status': 'ok', 'rows': df.collect().height}
            except Exception as e:
                # Preserva steps anteriores, registra erro
                registrar_erro_lote(lote_id, step_name, str(e))
                raise PipelineStepError(step_name, e) from e

        # 3. Inserir resultados no banco em transação atômica
        with engine.begin() as conn:
            self._bulk_insert(conn, df, lote_id, tenant_id)
            self._registrar_linhagem(conn, lote_id)

        # 4. Refresh de materialized views
        self._refresh_views()

        return {'status': 'concluido', 'rows_processed': total}
```

### 4.4 Estratégia de Idempotência e Deduplicação

- Ao receber o arquivo, o sistema calcula `SHA-256` do conteúdo binário.
- Consulta `lotes_importacao` por `(tenant_id, hash_sha256)` — se existir com status `concluido`, retorna imediatamente o `lote_id` existente.
- Se existir com status `erro`, permite reenvio (novo `lote_id`).
- O hash garante que o mesmo arquivo não seja processado duas vezes.

### 4.5 Estratégia para Grandes Volumes

| Tamanho do arquivo | Estratégia                                   |
|--------------------|----------------------------------------------|
| < 100 MB           | Polars `read_csv` direto em memória          |
| 100 MB - 1 GB      | Polars `scan_csv` (lazy) + `collect()`       |
| > 1 GB             | `pl.read_csv_batched()` streaming em chunks  |
| > 10 GB            | Pré-processamento com `split` + processamento paralelo em múltiplos workers |

---

## 5. Dashboards de BI

### 5.1 Widget Registry (Catálogo de Componentes)

Cada tipo de widget é um componente React registrado no catálogo. Para adicionar um novo tipo, basta criar o componente e registrá-lo.

```typescript
// src/components/widgets/registry.ts
import { BarChartWidget } from './BarChartWidget';
import { LineChartWidget } from './LineChartWidget';
import { PieChartWidget }  from './PieChartWidget';
import { KPICardWidget }   from './KPICardWidget';
import { DataTableWidget } from './DataTableWidget';
import { HeatmapWidget }   from './HeatmapWidget';

export const widgetRegistry = {
  bar_chart:   BarChartWidget,
  line_chart:  LineChartWidget,
  pie_chart:   PieChartWidget,
  kpi_card:    KPICardWidget,
  data_table:  DataTableWidget,
  heatmap:     HeatmapWidget,
} as const;

export type WidgetType = keyof typeof widgetRegistry;
```

### 5.2 API de Dados para Widgets

Todos os widgets consomem endpoints padronizados. Cada endpoint aceita filtros dinâmicos e retorna dados prontos para renderização.

```
GET /api/v1/{tenant_slug}/bi/{departamento_slug}/{widget_endpoint}
  ?data_inicio=2024-01-01
  &data_fim=2024-12-31
  &centro_custo_id=1,2,3
  &produto_id=10
  &agrupamento=mensal
  ,refresh_cache=false
```

Resposta padronizada:

```json
{
  "widget_tipo": "bar_chart",
  "dados": {
    "categorias": ["Jan", "Fev", "Mar", ...],
    "series": [
      {"nome": "Receita", "valores": [100000, 120000, 110000, ...]},
      {"nome": "Despesa", "valores": [80000, 85000, 90000, ...]}
    ]
  },
  "metadata": {
    "atualizado_em": "2026-05-04T10:30:00Z",
    "total_registros": 1200,
    "cache_ttl": 300
  }
}
```

### 5.3 Cache Inteligente

- Redis armazena resultado de queries com TTL configurável por widget.
- Chave de cache: `cache:{tenant_id}:{widget_id}:{hash_dos_filtros}`.
- Invalidação seletiva: ao processar um novo lote, as chaves de cache relacionadas ao departamento/período são invalidadas.
- O frontend pode forçar refresh com `?refresh_cache=true`.

### 5.4 Exportação Agendada (Celery Beat)

- Usuário configura periodicidade (cron expression), formato (PDF/Excel/CSV) e lista de destinatários.
- Celery Beat dispara a task no horário agendado.
- A task gera o relatório, armazena no MinIO e envia link por email.
- Registro em `exportacoes_agendadas.ultima_execucao`.

---

## 6. Segurança e Governança

### 6.1 Autenticação (JWT)

- **Access token**: curta duração (15-30 min), enviado como `Authorization: Bearer <token>`.
- **Refresh token**: longa duração (7 dias), armazenado em cookie `httpOnly` + `secure` + `sameSite=strict`.
- **Rotação de refresh token**: ao usar um refresh token, o antigo é invalidado e um novo é emitido.
- **Blacklist**: tokens revogados (logout, troca de senha) são armazenados em Redis até expirarem.

### 6.2 Autorização (RBAC)

| Papel         | Permissões                                                                 |
|---------------|----------------------------------------------------------------------------|
| **admin**     | Acesso total ao tenant: CRUD templates, pipelines, dashboards, usuários    |
| **gestor**    | Visualizar + exportar todos os departamentos; ajustar parâmetros           |
| **analista**  | Importar + visualizar + exportar nos departamentos autorizados              |
| **visualizador** | Apenas visualizar dashboards nos departamentos autorizados               |

- Permissões de departamento refinadas via `permissoes_departamento`.
- Permissões de widget: um visualizador pode ver um dashboard mas não widgets específicos (ex.: dados financeiros sensíveis).
- Todos os endpoints validam `tenant_id` do token JWT contra o `tenant_slug` da URL.

### 6.3 Multi-Tenancy

- Todas as tabelas possuem `tenant_id`.
- PostgreSQL Row-Level Security (RLS) como camada adicional de segurança:

```sql
ALTER TABLE transacoes ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON transacoes
    USING (tenant_id = current_setting('app.current_tenant_id')::int);
```

- A aplicação define `app.current_tenant_id` no início de cada request autenticado.
- Índices são criados com `tenant_id` como primeira coluna para performance.

### 6.4 Auditoria

- Toda operação de escrita (importação, alteração de template, mudança de permissão, exportação de relatório) é registrada em `audit_log`.
- `audit_log.detalhes` armazena um snapshot JSON do estado antes/depois para operações de alteração.
- Logs são imutáveis — sem UPDATE ou DELETE na tabela de auditoria.
- Retenção configurável (ex.: 2 anos), com partições mensais para facilitar expurgo.

### 6.5 Rate Limiting

- Por tenant: máximo de requisições/minuto configurável.
- Por usuário: máximo de uploads/hora.
- Implementado via Redis (sliding window) no middleware do FastAPI.

---

## 7. Stack Tecnológica

| Camada                | Tecnologia                              | Versão Mínima   |
|-----------------------|-----------------------------------------|-----------------|
| Frontend              | React 18 + TypeScript + Ant Design 5    | 18.x / 5.x      |
| Gráficos              | Apache ECharts                          | 5.x             |
| Tabelas               | AG Grid Community                       | 31.x            |
| Backend API           | FastAPI + Pydantic v2                   | 0.110+ / 2.x    |
| Tarefas assíncronas   | Celery + Redis                          | 5.x / 7.x       |
| Tarefas agendadas     | Celery Beat + django-celery-beat        | -               |
| Processamento dados   | Polars (com engine calamine para XLSX)  | 1.x             |
| Banco relacional      | PostgreSQL                              | 16+             |
| Cache                 | Redis                                   | 7.x             |
| Mensageria/Pub-Sub    | Redis                                   | 7.x             |
| Armazenamento arquivos| MinIO (compatível S3)                   | latest          |
| Autenticação          | python-jose (JWT) + passlib (bcrypt)    | -               |
| Monitoramento         | Prometheus + Grafana + Flower (Celery)  | -               |
| Tracing               | OpenTelemetry (OTLP para Jaeger)        | -               |
| Logging               | Structlog (JSON estruturado)            | -               |
| Infraestrutura        | Docker, docker-compose (dev), Kubernetes (prod) | -          |

---

## 8. Estrutura de Projeto

```
/bi-agro-platform
  ├── backend/
  │   ├── app/
  │   │   ├── api/
  │   │   │   ├── __init__.py
  │   │   │   ├── deps.py               # Dependências FastAPI (DB session, current_user, current_tenant)
  │   │   │   └── v1/
  │   │   │       ├── __init__.py
  │   │   │       ├── router.py          # Inclusão de todos os routers v1
  │   │   │       ├── auth.py            # Login, refresh, logout
  │   │   │       ├── tenants.py         # CRUD tenants (admin global)
  │   │   │       ├── departamentos.py   # CRUD departamentos
  │   │   │       ├── templates.py       # CRUD templates de importação
  │   │   │       ├── pipelines.py       # CRUD pipelines
  │   │   │       ├── upload.py          # Upload de arquivos + polling de progresso
  │   │   │       ├── dashboards.py      # CRUD dashboards e widgets
  │   │   │       ├── bi.py              # Endpoints de dados para widgets
  │   │   │       ├── export.py          # Exportação de relatórios
  │   │   │       ├── usuarios.py        # Gestão de usuários e permissões
  │   │   │       └── dados_mestres.py   # CRUD plano_contas, centros_custo, produtos, etc.
  │   │   ├── core/
  │   │   │   ├── config.py             # Settings via pydantic-settings
  │   │   │   ├── security.py           # JWT, hash senha, RBAC decorators
  │   │   │   ├── database.py           # AsyncSession, engine
  │   │   │   └── middleware.py          # Rate limiting, tenant context, logging
  │   │   ├── models/                    # SQLAlchemy ORM models
  │   │   │   ├── base.py
  │   │   │   ├── tenant.py
  │   │   │   ├── departamento.py
  │   │   │   ├── plano_contas.py
  │   │   │   ├── transacao.py
  │   │   │   ├── lote.py
  │   │   │   ├── usuario.py
  │   │   │   └── dashboard.py
  │   │   ├── schemas/                   # Pydantic v2 schemas (request/response)
  │   │   ├── services/                  # Lógica de negócio
  │   │   │   ├── importacao_service.py
  │   │   │   ├── pipeline_service.py
  │   │   │   ├── dashboard_service.py
  │   │   │   ├── bi_service.py
  │   │   │   └── export_service.py
  │   │   ├── tasks/                     # Celery tasks
  │   │   │   ├── __init__.py            # celery_app factory
  │   │   │   ├── importacao.py          # Processa arquivo
  │   │   │   ├── exportacao.py          # Gera relatório agendado
  │   │   │   └── manutencao.py          # Refresh views, expurgo logs, criar partições
  │   │   ├── pipelines/                 # Engine de regras YAML
  │   │   │   ├── engine.py              # PipelineEngine
  │   │   │   ├── steps.py               # validate, transform, aggregate, materialize
  │   │   │   └── expressions.py         # Avaliador de expressões/fórmulas
  │   │   └── templates/                 # Schemas JSON de templates padrão
  │   ├── alembic/                       # Migrações de banco
  │   │   ├── versions/
  │   │   └── env.py
  │   ├── tests/
  │   │   ├── unit/
  │   │   │   ├── test_pipeline_engine.py
  │   │   │   ├── test_expressions.py
  │   │   │   └── test_security.py
  │   │   ├── integration/
  │   │   │   ├── test_upload_flow.py
  │   │   │   ├── test_bi_endpoints.py
  │   │   │   └── conftest.py
  │   │   └── fixtures/
  │   │       ├── contabilidade.csv
  │   │       └── compras_graos.xlsx
  │   ├── requirements.txt
  │   ├── Dockerfile
  │   └── Dockerfile.worker
  ├── frontend/
  │   ├── src/
  │   │   ├── components/
  │   │   │   ├── widgets/               # Catálogo de widgets + registry
  │   │   │   │   ├── registry.ts
  │   │   │   │   ├── WidgetRenderer.tsx
  │   │   │   │   ├── BarChartWidget.tsx
  │   │   │   │   ├── LineChartWidget.tsx
  │   │   │   │   ├── PieChartWidget.tsx
  │   │   │   │   ├── KPICardWidget.tsx
  │   │   │   │   ├── DataTableWidget.tsx
  │   │   │   │   └── HeatmapWidget.tsx
  │   │   │   ├── layout/
  │   │   │   │   ├── AppLayout.tsx
  │   │   │   │   ├── Sidebar.tsx
  │   │   │   │   └── Header.tsx
  │   │   │   ├── upload/
  │   │   │   │   ├── FileUploader.tsx
  │   │   │   │   └── ProgressBar.tsx
  │   │   │   └── common/
  │   │   │       ├── FiltroPeriodo.tsx
  │   │   │       └── FiltroDinamico.tsx
  │   │   ├── pages/
  │   │   │   ├── Login.tsx
  │   │   │   ├── DashboardPage.tsx       # Renderiza layout de widgets do usuário
  │   │   │   ├── Departamentos/
  │   │   │   │   ├── Contabil.tsx
  │   │   │   │   ├── Financeiro.tsx
  │   │   │   │   ├── Vendas.tsx
  │   │   │   │   ├── Compras.tsx
  │   │   │   │   ├── Producao.tsx
  │   │   │   │   └── Logistica.tsx
  │   │   │   ├── Importacao.tsx           # Upload + progresso
  │   │   │   ├── Admin/
  │   │   │   │   ├── Templates.tsx
  │   │   │   │   ├── Pipelines.tsx
  │   │   │   │   ├── Usuarios.tsx
  │   │   │   │   └── DadosMestres.tsx
  │   │   │   └── Exportacao.tsx
  │   │   ├── hooks/
  │   │   │   ├── useAuth.ts
  │   │   │   ├── useWidgetData.ts
  │   │   │   └── useUploadProgress.ts
  │   │   ├── services/
  │   │   │   ├── api.ts                   # Axios instance com interceptors JWT
  │   │   │   ├── authService.ts
  │   │   │   ├── biService.ts
  │   │   │   ├── uploadService.ts
  │   │   │   └── dashboardService.ts
  │   │   ├── store/                       # Zustand ou Redux Toolkit
  │   │   │   ├── authStore.ts
  │   │   │   ├── tenantStore.ts
  │   │   │   └── dashboardStore.ts
  │   │   ├── utils/
  │   │   └── App.tsx
  │   ├── tests/
  │   │   ├── components/
  │   │   └── e2e/                         # Playwright
  │   ├── package.json
  │   ├── tsconfig.json
  │   ├── vite.config.ts
  │   └── Dockerfile
  ├── docker/
  │   ├── docker-compose.yml
  │   ├── docker-compose.prod.yml
  │   ├── nginx/
  │   │   └── nginx.conf
  │   └── postgres/
  │       └── init.sql                     # Criação inicial de tenants e departments
  └── docs/
      ├── README.md
      ├── api.md                           # Documentação da API (OpenAPI extendido)
      ├── modelagem.md                     # DER e explicação das decisões de modelagem
      └── deploy.md                        # Guia de deploy
```

---

## 9. Infraestrutura e Observabilidade

### 9.1 Ambientes

| Ambiente   | Infra                            | Finalidade                        |
|------------|----------------------------------|-----------------------------------|
| **Dev**    | docker-compose (tudo local)      | Desenvolvimento e testes          |
| **Homolog**| Kubernetes (cluster dedicado)    | Validação pré-produção            |
| **Prod**   | Kubernetes (cluster gerenciado)  | Produção com HA                   |

### 9.2 docker-compose.yml (Desenvolvimento)

Serviços: `postgres`, `redis`, `minio`, `api`, `worker`, `worker-beat`, `flower`, `frontend`, `nginx`.

### 9.3 Observabilidade

- **Logging**: Structlog em JSON estruturado — cada log carrega `tenant_id`, `usuario_id`, `correlation_id`, `endpoint`.
- **Métricas**: Prometheus coleta métricas de:
  - FastAPI (tempo de resposta, taxa de erros, requests por endpoint).
  - Celery (tasks concluídas, falhas, tempo médio, tamanho da fila).
  - PostgreSQL (conexões ativas, queries lentas).
- **Tracing**: OpenTelemetry instrumenta FastAPI + Celery + SQLAlchemy. Spans exportados para Jaeger.
- **Alertas**: Grafana alerta quando fila Celery > N tarefas, taxa de erro > X%, ou disco > Y%.
- **Health checks**: endpoints `/health/live` (liveness) e `/health/ready` (readiness) para Kubernetes.

### 9.4 Backup e Disaster Recovery

- **PostgreSQL**: `pg_dump` diário + WAL archiving contínuo para point-in-time recovery.
- **MinIO**: replicação entre buckets (ou snapshots periódicos).
- **Retenção**: 30 dias de backups diários, 12 meses de backups mensais.
- **Teste de restore**: automatizado mensalmente.

### 9.5 CI/CD (GitHub Actions)

- **PR → main**: lint, typecheck, testes unitários + integração, build de imagem Docker.
- **Merge → main**: deploy automático em homologação.
- **Tag → prod**: deploy manual após aprovação.

---

## 10. Roadmap de Implementação

### Sprint 1: Fundação (Semanas 1-2)
- [ ] Setup docker-compose (PostgreSQL, Redis, MinIO, API, Worker, Frontend)
- [ ] FastAPI com estrutura modular, config, health checks, logs estruturados
- [ ] Migração inicial: tenants, departamentos, plano_contas, centros_custo, produtos
- [ ] Autenticação JWT (login, refresh, logout, middleware de tenant)
- [ ] RBAC básico (papéis e middleware de autorização)
- [ ] Frontend: AppLayout com Sidebar + Header, tela de Login
- [ ] Testes unitários iniciais (auth, security)

### Sprint 2: Importação e Processamento (Semanas 3-4)
- [ ] CRUD de templates de importação e pipelines (API + admin frontend)
- [ ] Upload de arquivo (frontend com progresso WebSocket/Pub-Sub)
- [ ] Armazenamento no MinIO + cálculo de hash SHA-256
- [ ] Worker Celery: validação contra template JSON Schema
- [ ] Pipeline Engine: steps de validate, transform (join com dados mestres)
- [ ] Inserção em lote com transação atômica + linhagem
- [ ] Pipeline contábil funcional: CSV → balancete
- [ ] Testes de integração do fluxo completo de upload

### Sprint 3: Dashboards Iniciais — Contabilidade (Semanas 5-6)
- [ ] Endpoints BI para contabilidade (balancete, DRE, razão)
- [ ] Widget Registry: gráfico de barras, linha, KPI card, tabela de dados
- [ ] Dashboard contábil com layout persistido por usuário
- [ ] Filtros de período e centro de custo
- [ ] Cache Redis com invalidação por lote
- [ ] Testes E2E (Playwright) do dashboard contábil

### Sprint 4: Expansão Multi-Departamental (Semanas 7-8)
- [ ] Templates para vendas, compras e produção de grãos
- [ ] Pipelines YAML completos para cada novo departamento
- [ ] Dashboards configuráveis por departamento (abas com widgets específicos)
- [ ] Drill-down nos gráficos (ex.: do total anual para mensal para diário)
- [ ] Exportação manual de relatórios (PDF + Excel)

### Sprint 5: Segurança, Auditoria e Multi-Tenancy (Semanas 9-10)
- [ ] Row-Level Security no PostgreSQL
- [ ] Auditoria completa (`audit_log` em todas as operações sensíveis)
- [ ] Rate limiting por tenant e usuário
- [ ] Permissões granulares por departamento e widget
- [ ] Isolamento de tenants no MinIO (buckets por tenant)

### Sprint 6: Escalabilidade, Observabilidade e Produção (Semanas 11-12)
- [ ] Prometheus + Grafana + dashboards operacionais
- [ ] OpenTelemetry tracing (Jaeger)
- [ ] Particionamento automático de `transacoes` (criação mensal)
- [ ] Exportação agendada (Celery Beat)
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Testes de carga (Locust) e ajustes de performance
- [ ] Documentação de deploy e operação

---

## 11. Considerações Finais

A plataforma foi projetada desde o início para ser um **hub de dados multi-tenant do agronegócio**, unificando informações de diferentes setores em um único local com isolamento e segurança.

**Decisões arquiteturais fundamentais:**

- **Type Table Pattern** com FKs explícitas substitui a abordagem genérica `entidade_tipo`/`entidade_id`, garantindo integridade referencial real e índices eficientes.
- **Particionamento nativo** desde a Sprint 1 evita migrações dolorosas no futuro.
- **Hash SHA-256** como chave de idempotência elimina processamento duplicado sem depender do nome do arquivo.
- **Pipeline atômico com preservação de steps** facilita debug e retry seletivo.
- **Polars lazy/streaming** permite processar arquivos de qualquer tamanho sem escalar RAM.
- **Widget Registry + layout persistido** dá flexibilidade ao usuário final sem código customizado.
- **Multi-tenancy com RLS** garante que um bug de aplicação jamais vaze dados entre tenants.
- **Observabilidade desde o Dia 1** (logs estruturados + métricas + tracing) evita o cenário de "caixa preta em produção".

A abordagem de templates e pipelines permite que novos departamentos sejam adicionados sem alterações no código core — apenas configurando schemas de importação e regras de negócio em YAML.

Este documento serve como guia arquitetural para o desenvolvimento. Qualquer dúvida ou necessidade de detalhamento de uma seção específica, estou à disposição.
