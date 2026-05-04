import { useEffect, useState } from 'react'
import { Table, Button, Modal, Form, Input, Space, Popconfirm, message } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import api from '../../services/api'

interface CrudTableProps {
  endpoint: string
  title: string
  columns: { title: string; dataIndex: string; key: string }[]
  formFields: { name: string; label: string; required?: boolean; type?: string }[]
}

export default function CrudTable({ endpoint, title, columns, formFields }: CrudTableProps) {
  const [data, setData] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState<any>(null)
  const [form] = Form.useForm()

  const load = async () => {
    setLoading(true)
    try {
      const res = await api.get(endpoint)
      setData(res.data)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [endpoint])

  const onSave = async (values: any) => {
    try {
      if (editing) {
        await api.put(`${endpoint}/${editing.id}`, values)
        message.success('Atualizado')
      } else {
        await api.post(endpoint, values)
        message.success('Criado')
      }
      setModalOpen(false)
      form.resetFields()
      setEditing(null)
      load()
    } catch {
      message.error('Erro ao salvar')
    }
  }

  const onDelete = async (id: number) => {
    try {
      await api.delete(`${endpoint}/${id}`)
      message.success('Removido')
      load()
    } catch {
      message.error('Erro ao remover')
    }
  }

  const openEdit = (record: any) => {
    setEditing(record)
    form.setFieldsValue(record)
    setModalOpen(true)
  }

  const openCreate = () => {
    setEditing(null)
    form.resetFields()
    setModalOpen(true)
  }

  const actionsColumn = {
    title: 'Ações', key: 'actions', width: 120,
    render: (_: any, record: any) => (
      <Space>
        <Button size="small" icon={<EditOutlined />} onClick={() => openEdit(record)} />
        <Popconfirm title="Remover?" onConfirm={() => onDelete(record.id)}>
          <Button size="small" danger icon={<DeleteOutlined />} />
        </Popconfirm>
      </Space>
    ),
  }

  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h3>{title}</h3>
        <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>Novo</Button>
      </div>
      <Table dataSource={data} columns={[...columns, actionsColumn]} rowKey="id" loading={loading} size="small" />
      <Modal title={editing ? `Editar ${title}` : `Novo ${title}`} open={modalOpen} onCancel={() => setModalOpen(false)} onOk={() => form.submit()} destroyOnHidden>
        <Form form={form} layout="vertical" onFinish={onSave}>
          {formFields.map((f) => (
            <Form.Item key={f.name} name={f.name} label={f.label} rules={f.required ? [{ required: true, message: 'Obrigatório' }] : []}>
              <Input />
            </Form.Item>
          ))}
        </Form>
      </Modal>
    </>
  )
}
