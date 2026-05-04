import CrudTable from '../../components/common/CrudTable'

export default function Pipelines() {
  return (
    <CrudTable
      endpoint="/import-config/pipelines"
      title="Pipelines de Processamento"
      columns={[
        { title: 'Nome', dataIndex: 'nome', key: 'nome' },
        { title: 'Departamento', dataIndex: 'departamento_id', key: 'dept' },
        { title: 'Versão', dataIndex: 'versao', key: 'ver' },
        { title: 'Ativo', dataIndex: 'ativo', key: 'ativo' },
      ]}
      formFields={[
        { name: 'tenant_id', label: 'Tenant ID', required: true },
        { name: 'departamento_id', label: 'Departamento ID', required: true },
        { name: 'nome', label: 'Nome', required: true },
        { name: 'config_yaml', label: 'Configuração (YAML)' },
      ]}
    />
  )
}
