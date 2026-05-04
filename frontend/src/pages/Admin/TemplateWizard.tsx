import { useState, useEffect, useRef } from 'react'
import { Card, Steps, Upload, Button, Select, Table, message, Result, Space, Tag, Input, Typography } from 'antd'
import { InboxOutlined, ArrowRightOutlined, CheckCircleOutlined } from '@ant-design/icons'
import type { UploadFile } from 'antd'
import api from '../../services/api'

const { Dragger } = Upload

interface SuggestedMapping {
  source_column: string
  suggested_target: string | null
  confidence: string
}

interface TargetField {
  key: string
  label: string
  type: string
  required: boolean
  description: string
}

interface Mapping {
  source_column: string
  target_field: string | null
}

export default function TemplateWizard({ onCreated }: { onCreated?: () => void }) {
  const rawFileRef = useRef<File | null>(null)
  const [step, setStep] = useState(0)
  const [fileList, setFileList] = useState<UploadFile[]>([])
  const [analyzing, setAnalyzing] = useState(false)
  const [analysis, setAnalysis] = useState<any>(null)
  const [departamentoId, setDepartamentoId] = useState<number | null>(null)
  const [targetFields, setTargetFields] = useState<TargetField[]>([])
  const [mappings, setMappings] = useState<Mapping[]>([])
  const [templateName, setTemplateName] = useState('')
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (step === 2 && departamentoId) {
      api.get(`/import-config/field-mapping/${departamentoId}`)
        .then(r => {
          setTargetFields(r.data.target_fields)
          const auto: Mapping[] = (analysis?.suggested_mappings || []).map((s: SuggestedMapping) => ({
            source_column: s.source_column,
            target_field: s.suggested_target || null,
          }))
          setMappings(auto)
        })
        .catch(() => message.error('Erro ao carregar campos'))
    }
  }, [step, departamentoId])

  const handleBeforeUpload = (file: File) => {
    rawFileRef.current = file
    setFileList([{
      uid: `-1`,
      name: file.name,
      size: file.size,
      type: file.type,
      originFileObj: file as any,
    }])
    return false
  }

  const handleAnalyze = async () => {
    const file = rawFileRef.current
    if (!file) return
    setAnalyzing(true)
    const formData = new FormData()
    formData.append('file', file, file.name)
    try {
      const r = await api.post('/import-config/analyze', formData)
      setAnalysis(r.data)
      setStep(1)
    } catch (e: any) {
      message.error(e.response?.data?.detail || 'Erro ao analisar arquivo')
    } finally {
      setAnalyzing(false)
    }
  }

  const updateMapping = (sourceColumn: string, targetField: string | null) => {
    setMappings(prev => prev.map(m => m.source_column === sourceColumn ? { ...m, target_field: targetField } : m))
  }

  const handleSave = async () => {
    const mapped = mappings.filter(m => m.target_field)
    if (mapped.length === 0) {
      message.warning('Mapeie ao menos uma coluna')
      return
    }

    const colunas = mapped.map(m => {
      const tf = targetFields.find(f => f.key === m.target_field)
      return {
        nome: m.source_column,
        tipo: tf?.type || 'string',
        obrigatorio: tf?.required || false,
      }
    })

    const jsonSchema = {
      departamento: departamentoId,
      versao: 1,
      colunas,
    }

    setSaving(true)
    try {
      await api.post('/import-config/templates', {
        tenant_id: 1,
        departamento_id: departamentoId,
        nome: templateName || `Template ${analysis?.filename || 'Importado'}`,
        json_schema: jsonSchema,
      })
      message.success('Template criado com sucesso!')
      onCreated?.()
    } catch (e: any) {
      message.error(e.response?.data?.detail || 'Erro ao salvar template')
    } finally {
      setSaving(false)
    }
  }

  const confidenceColor: Record<string, string> = { alta: 'green', media: 'orange', baixa: 'red' }

  return (
    <Card title="Assistente de De-Para" style={{ maxWidth: 900, margin: '0 auto' }}>
      <Steps current={step} items={[
        { title: '1. Upload da Planilha' },
        { title: '2. Selecionar Departamento' },
        { title: '3. Mapear Colunas (De-Para)' },
        { title: '4. Salvar Template' },
      ]} style={{ marginBottom: 32 }} />

      {step === 0 && (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Typography.Text type="secondary">
            Faça upload de uma planilha CSV ou XLSX. O sistema irá analisar os cabeçalhos e sugerir o mapeamento automaticamente.
          </Typography.Text>
          <Dragger maxCount={1} accept=".csv,.xlsx"
            beforeUpload={handleBeforeUpload}
            onRemove={() => { rawFileRef.current = null; setFileList([]) }}
            fileList={fileList}
          >
            <p className="ant-upload-drag-icon"><InboxOutlined /></p>
            <p className="ant-upload-text">Arraste sua planilha aqui</p>
            <p className="ant-upload-hint">Formatos aceitos: CSV e XLSX</p>
          </Dragger>
          <Button type="primary" size="large" block icon={<ArrowRightOutlined />}
            onClick={handleAnalyze} loading={analyzing} disabled={!rawFileRef.current}>
            Analisar Arquivo
          </Button>
        </Space>
      )}

      {step === 1 && (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Result status="success" title="Arquivo analisado"
            subTitle={`${analysis?.headers?.length || 0} colunas · ${analysis?.total_rows || 0} linhas · ${analysis?.filename}`}
          />

          <div style={{ background: '#f6ffed', padding: 16, borderRadius: 8 }}>
            <strong>Colunas detectadas na planilha:</strong>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginTop: 8 }}>
              {analysis?.headers?.map((h: string) => <Tag key={h}>{h}</Tag>)}
            </div>
          </div>

          <div>
            <strong>Para qual departamento?</strong>
            <Select placeholder="Selecione o departamento" style={{ width: '100%', marginTop: 8 }} size="large"
              value={departamentoId}
              onChange={(v) => setDepartamentoId(v)}
              options={[
                { label: 'Contabilidade', value: 1 }, { label: 'Financeiro', value: 2 },
                { label: 'Vendas', value: 3 }, { label: 'Compras', value: 4 },
                { label: 'Produção', value: 5 }, { label: 'Logística', value: 6 },
              ]}
            />
          </div>

          <Button type="primary" size="large" block icon={<ArrowRightOutlined />}
            onClick={() => setStep(2)} disabled={!departamentoId}>
            Mapear Colunas
          </Button>
        </Space>
      )}

      {step === 2 && (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <div style={{ background: '#e6f4ff', padding: 16, borderRadius: 8 }}>
            <strong>De-Para:</strong> Mapeie cada coluna da planilha para um campo do sistema.
            Colunas com sugestão automática já estão preenchidas.
          </div>

          <Table dataSource={mappings} rowKey="source_column" pagination={false} size="small"
            columns={[
              {
                title: 'Coluna na Planilha', dataIndex: 'source_column', key: 'src',
                render: (col: string, _: any, i: number) => {
                  const sug = analysis?.suggested_mappings?.[i]
                  const conf = sug?.confidence || 'baixa'
                  return (
                    <Space>
                      {col}
                      {conf === 'alta' && <Tag color="green" style={{ fontSize: 10 }}>✔ automático</Tag>}
                      {conf === 'media' && <Tag color="orange" style={{ fontSize: 10 }}>sugestão</Tag>}
                    </Space>
                  )
                },
              },
              {
                title: 'Campo no Sistema', dataIndex: 'target_field', key: 'tgt',
                render: (_: any, record: Mapping) => (
                  <Select placeholder="Selecionar campo..." style={{ width: 280 }} allowClear
                    value={record.target_field}
                    onChange={(v) => updateMapping(record.source_column, v)}
                    options={targetFields.map(f => ({
                      label: (
                        <span>
                          {f.label}
                          {f.required && <Tag color="red" style={{ marginLeft: 4, fontSize: 10 }}>obrig</Tag>}
                          <span style={{ color: '#999', fontSize: 11, marginLeft: 4 }}>({f.type})</span>
                        </span>
                      ),
                      value: f.key,
                    }))}
                  />
                ),
              },
            ]}
          />

          <div>
            <strong>Nome do Template:</strong>
            <Input placeholder="Ex: Template de Vendas Jan/2024" style={{ marginTop: 8 }}
              value={templateName} onChange={e => setTemplateName(e.target.value)} />
          </div>

          <Button type="primary" size="large" block icon={<CheckCircleOutlined />}
            onClick={handleSave} loading={saving} disabled={!templateName.trim()}>
            Salvar Template
          </Button>
        </Space>
      )}
    </Card>
  )
}
