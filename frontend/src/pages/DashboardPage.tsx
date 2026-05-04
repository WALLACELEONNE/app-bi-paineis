import { useEffect, useState } from 'react'
import { Card, Row, Col, Button, Select, DatePicker, Space, Modal, Typography, Empty, Popconfirm } from 'antd'
import { PlusOutlined, DeleteOutlined, ReloadOutlined } from '@ant-design/icons'
import dayjs from 'dayjs'
import WidgetRenderer from '../components/widgets/WidgetRenderer'
import { widgetLabels } from '../components/widgets/registry'
import { useDashboardStore } from '../store/dashboardStore'
import api from '../services/api'

const { RangePicker } = DatePicker

export default function DashboardPage() {
  const { widgets, dashboardId, filters, loading, loadWidgets, addWidget, removeWidget, setFilters } = useDashboardStore()
  const [dashboards, setDashboards] = useState<any[]>([])
  const [selectedDash, setSelectedDash] = useState<number | null>(null)
  const [addModalOpen, setAddModalOpen] = useState(false)
  const [addType, setAddType] = useState<string>('kpi_card')

  useEffect(() => {
    api.get('/dashboards/').then(r => {
      setDashboards(r.data)
      if (r.data.length > 0 && !selectedDash) {
        setSelectedDash(r.data[0].id)
        loadWidgets(r.data[0].id)
      }
    })
  }, [])

  const selectDashboard = (id: number) => {
    setSelectedDash(id)
    loadWidgets(id)
  }

  const ensureDashboard = async () => {
    if (dashboards.length === 0) {
      const r = await api.post('/dashboards/', { tenant_id: 1, nome: 'Dashboard Principal', slug: 'principal' })
      setDashboards([r.data])
      setSelectedDash(r.data.id)
      loadWidgets(r.data.id)
    }
  }

  const onAddWidget = async () => {
    await addWidget(addType, {
      endpoint: addType === 'kpi_card' ? 'kpi' : addType === 'data_table' ? 'tabela' : 'series_temporal',
      params: {},
      largura: 6,
      altura: 3,
    })
    setAddModalOpen(false)
  }

  const onDateChange = (dates: any) => {
    if (dates) {
      setFilters({ data_inicio: dates[0].format('YYYY-MM-DD'), data_fim: dates[1].format('YYYY-MM-DD') })
    } else {
      setFilters({ data_inicio: null, data_fim: null })
    }
  }

  return (
    <div>
      <Card style={{ marginBottom: 16 }}>
        <Space wrap>
          <Select
            placeholder="Dashboard"
            style={{ width: 240 }}
            value={selectedDash}
            onChange={selectDashboard}
            options={dashboards.map((d: any) => ({ label: d.nome, value: d.id }))}
          />
          <RangePicker onChange={onDateChange} value={filters.data_inicio ? [dayjs(filters.data_inicio), dayjs(filters.data_fim)] : null} />
          <Select
            placeholder="Departamento"
            style={{ width: 180 }}
            allowClear
            value={filters.departamento_id}
            onChange={(v) => setFilters({ departamento_id: v })}
            options={[
              { label: 'Contabilidade', value: 1 }, { label: 'Financeiro', value: 2 },
              { label: 'Vendas', value: 3 }, { label: 'Compras', value: 4 },
              { label: 'Produção', value: 5 }, { label: 'Logística', value: 6 },
            ]}
          />
          <Button icon={<ReloadOutlined />} onClick={() => selectedDash && loadWidgets(selectedDash)}>Atualizar</Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => { ensureDashboard(); setAddModalOpen(true) }}>Widget</Button>
        </Space>
      </Card>

      {widgets.length === 0 ? (
        <Card>
          <Empty description="Nenhum widget. Clique em 'Widget' para adicionar.">
            <Button type="primary" icon={<PlusOutlined />} onClick={() => { ensureDashboard(); setAddModalOpen(true) }}>Adicionar Widget</Button>
          </Empty>
        </Card>
      ) : (
        <Row gutter={[16, 16]}>
          {widgets.map(w => (
            <Col key={w.id} span={w.largura * 2}>
              <Card
                title={w.titulo || widgetLabels[w.tipo] || w.tipo}
                extra={
                  <Popconfirm title="Remover?" onConfirm={() => removeWidget(w.id)}>
                    <Button size="small" danger icon={<DeleteOutlined />} />
                  </Popconfirm>
                }
                styles={{ body: { padding: 12 } }}
              >
                <WidgetRenderer tipo={w.tipo} config={w.config} />
              </Card>
            </Col>
          ))}
        </Row>
      )}

      <Modal title="Adicionar Widget" open={addModalOpen} onCancel={() => setAddModalOpen(false)} onOk={onAddWidget}>
        <Select
          style={{ width: '100%' }}
          value={addType}
          onChange={setAddType}
          options={Object.entries(widgetLabels).map(([key, label]) => ({ label, value: key }))}
        />
      </Modal>
    </div>
  )
}
