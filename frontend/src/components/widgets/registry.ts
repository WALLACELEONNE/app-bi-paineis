import { BarChartWidget, LineChartWidget, PieChartWidget, KPICardWidget, DataTableWidget, HeatmapWidget } from './WidgetComponents'

export const widgetComponentMap: Record<string, React.ComponentType<{ data: any; height?: number }>> = {
  bar_chart: BarChartWidget,
  line_chart: LineChartWidget,
  pie_chart: PieChartWidget,
  kpi_card: KPICardWidget,
  data_table: DataTableWidget,
  heatmap: HeatmapWidget,
}

export const widgetLabels: Record<string, string> = {
  bar_chart: 'Gráfico de Barras',
  line_chart: 'Gráfico de Linha',
  pie_chart: 'Gráfico de Pizza',
  kpi_card: 'Cartão KPI',
  data_table: 'Tabela de Dados',
  heatmap: 'Mapa de Calor',
}

export type WidgetType = keyof typeof widgetComponentMap
