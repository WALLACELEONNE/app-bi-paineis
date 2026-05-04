# Fluxograma Completo: Do Cadastro à Visualização

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                           BI AGRO PLATFORM — FLUXO COMPLETO                        │
└──────────────────────────────────────────────────────────────────────────────────┘

 PASSO 1                    PASSO 2                   PASSO 3
 ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────────┐
 │  DADOS MESTRES  │       │    TEMPLATES     │       │     PIPELINES       │
 │                 │       │                 │       │                     │
 │ • Plano Contas  │──────▶│ Schema JSON     │──────▶│ Regras YAML         │
 │ • Centros Custo │       │ (colunas do     │       │ (o que fazer com    │
 │ • Produtos      │       │  arquivo CSV)   │       │  os dados)          │
 │ • Clientes/For. │       │                 │       │                     │
 │ • Fazendas      │       │ Ex: data,       │       │ Ex: calcular saldo, │
 │ • Armazéns      │       │ debito, credito,│       │ agrupar por mês,    │
 │ • Safras        │       │ valor           │       │ somar valores       │
 └────────┬────────┘       └────────┬────────┘       └──────────┬──────────┘
          │                         │                           │
          │          ┌──────────────┴────────────┐              │
          │          │                           │              │
          ▼          ▼                           ▼              │
       ┌────────────────────────────────────────────────┐       │
       │              PASSO 4: IMPORTAÇÃO                │       │
       │                                                │       │
       │  1. Selecione o TEMPLATE (define colunas)      │       │
       │  2. Selecione o PIPELINE (define regras)       │◄──────┘
       │  3. Arraste o arquivo CSV/XLSX                 │
       │  4. Clique em PROCESSAR ARQUIVO                │
       │                                                │
       │  ┌──────────┐    ┌──────────┐    ┌──────────┐ │
       │  │ Validação │───▶│Transform.│───▶│Insert BD │ │
       │  │ (schema)  │    │ (YAML)   │    │(transacoes)│
       │  └──────────┘    └──────────┘    └──────────┘ │
       └───────────────────────┬────────────────────────┘
                               │
                               ▼
       ┌────────────────────────────────────────────────┐
       │           PASSO 5: DASHBOARD / BI               │
       │                                                │
       │  • Adicione widgets (KPI, Barras, Pizza...)   │
       │  • Aplique filtros (data, departamento)        │
       │  • Visualize gráficos em tempo real            │
       │  • Exporte para Excel                          │
       └────────────────────────────────────────────────┘
```

---

## Guia Passo a Passo: Exemplo Completo com Vendas de Grãos

Vamos seguir um cenário real: **importar vendas de grãos e visualizar no dashboard**.

---

### PASSO 1: Cadastrar Dados Mestres

> **Menu:** Administração → Dados Mestres → cada aba

Antes de importar qualquer coisa, cadastre as entidades de referência:

#### 1a. Clientes/Fornecedores
```
Aba: Clientes/Fornecedores → Novo
  Tenant ID:        1
  Tipo:             C
  Razão Social:     AgroComercial Ltda
  CNPJ/CPF:         12345678000199
```

```
  Tenant ID:        1
  Tipo:             C
  Razão Social:     Cooperativa Grãos Brasil
  CNPJ/CPF:         98765432000188
```

#### 1b. Produtos
```
Aba: Produtos → Novo
  Tenant ID:        1
  Código:           SOJA-001
  Nome:             Soja Grão Tipo 1
  Tipo:             grao
  Unidade:          sc
  Cultura:          soja
```

```
  Tenant ID:        1
  Código:           MILHO-001
  Nome:             Milho Grão
  Tipo:             grao
  Unidade:          sc
  Cultura:          milho
```

#### 1c. Safras
```
Aba: Safras → Novo
  Tenant ID:        1
  Código:           23/24
  Ano Início:       2023
  Ano Fim:          2024
