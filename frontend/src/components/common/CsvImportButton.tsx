import { useState } from 'react'
import { Upload, Button, message } from 'antd'
import { UploadOutlined } from '@ant-design/icons'
import api from '../../services/api'

interface Props {
  entity: string
  onImported: () => void
}

export default function CsvImportButton({ entity, onImported }: Props) {
  const [uploading, setUploading] = useState(false)

  const handleUpload = async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    setUploading(true)
    try {
      const r = await api.post(`/dados-mestres/import/${entity}`, formData)
      const { ok, erros } = r.data
      message.success(`Importado: ${ok} linhas OK, ${erros} erros`)
      onImported()
    } catch (e: any) {
      message.error(e.response?.data?.detail || 'Erro na importação')
    } finally {
      setUploading(false)
    }
    return false
  }

  return (
    <Upload accept=".csv" showUploadList={false} beforeUpload={handleUpload}>
      <Button icon={<UploadOutlined />} loading={uploading} size="small">
        Importar CSV
      </Button>
    </Upload>
  )
}
