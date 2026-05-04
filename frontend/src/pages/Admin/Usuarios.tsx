import CrudTable from '../../components/common/CrudTable'

export default function Usuarios() {
  return (
    <CrudTable
      endpoint="/usuarios"
      title="Usuários"
      columns={[
        { title: 'Nome', dataIndex: 'nome', key: 'nome' },
        { title: 'Email', dataIndex: 'email', key: 'email' },
        { title: 'Role', dataIndex: 'role', key: 'role' },
        { title: 'Ativo', dataIndex: 'ativo', key: 'ativo' },
      ]}
      formFields={[
        { name: 'tenant_id', label: 'Tenant ID', required: true },
        { name: 'nome', label: 'Nome', required: true },
        { name: 'email', label: 'Email', required: true },
        { name: 'senha', label: 'Senha', required: true },
        { name: 'role', label: 'Role (admin/gestor/analista/visualizador)', required: true },
      ]}
    />
  )
}
