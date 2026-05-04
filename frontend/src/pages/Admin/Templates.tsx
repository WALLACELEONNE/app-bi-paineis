import CrudTable from '../../components/common/CrudTable'

const JSON_DEFAULT = `{
  "colunas": [
    {
      "nome": "data",
      "tipo": "date",
      "obrigatorio": true
    },
    {
      "nome": "valor",
      "tipo": "float",
      "obrigatorio": true
    }
  ],
  "mapeamento": {},
  "validacoes_customizadas": []
}`

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
        { name: 'json_schema', label: 'Schema (JSON)', type: 'code' },
      ]}
      codeFields={['json_schema']}
      defaultValues={{ json_schema: JSON_DEFAULT }}
    />
  )
}
