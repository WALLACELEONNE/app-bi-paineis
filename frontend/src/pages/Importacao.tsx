import { useState, useEffect } from 'react'
import { Card, Upload, Button, Select, Space, Table, Typography, message } from 'antd'
import { UploadOutlined, InboxOutlined } from '@ant-design/icons'
import type { UploadFile } from 'antd'
import api from '../services/api'

const { Dragger } = Upload
const { Text } = Typography

interface Template {
  id: number; nome: string; departamento_id: number; versao: number;
}

interface Pipeline {
  id: number; nome: string; departamento_id: number; versao: number; ativo: boolean;
}

interface Lote {
  id: number; nome_arquivo: string; status: string; linhas_ok: number;
  linhas_erro: number; total_linhas: number; erro_mensagem: string | null; criado_em: string;
}

function toUploadFile(f: File): UploadFile {
  return {
    uid: `${f.name}-${f.size}-${f.lastModified}`,
    name: f.name,
    size: f.size,
    type: f.type,
    originFileObj: f as any,
  }
}

export default function ImportacaoPage() {
  const [templates, setTemplates] = useState<Template[]>([])
  const [pipelines, setPipelines] = useState<Pipeline[]>([])
  const [selectedTemplate, setSelectedTemplate] = useState<number | null>(null)
  const [selectedPipeline, setSelectedPipeline] = useState<number | null>(null)
  const [fileList, setFileList] = useState<UploadFile[]>([])
  const [uploading, setUploading] = useState(false)
  const [lotes, setLotes] = useState<Lote[]>([])

  const loadLotes = () => {
    api.get('/upload/')
      .then(r => setLotes(r.data))
      .catch(() => message.error('Erro ao carregar histórico'))
  }

  useEffect(() => {
    api.get('/import-config/templates')
      .then(r => setTemplates(r.data))
      .catch(() => message.error('Erro ao carregar templates'))
    api.get('/import-config/pipelines')
      .then(r => setPipelines(r.data))
      .catch(() => message.error('Erro ao carregar pipelines'))
    loadLotes()
  }, [])

  const handleUpload = async () => {
    if (fileList.length === 0 || !selectedTemplate || !selectedPipeline) return
    const formData = new FormData()
    const originFile = (fileList[0] as any).originFileObj || fileList[0]
    formData.append('file', originFile, fileList[0].name)
    formData.append('template_id', String(selectedTemplate))
    formData.append('pipeline_id', String(selectedPipeline))
    setUploading(true)
    try {
      await api.post('/upload/', formData)
      message.success('Arquivo enviado e enfileirado para processamento')
      setFileList([])
      loadLotes()
      setTimeout(loadLotes, 5000)
    } catch (e: any) {
      message.error(e.response?.data?.detail || 'Erro no upload')
    } finally {
      setUploading(false)
    }
  }

  const statusColor: Record<string, string> = {
    pendente: 'default', processando: 'processing', concluido: 'success', erro: 'error',
  }

  const columns = [
    { title: 'Arquivo', dataIndex: 'nome_arquivo', key: 'file' },
    { title: 'Status', dataIndex: 'status', key: 'status', render: (s: string) => <Text type={statusColor[s] as any}>{s}</Text> },
    { title: 'Linhas', key: 'rows', render: (_: any, r: Lote) => `${r.linhas_ok || 0}/${r.total_linhas || 0}` },
    { title: 'Data', dataIndex: 'criado_em', key: 'date', render: (d: string) => new Date(d).toLocaleString('pt-BR') },
  ]

  return (
    <div style={{ maxWidth: 800, margin: '0 auto' }}>
      <Card title="Importação de Dados" style={{ marginBottom: 24 }}>
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Space wrap>
            <Select
              placeholder="Template de importação"
              style={{ width: 280 }}
              value={selectedTemplate}
              onChange={setSelectedTemplate}
              options={templates.map(t => ({ label: `${t.nome} (v${t.versao})`, value: t.id }))}
            />
            <Select
              placeholder="Pipeline de processamento"
              style={{ width: 280 }}
              value={selectedPipeline}
              onChange={setSelectedPipeline}
              options={pipelines.filter(p => p.ativo).map(p => ({ label: `${p.nome} (v${p.versao})`, value: p.id }))}
            />
          </Space>

          <Dragger
            maxCount={1}
            beforeUpload={() => false}
            onRemove={() => setFileList([])}
            onChange={({ fileList: fl }) => setFileList(fl)}
            fileList={fileList}
          >
            <p className="ant-upload-drag-icon"><InboxOutlined /></p>
            <p className="ant-upload-text">Clique ou arraste o arquivo CSV/XLSX</p>
          </Dragger>

          <Button type="primary" icon={<UploadOutlined />} onClick={handleUpload}
            loading={uploading} disabled={fileList.length === 0 || !selectedTemplate || !selectedPipeline} block size="large">
            Processar Arquivo
          </Button>
        </Space>
      </Card>

      <Card title="Histórico de Importações">
        <Table dataSource={lotes} columns={columns} rowKey="id" size="small" />
      </Card>
    </div>
  )
}
