import CrudTable from '../../components/common/CrudTable'

export default function Templates() {
  return (
    <CrudTable
      endpoint="/import-config/templates"
      title="Templates de Importação"
      columns={[
        { title: 'Nome', dataIndex: 'nome', key: 'nome' },
        { title: 'Departamento', dataIndex: 'departamento_id', key: 'dept' },
        { title: 'Versão', dataIndex: 'versao', key: 'ver' },
      ]}
      formFields={[
        { name: 'tenant_id', label: 'Tenant ID', required: true },
        { name: 'departamento_id', label: 'Departamento ID', required: true },
        { name: 'nome', label: 'Nome', required: true },
        { name: 'schema_json', label: 'Schema (JSON)' },
      ]}
    />
  )
}
