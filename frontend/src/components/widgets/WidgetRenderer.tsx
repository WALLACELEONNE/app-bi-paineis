import { useEffect, useState } from 'react'
import { Spin, Empty } from 'antd'
import { widgetComponentMap } from './registry'
import api from '../../services/api'

interface Props {
  tipo: string
  config: any
}

export default function WidgetRenderer({ tipo, config }: Props) {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    const endpoint = config.endpoint || `${tipo}`
    const params = config.params || {}
    api.get(`/bi/${endpoint}`, { params })
      .then(r => { if (!cancelled) setData(r.data) })
      .catch(() => { if (!cancelled) setData(null) })
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [tipo, config])

  if (loading) return <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 200 }}><Spin /></div>
  if (!data) return <Empty description="Sem dados" />

  const Component = widgetComponentMap[tipo]
  if (!Component) return <Empty description={`Widget "${tipo}" não encontrado`} />
  return <Component data={data} height={config.height || 280} />
}
