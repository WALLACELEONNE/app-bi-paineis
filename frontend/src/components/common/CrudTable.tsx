import { useEffect, useState } from 'react'
import { Table, Button, Modal, Form, Input, Space, Popconfirm, message } from 'antd'
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons'
import api from '../../services/api'
import FormCodeEditor from './FormCodeEditor'
import { useAuthStore } from '../../store/authStore'

interface FormField {
  name: string
  label: string
  required?: boolean
  type?: string
  hidden?: boolean
}

interface CrudTableProps {
  endpoint: string
  title: string
  columns: { title: string; dataIndex: string; key: string }[]
  formFields: FormField[]
  defaultValues?: Record<string, any>
  codeFields?: string[]
}

function getTenantId(): number {
  const user = useAuthStore.getState().user
  return user?.tenant_id || 1
}

export default function CrudTable({ endpoint, title, columns, formFields, defaultValues = {}, codeFields = [] }: CrudTableProps) {
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
    } catch {
      message.error('Erro ao carregar dados')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [endpoint])

  const onSave = async (values: any) => {
    try {
      const payload = { ...values }
      for (const f of codeFields) {
        if (typeof payload[f] === 'string') {
          try { payload[f] = JSON.parse(payload[f]) } catch {}
        }
      }
      if (editing) {
        await api.put(`${endpoint}/${editing.id}`, payload)
        message.success('Atualizado')
      } else {
        if (!editing) payload.tenant_id = getTenantId()
        await api.post(endpoint, { ...defaultValues, ...payload })
        message.success('Criado')
      }
      setModalOpen(false)
      form.resetFields()
      setEditing(null)
      load()
    } catch (e: any) {
      message.error(e.response?.data?.detail || 'Erro ao salvar')
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
    const formValues: any = {}
    for (const f of formFields) {
      if (f.type === 'code' && record[f.name]) {
        formValues[f.name] = typeof record[f.name] === 'string' ? record[f.name] : JSON.stringify(record[f.name], null, 2)
      } else {
        formValues[f.name] = record[f.name]
      }
    }
    form.setFieldsValue(formValues)
    setModalOpen(true)
  }

  const openCreate = () => {
    setEditing(null)
    const initial: any = {}
    for (const f of formFields) {
      if (f.name === 'tenant_id') initial[f.name] = String(getTenantId())
      else if (defaultValues[f.name] !== undefined) initial[f.name] = defaultValues[f.name]
    }
    form.resetFields()
    form.setFieldsValue(initial)
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
      <Modal
        title={editing ? `Editar ${title}` : `Novo ${title}`}
        open={modalOpen} onCancel={() => setModalOpen(false)} onOk={() => form.submit()}
        destroyOnHidden width={codeFields.length > 0 ? 800 : 520}
      >
        <Form form={form} layout="vertical" onFinish={onSave}>
          {formFields.map((f) => !f.hidden && (
            <Form.Item key={f.name} name={f.name} label={f.label} rules={f.required ? [{ required: true, message: 'Obrigatório' }] : []}>
              {f.name === 'tenant_id' ? (
                <Input disabled placeholder="Preenchido automaticamente" />
              ) : codeFields.includes(f.name) ? (
                <FormCodeEditor name={f.name} language={f.name.includes('yaml') || f.name.includes('config') ? 'yaml' : 'json'} />
              ) : f.name === 'json_schema' || f.name === 'config_yaml' ? (
                <Input.TextArea rows={8} style={{ fontFamily: 'monospace', fontSize: 13 }} />
              ) : (
                <Input />
              )}
            </Form.Item>
          ))}
        </Form>
      </Modal>
    </>
  )
}
