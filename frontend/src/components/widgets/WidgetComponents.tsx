import ReactECharts from 'echarts-for-react'

interface Props { data: any; height?: number }

export function BarChartWidget({ data, height }: Props) {
  const option = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: data?.categorias || [] },
    yAxis: { type: 'value' },
    series: (data?.series || []).map((s: any) => ({ name: s.nome, type: 'bar', data: s.valores })),
  }
  return <ReactECharts option={option} style={{ height: height || 300 }} />
}

export function LineChartWidget({ data, height }: Props) {
  const option = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: data?.categorias || [] },
    yAxis: { type: 'value' },
    series: (data?.series || []).map((s: any) => ({ name: s.nome, type: 'line', data: s.valores, smooth: true })),
  }
  return <ReactECharts option={option} style={{ height: height || 300 }} />
}

export function PieChartWidget({ data, height }: Props) {
  const option = {
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      data: (data?.categorias || []).map((c: string, i: number) => ({
        name: c, value: data?.series?.[0]?.valores?.[i] || 0,
      })),
    }],
  }
  return <ReactECharts option={option} style={{ height: height || 300 }} />
}

export function KPICardWidget({ data }: Props) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
      <span style={{ fontSize: 12, color: '#888' }}>VALOR TOTAL</span>
      <span style={{ fontSize: 36, fontWeight: 700, color: '#166534' }}>
        {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', minimumFractionDigits: 0 }).format(data?.total || 0)}
      </span>
      <span style={{ fontSize: 12, color: '#aaa' }}>{data?.registros || 0} registros</span>
    </div>
  )
}

export function DataTableWidget({ data }: Props) {
  if (!data?.colunas || !data?.linhas) return <div style={{ padding: 20, color: '#999' }}>Sem dados</div>
  return (
    <table style={{ width: '100%', fontSize: 12, borderCollapse: 'collapse' }}>
      <thead>
        <tr style={{ background: '#f5f5f5' }}>
          {data.colunas.map((c: string) => <th key={c} style={{ padding: 6, textAlign: 'left', borderBottom: '1px solid #ddd' }}>{c}</th>)}
        </tr>
      </thead>
      <tbody>
        {data.linhas.map((row: any, i: number) => (
          <tr key={i}>
            {data.colunas.map((c: string) => <td key={c} style={{ padding: 6, borderBottom: '1px solid #eee' }}>{typeof row[c] === 'number' ? row[c].toLocaleString('pt-BR') : String(row[c] ?? '-')}</td>)}
          </tr>
        ))}
      </tbody>
    </table>
  )
}

export function HeatmapWidget({ data }: Props) {
  const months = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
  const option = {
    tooltip: { position: 'top' as const },
    grid: { height: '70%', top: '10%' },
    xAxis: { type: 'category', data: data?.categorias || months, splitArea: { show: true } },
    yAxis: { type: 'category', data: data?.categorias || [] },
    visualMap: { min: 0, max: 10, calculable: true, orient: 'horizontal', left: 'center', bottom: 0 },
    series: [{
      type: 'heatmap',
      data: data?.heatmap_data || [],
      label: { show: true },
      emphasis: { itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.5)' } },
    }],
  }
  return <ReactECharts option={option} style={{ height: 300 }} />
}
