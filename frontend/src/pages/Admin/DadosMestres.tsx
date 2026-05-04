import { useState } from 'react'
import { Tabs, Card } from 'antd'
import CrudTable from '../../components/common/CrudTable'
import CsvImportButton from '../../components/common/CsvImportButton'

export default function DadosMestres() {
  const [refreshKey, setRefreshKey] = useState(0)
  const refresh = () => setRefreshKey(k => k + 1)

  const tab = (key: string, label: string, endpoint: string, title: string, columns: any[], formFields: any[], entity: string) => ({
    key, label,
    children: (
      <div>
        <div style={{ marginBottom: 8 }}>
          <CsvImportButton entity={entity} onImported={refresh} />
        </div>
        <CrudTable key={`${key}-${refreshKey}`} endpoint={endpoint} title={title} columns={columns} formFields={formFields} />
      </div>
    ),
  })

  const tabs = [
    tab('plano-contas', 'Plano de Contas', '/dados-mestres/plano-contas/', 'Plano de Contas',
      [
        { title: 'Código Red.', dataIndex: 'codigo_reduzido', key: 'codigo' },
        { title: 'Descrição', dataIndex: 'descricao', key: 'desc' },
        { title: 'Nível', dataIndex: 'nivel', key: 'nivel' },
        { title: 'Natureza', dataIndex: 'natureza', key: 'nat' },
        { title: 'Grupo', dataIndex: 'grupo', key: 'grupo' },
      ],
      [
        { name: 'tenant_id', label: 'Tenant ID', required: true },
        { name: 'codigo_reduzido', label: 'Código Reduzido', required: true },
        { name: 'descricao', label: 'Descrição', required: true },
        { name: 'nivel', label: 'Nível', required: true },
        { name: 'natureza', label: 'Natureza' },
        { name: 'grupo', label: 'Grupo' },
      ],
      'plano-contas',
    ),
    tab('centros-custo', 'Centros de Custo', '/dados-mestres/centros-custo/', 'Centros de Custo',
      [{ title: 'Código', dataIndex: 'codigo', key: 'cod' }, { title: 'Descrição', dataIndex: 'descricao', key: 'desc' }],
      [{ name: 'tenant_id', label: 'Tenant ID', required: true }, { name: 'codigo', label: 'Código', required: true }, { name: 'descricao', label: 'Descrição', required: true }],
      'centros-custo',
    ),
    tab('produtos', 'Produtos', '/dados-mestres/produtos/', 'Produtos',
      [{ title: 'Código', dataIndex: 'codigo', key: 'cod' }, { title: 'Nome', dataIndex: 'nome', key: 'nome' }, { title: 'Tipo', dataIndex: 'tipo', key: 'tipo' }, { title: 'Unidade', dataIndex: 'unidade', key: 'uni' }, { title: 'Cultura', dataIndex: 'cultura', key: 'cult' }],
      [{ name: 'tenant_id', label: 'Tenant ID', required: true }, { name: 'codigo', label: 'Código', required: true }, { name: 'nome', label: 'Nome', required: true }, { name: 'tipo', label: 'Tipo (grao/insumo/servico)', required: true }, { name: 'unidade', label: 'Unidade (sc/ton/kg)', required: true }, { name: 'cultura', label: 'Cultura' }],
      'produtos',
    ),
    tab('clientes-fornecedores', 'Clientes/Fornecedores', '/dados-mestres/clientes-fornecedores/', 'Clientes/Fornecedores',
      [{ title: 'Razão Social', dataIndex: 'razao_social', key: 'nome' }, { title: 'CNPJ/CPF', dataIndex: 'cnpj_cpf', key: 'doc' }, { title: 'Tipo', dataIndex: 'tipo', key: 'tipo' }],
      [{ name: 'tenant_id', label: 'Tenant ID', required: true }, { name: 'tipo', label: 'Tipo (C/F/A)', required: true }, { name: 'razao_social', label: 'Razão Social', required: true }, { name: 'cnpj_cpf', label: 'CNPJ/CPF' }],
      'clientes-fornecedores',
    ),
    tab('fazendas', 'Fazendas', '/dados-mestres/fazendas/', 'Fazendas',
      [{ title: 'Código', dataIndex: 'codigo', key: 'cod' }, { title: 'Nome', dataIndex: 'nome', key: 'nome' }, { title: 'Município', dataIndex: 'municipio', key: 'mun' }, { title: 'UF', dataIndex: 'uf', key: 'uf' }],
      [{ name: 'tenant_id', label: 'Tenant ID', required: true }, { name: 'codigo', label: 'Código', required: true }, { name: 'nome', label: 'Nome', required: true }, { name: 'municipio', label: 'Município' }, { name: 'uf', label: 'UF' }],
      'fazendas',
    ),
    tab('armazens', 'Armazéns', '/dados-mestres/armazens/', 'Armazéns',
      [{ title: 'Código', dataIndex: 'codigo', key: 'cod' }, { title: 'Nome', dataIndex: 'nome', key: 'nome' }, { title: 'Capacidade', dataIndex: 'capacidade', key: 'cap' }],
      [{ name: 'tenant_id', label: 'Tenant ID', required: true }, { name: 'codigo', label: 'Código', required: true }, { name: 'nome', label: 'Nome', required: true }, { name: 'capacidade', label: 'Capacidade' }, { name: 'unidade', label: 'Unidade' }],
      'armazens',
    ),
    tab('safras', 'Safras', '/dados-mestres/safras/', 'Safras',
      [{ title: 'Código', dataIndex: 'codigo', key: 'cod' }, { title: 'Início', dataIndex: 'ano_inicio', key: 'ini' }, { title: 'Fim', dataIndex: 'ano_fim', key: 'fim' }],
      [{ name: 'tenant_id', label: 'Tenant ID', required: true }, { name: 'codigo', label: 'Código (ex: 24/25)', required: true }, { name: 'ano_inicio', label: 'Ano Início', required: true }, { name: 'ano_fim', label: 'Ano Fim', required: true }],
      'safras',
    ),
  ]

  return (
    <Card title="Dados Mestres">
      <Tabs items={tabs} />
    </Card>
  )
}
