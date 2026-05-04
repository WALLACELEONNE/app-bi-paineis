import { create } from 'zustand'
import api from '../services/api'

interface Widget {
  id: number
  tipo: string
  titulo: string
  config: any
  posicao_x: number
  posicao_y: number
  largura: number
  altura: number
}

interface DashboardState {
  widgets: Widget[]
  dashboardId: number | null
  filters: { data_inicio: string | null; data_fim: string | null; departamento_id: number | null }
  loading: boolean
  loadWidgets: (dashId: number) => Promise<void>
  addWidget: (tipo: string, config: any) => Promise<void>
  removeWidget: (widgetId: number) => Promise<void>
  setFilters: (filters: Partial<DashboardState['filters']>) => void
}

export const useDashboardStore = create<DashboardState>((set, get) => ({
  widgets: [],
  dashboardId: null,
  filters: { data_inicio: null, data_fim: null, departamento_id: null },
  loading: false,

  loadWidgets: async (dashId: number) => {
    set({ loading: true, dashboardId: dashId })
    try {
      const r = await api.get(`/dashboards/${dashId}/widgets`)
      set({ widgets: r.data, loading: false })
    } catch {
      set({ loading: false })
    }
  },

  addWidget: async (tipo: string, config: any) => {
    const { dashboardId } = get()
    if (!dashboardId) return
    const configWithFilters = { ...config, params: { ...config.params, ...get().filters } }
    const r = await api.post(`/dashboards/${dashboardId}/widgets`, {
      dashboard_id: dashboardId,
      usuario_id: 0,
      tipo,
      config: configWithFilters,
      posicao_x: 0,
      posicao_y: get().widgets.length,
      largura: configWithFilters.largura || 6,
      altura: configWithFilters.altura || 3,
    })
    set(s => ({ widgets: [...s.widgets, r.data] }))
  },

  removeWidget: async (widgetId: number) => {
    const { dashboardId } = get()
    if (!dashboardId) return
    await api.delete(`/dashboards/${dashboardId}/widgets/${widgetId}`)
    set(s => ({ widgets: s.widgets.filter(w => w.id !== widgetId) }))
  },

  setFilters: (filters) => {
    set(s => ({ filters: { ...s.filters, ...filters } }))
  },
}))