```

#### 1d. Fazendas (opcional)
```
Aba: Fazendas → Novo
  Tenant ID:        1
  Código:           FAZ001
  Nome:             Fazenda Boa Vista
  Município:        Rio Verde
  UF:               GO
```

---

### PASSO 2: Criar Template de Importação

> **Menu:** Administração → Templates → Novo

O template define **QUAIS colunas** o sistema espera no arquivo CSV.

**Exemplo para Vendas de Grãos:**

```
  Tenant ID:        1
  Departamento ID:  3    ← Vendas (ver tabela de departamentos abaixo)
  Nome:             Template de Vendas de Grãos
  Schema (JSON):    (colar o JSON abaixo)
```

**JSON Schema para Vendas:**

```json
{
  "colunas": [
    {"nome": "data",           "tipo": "date",   "obrigatorio": true},
    {"nome": "cliente_cnpj",   "tipo": "string", "obrigatorio": true},
    {"nome": "produto_codigo", "tipo": "string", "obrigatorio": true},
    {"nome": "fazenda_codigo", "tipo": "string", "obrigatorio": false},
    {"nome": "safra",          "tipo": "string", "obrigatorio": false},
    {"nome": "quantidade_sc",  "tipo": "float",  "obrigatorio": true, "min": 0},
    {"nome": "valor_total",    "tipo": "float",  "obrigatorio": true, "min": 0}
  ],
  "mapeamento": {
    "cliente_cnpj":   {"entidade": "clientes_fornecedores", "campo_busca": "cnpj_cpf", "fk_destino": "cliente_fornecedor_id"},
    "produto_codigo": {"entidade": "produtos",              "campo_busca": "codigo",    "fk_destino": "produto_id"},
    "fazenda_codigo": {"entidade": "fazendas",             "campo_busca": "codigo",    "fk_destino": "fazenda_id"},
    "safra":          {"entidade": "safras",               "campo_busca": "codigo",    "fk_destino": "safra_id"}
  },
  "validacoes_customizadas": [
    {"regra": "valor_total / quantidade_sc <= 200", "mensagem": "Preço por saca acima de R$ 200 — verificar"}
  ]
}
```

> **Tabela de Departamentos:** 1=Contabilidade, 2=Financeiro, 3=Vendas, 4=Compras, 5=Produção, 6=Logística

---

### PASSO 3: Criar Pipeline de Processamento

> **Menu:** Administração → Pipelines → Novo

O pipeline define **O QUE FAZER** com os dados após a validação.

```
  Tenant ID:        1
  Departamento ID:  3    ← Vendas
  Nome:             Pipeline de Vendas de Grãos
  Config (YAML):    (colar o YAML abaixo)
