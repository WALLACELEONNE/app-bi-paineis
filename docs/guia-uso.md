# BI Agro Platform — Guia de Uso

**Versão:** 1.0.0 | **Acesso:** http://localhost:5173
**Login padrão:** `admin@biagro.com.br` / `admin123`

---

## Índice

1. [Módulo de Administração](#1-módulo-de-administração)
   - Dados Mestres (Plano de Contas, Centros de Custo, Produtos, Clientes/Fornecedores, Fazendas, Armazéns, Safras)
   - Templates de Importação
   - Pipelines de Processamento
   - Gestão de Usuários
2. [Módulo de Importação](#2-módulo-de-importação)
   - Criar um Template
   - Criar um Pipeline
   - Upload de Arquivo
   - Consultar Histórico
3. [Módulo de Contabilidade (Operação)](#3-módulo-de-contabilidade)
   - Visão Geral
   - Dashboard Contábil
   - Adicionar Widgets
   - Exportar Dados
4. [Solução de Problemas](#4-solução-de-problemas)

---

## 1. Módulo de Administração

Acesse pelo menu lateral: **Administração**. A tela possui 4 abas.

### 1.1 Dados Mestres

Aqui você cadastra as entidades de negócio usadas por todos os módulos.

#### Plano de Contas
Utilize como base o **Tran447** ou seu plano contábil próprio.

| Como fazer | Passos |
|---|---|
| **Listar** | A aba já carrega todos os registros |
| **Criar** | Clique `Novo` → preencha os campos → confirme |
| **Editar** | Clique no ícone ✏️ na linha → altere → confirme |
| **Remover** | Clique no ícone 🗑️ → confirme a exclusão |

**Campos importantes:**
- `Código Reduzido`: ex: `1.1.1.01.001`
- `Descrição`: ex: `Caixa Geral`
- `Nível`: 1 a 5 (nível hierárquico)
- `Natureza`: `credora` ou `devedora`
- `Grupo`: `Ativo`, `Passivo`, `Receita`, `Despesa`

#### Centros de Custo
Cadastre centros de custo como `CC001 - Administrativo`, `CC002 - Comercial Grãos`, `CC003 - Logística`.

#### Produtos
Cadastre grãos, insumos e serviços.

| Campo | Exemplo |
|---|---|
| `Código` | `SOJA-001` |
| `Nome` | `Soja Grão Tipo 1` |
| `Tipo` | `grao`, `insumo` ou `servico` |
| `Unidade` | `sc` (saca), `ton` (tonelada), `kg`, `lt` |
| `Cultura` | `soja`, `milho`, `trigo` |

#### Clientes/Fornecedores
- `Tipo`: `C` (cliente), `F` (fornecedor), `A` (ambos)
- `CNPJ/CPF`: apenas números, 11 ou 14 dígitos

#### Fazendas, Armazéns, Safras
Cadastre conforme necessidade. Safras usam formato `24/25`.

---

### 1.2 Templates de Importação

Templates definem **quais colunas** o sistema espera no arquivo CSV/XLSX e como validá-las.

#### Criar um Template

1. Acesse a aba **Templates**
2. Clique `Novo`
3. Preencha:
   - `Tenant ID`: `1`
   - `Departamento ID`: `1` (Contabilidade), `3` (Vendas), etc.
   - `Nome`: ex: `Template Contábil CSV`
   - `Schema (JSON)`: a estrutura das colunas (ver exemplo abaixo)
4. Confirme

**Exemplo de Schema JSON para Contabilidade:**

```json
{
  "colunas": [
    {"nome": "data",               "tipo": "date",   "obrigatorio": true,  "formato": "DD/MM/YYYY"},
    {"nome": "descricao",          "tipo": "string", "obrigatorio": false},
    {"nome": "centro_custo_codigo","tipo": "string", "obrigatorio": false},
    {"nome": "debito",             "tipo": "float",  "obrigatorio": false,  "min": 0},
    {"nome": "credito",            "tipo": "float",  "obrigatorio": false,  "min": 0},
    {"nome": "valor",              "tipo": "float",  "obrigatorio": true,   "min": 0}
  ],
  "mapeamento": {
    "centro_custo_codigo": {"entidade": "centros_custo", "campo_busca": "codigo", "fk_destino": "centro_custo_id"}
  },
  "validacoes_customizadas": []
}
```

**Exemplo para Vendas de Grãos:**

```json
{
  "colunas": [
    {"nome": "data",            "tipo": "date",   "obrigatorio": true},
    {"nome": "cliente_cnpj",    "tipo": "string", "obrigatorio": true},
    {"nome": "produto_codigo",  "tipo": "string", "obrigatorio": true},
    {"nome": "quantidade_sc",   "tipo": "float",  "obrigatorio": true, "min": 0},
    {"nome": "valor_total",     "tipo": "float",  "obrigatorio": true, "min": 0},
    {"nome": "safra",           "tipo": "string", "obrigatorio": false}
  ],
  "mapeamento": {
    "cliente_cnpj":   {"entidade": "clientes_fornecedores", "campo_busca": "cnpj_cpf", "fk_destino": "cliente_fornecedor_id"},
    "produto_codigo": {"entidade": "produtos",              "campo_busca": "codigo",    "fk_destino": "produto_id"},
    "safra":          {"entidade": "safras",               "campo_busca": "codigo",    "fk_destino": "safra_id"}
  }
}
```

---

### 1.3 Pipelines de Processamento

Pipelines definem **o que fazer** com os dados após a validação: transformações, cálculos e agregações.

#### Criar um Pipeline

1. Acesse a aba **Pipelines**
2. Clique `Novo`
3. Preencha:
   - `Tenant ID`: `1`
   - `Departamento ID`: mesmo do template
   - `Nome`: ex: `Pipeline Contábil`
   - `Configuração (YAML)`: as regras de processamento
4. Confirme

**Exemplo para Contabilidade:**

```yaml
pipeline_contabil:
  steps:
    - validate:
        regras: []
    - transform:
        - calcular:
            nome: saldo_movimento
            formula: "credito - debito"
```

**Exemplo para Vendas (com agregação):**

```yaml
pipeline_vendas:
  steps:
    - validate:
        regras: []
    - transform:
        - calcular:
            nome: preco_medio_saca
            formula: "valor_total / quantidade_sc"
    - aggregate:
        - group_by: [produto_codigo, data]
          aggregations:
            volume_total: "sum(quantidade_sc)"
            receita_total: "sum(valor_total)"
```

---

### 1.4 Gestão de Usuários

Acesse a aba **Usuários** (requer role `admin`).

| Papel (role) | Permissões |
|---|---|
| `admin` | Acesso total: CRUD em todos os módulos, gestão de usuários |
| `gestor` | Visualizar e exportar todos os departamentos |
| `analista` | Importar, visualizar e exportar nos departamentos autorizados |
| `visualizador` | Apenas visualizar dashboards |

**Para criar um usuário:** Clique `Novo` → preencha nome, email, senha, role → confirme.

---

## 2. Módulo de Importação

Acesse pelo menu lateral: **Importação**.

### 2.1 Pré-requisitos

Antes de importar, você precisa ter:
1. Um **Template** cadastrado (Administração → Templates)
2. Um **Pipeline** cadastrado (Administração → Pipelines)
3. Um arquivo **CSV** com encoding UTF-8

### 2.2 Formato do Arquivo CSV

O arquivo deve ter cabeçalho com os nomes das colunas iguais aos definidos no template.

**Exemplo `contabilidade.csv`:**
```csv
data,descricao,centro_custo_codigo,debito,credito,valor
2024-01-15,Compra de sementes,CC001,15000,0,15000
2024-01-20,Venda de soja,CC002,0,50000,50000
2024-02-10,Fertilizantes,CC001,8000,0,8000
2024-03-01,Venda de milho,CC002,0,35000,35000
```

### 2.3 Fluxo de Importação

| Passo | Ação |
|---|---|
| 1 | Selecione o **Template** no dropdown |
| 2 | Selecione o **Pipeline** no dropdown |
| 3 | Arraste o arquivo CSV para a área pontilhada ou clique para selecionar |
| 4 | Clique em **Processar Arquivo** |
| 5 | Aguarde — o processamento leva de 2 a 10 segundos |
| 6 | O status muda para **concluído** quando terminar |

**Status possíveis:**
- `pendente` — aguardando na fila
- `processando` — sendo processado pelo worker
- `concluido` — processado com sucesso (exibe linhas OK/erro)
- `erro` — falha no processamento (exibe mensagem de erro)

### 2.4 Idempotência

O sistema detecta **arquivos duplicados** pelo hash SHA-256. Se você enviar o mesmo arquivo duas vezes, a segunda tentativa será ignorada (retorna o lote já processado). Para reprocessar, altere o conteúdo do arquivo.

### 2.5 Histórico

A tabela na parte inferior mostra todos os lotes já enviados, com status, quantidade de linhas e data.

---

## 3. Módulo de Contabilidade

Acesse pelo menu lateral: **Contabilidade**.

### 3.1 Visão Geral

O dashboard contábil exibe widgets de BI alimentados pelos dados importados. Para começar:

1. **Importe dados** (módulo Importação) usando o template e pipeline contábil
2. Acesse **Contabilidade** no menu lateral
3. Adicione widgets para visualizar os dados

### 3.2 Dashboard Contábil

#### Filtros Globais

No topo da página você encontra:

| Filtro | Descrição |
|---|---|
| **Período** | Seletor de data inicial e final |
| **Departamento** | Filtra por departamento (Contabilidade = ID 1) |
| **Atualizar** | Recarrega todos os widgets |

> **Dica:** Os filtros globais são aplicados automaticamente a todos os widgets do dashboard.

#### Adicionar Widgets

1. Clique no botão **+ Widget**
2. Selecione o tipo de widget no modal:

| Widget | Indicado para | Endpoint |
|---|---|---|
| **Cartão KPI** | Valor total, quantidade de registros | `/bi/kpi` |
| **Gráfico de Barras** | Evolução mensal de receitas/despesas | `/bi/series_temporal` |
| **Gráfico de Linha** | Tendências ao longo do tempo | `/bi/series_temporal` |
| **Gráfico de Pizza** | Distribuição por departamento | `/bi/por_departamento` |
| **Tabela de Dados** | Listagem detalhada de lançamentos | `/bi/tabela` |
| **Mapa de Calor** | Intensidade por período x categoria | `/bi/heatmap` |

3. Confirme — o widget aparece no grid
4. Para remover, clique no ícone 🗑️ no canto do widget

### 3.3 Exemplo Prático: Balancete Contábil

**Objetivo:** Visualizar a evolução mensal do saldo contábil.

1. Importe o arquivo `contabilidade.csv` (módulo Importação)
2. Acesse **Contabilidade**
3. Adicione um **Cartão KPI** → mostra o valor total (ex: R$ 108.000)
4. Adicione um **Gráfico de Barras** → mostra barras por mês (Jan: R$ 65.000, Fev: R$ 8.000, Mar: R$ 35.000)
5. Adicione uma **Tabela de Dados** → lista detalhada dos lançamentos (data, valor, departamento)

### 3.4 Exportar Dados

Para exportar os dados filtrados para Excel:

1. No dashboard, ajuste os filtros de período e departamento
2. Acesse **API** diretamente: `GET /api/v1/export/excel?data_inicio=2024-01-01&data_fim=2024-12-31`
3. O arquivo `transacoes.xlsx` será baixado

> No futuro, um botão de exportação estará disponível diretamente no dashboard.

---

## 4. Solução de Problemas

| Problema | Causa Provável | Solução |
|---|---|---|
| Template/Pipeline não aparece no dropdown | Não foi cadastrado ou está inativo | Administração → Templates/Pipelines → verificar |
| Upload fica em `pendente` | Worker Celery não está rodando | `docker compose ps` → verificar `bi_worker` |
| Upload fica em `erro` | Arquivo não corresponde ao template | Verificar nomes das colunas no CSV vs JSON Schema |
| Dashboard mostra "Nenhum widget" | Nenhum widget foi adicionado | Clique em **+ Widget** |
| Widget mostra "Sem dados" | Filtros muito restritivos ou sem dados importados | Ajustar filtros de data ou importar dados primeiro |
| Erro `429 Too Many Requests` | Muitas requisições em curto período | Aguardar 60 segundos |
| Botão "Processar Arquivo" desabilitado | Falta selecionar template, pipeline ou arquivo | Preencher todos os campos |
| Página não carrega | Frontend ainda iniciando | Aguardar 5 segundos e recarregar (F5) |

---

## Comandos Rápidos (Docker)

```bash
# Verificar todos os serviços
docker compose ps

# Reiniciar um serviço específico
docker compose restart api
docker compose restart worker
docker compose restart frontend

# Ver logs em tempo real
docker compose logs -f api
docker compose logs -f worker

# Resetar dados de teste
docker compose down -v && docker compose up -d
```

---

## Acessos

| Serviço | URL | Credenciais |
|---|---|---|
| **Frontend** | http://localhost:5173 | `admin@biagro.com.br` / `admin123` |
| **API Swagger** | http://localhost:8000/api/docs | Usar token JWT do login |
| **MinIO Console** | http://localhost:9001 | `minio_admin` / `minio_secret_dev` |
| **Flower (Celery)** | http://localhost:5555 | `admin` / `flower_dev` |