```

**YAML para Vendas:**

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

### PASSO 4: Preparar e Importar Arquivo CSV

Crie um arquivo `vendas_graos.csv` com o conteúdo:

```csv
data,cliente_cnpj,produto_codigo,fazenda_codigo,safra,quantidade_sc,valor_total
2024-01-15,12345678000199,SOJA-001,FAZ001,23/24,500,75000
2024-01-20,98765432000188,SOJA-001,,23/24,300,46500
2024-02-10,12345678000199,MILHO-001,,23/24,800,64000
2024-02-15,98765432000188,SOJA-001,FAZ001,23/24,200,31000
2024-03-01,12345678000199,MILHO-001,,23/24,600,48000
```

> **Menu:** Importação

| Campo | Valor |
|---|---|
| **Template** | Template de Vendas de Grãos (v1) |
| **Pipeline** | Pipeline de Vendas de Grãos (v1) |
| **Arquivo** | Arraste `vendas_graos.csv` para a área pontilhada |
| **Ação** | Clique em **Processar Arquivo** |

Aguarde ~2 segundos. O status mudará para **concluído** com 5 linhas OK.

---

### PASSO 5: Visualizar no Dashboard

> **Menu:** Vendas (menu lateral)

#### 5a. Aplicar filtros
- No seletor **Departamento**, escolha "Vendas"
- No seletor de **Período**, escolha 01/01/2024 a 31/12/2024

#### 5b. Adicionar Widgets

Clique em **+ Widget** e adicione nesta ordem:

| # | Widget | Endpoint | O que mostra |
|---|--------|----------|-------------|
| 1 | **Cartão KPI** | `kpi` | Valor total de vendas (R$ 264.500) |
| 2 | **Gráfico de Barras** | `series_temporal` | Vendas por mês (Jan: R$ 121.500, Fev: R$ 95.000, Mar: R$ 48.000) |
| 3 | **Gráfico de Pizza** | `por_departamento` | Distribuição por departamento (Vendas = 100%) |
| 4 | **Tabela de Dados** | `tabela` | Lista detalhada de cada venda |

#### 5c. Interagir com os Widgets

- Passe o mouse sobre as barras para ver valores detalhados
- Altere o período para filtrar por mês específico
- Remova widgets que não precisa (ícone 🗑️)
- Recarregue com o botão **Atualizar**

---

## Resumo Visual da Relação entre os Componentes

```
                         ┌────────────────────────┐
                         │     ADMINISTRAÇÃO       │
                         │                        │
            ┌────────────┤ 1. Dados Mestres        │
            │            │    ↓                    │
            │            │ 2. Templates (JSON)     │
            │            │    ↓                    │
            │            │ 3. Pipelines (YAML)     │
            │            │    ↓                    │
            │            │ 4. Usuários             │
            │            └────────────┬───────────┘
            │                         │
            │  ┌──────────────────────┘
            │  │  Templates + Pipelines são usados na importação
            ▼  ▼
┌────────────────────────┐      ┌────────────────────────┐
│      IMPORTAÇÃO        │      │     DASHBOARD / BI      │
│                        │      │                        │
│ Upload CSV/XLSX ───────┼─────▶│ Widgets consultam      │
│   ↓                    │      │ transacoes e exibem:   │
│ Validação (Template)   │      │                        │
│   ↓                    │      │ • KPI (valor total)    │
│ Transform (Pipeline)   │      │ • Barras (mensal)      │
│   ↓                    │      │ • Pizza (depto)        │
│ INSERT INTO transacoes │      │ • Tabela (detalhes)    │
│                        │      │ • Linha (tendência)    │
│ Status: concluído ✓    │      │ • Heatmap (intensidade)│
└────────────────────────┘      └────────────────────────┘
```

---

## Dúvidas Comuns

**P: Preciso cadastrar TODOS os dados mestres antes?**
R: Não. Cadastre apenas o que seu arquivo CSV referencia. Se o CSV tem `cliente_cnpj`, cadastre clientes. Se não tem `fazenda_codigo`, não precisa cadastrar fazendas.

**P: Posso usar o mesmo template para vários departamentos?**
R: Cada template está vinculado a um departamento. Se Vendas e Compras usam colunas diferentes, crie templates separados.

**P: O pipeline é obrigatório?**
R: Sim. No mínimo, use um pipeline com apenas o step `validate`. Sem pipeline, o sistema não sabe o que fazer com os dados.

**P: Onde os dados ficam armazenados?**
R: Na tabela `transacoes`, particionada por mês (`transacoes_2024_01`, `transacoes_2024_02`, etc.).

**P: Como criar um pipeline que só insere os dados sem transformar?**
R: Use este YAML mínimo:
```yaml
pipeline_basico:
  steps:
    - validate:
        regras: []
```

---

## Checklist: Novo Departamento (ex: Logística)

Para adicionar um novo módulo de operação, siga esta ordem:

- [ ] **1. Dados Mestres:** Cadastrar armazéns, produtos, veículos (se aplicável)
- [ ] **2. Template:** Criar JSON Schema com as colunas do arquivo de logística
- [ ] **3. Pipeline:** Criar YAML com regras de transformação (ex: calcular frete médio)
- [ ] **4. Importar:** Upload do CSV de fretes/entregas
- [ ] **5. Dashboard:** Adicionar widgets de BI no menu Logística
