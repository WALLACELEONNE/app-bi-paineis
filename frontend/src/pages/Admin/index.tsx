import { Tabs, Card } from 'antd'
import DadosMestres from './DadosMestres'
import Templates from './Templates'
import Pipelines from './Pipelines'
import Usuarios from './Usuarios'
import TemplateWizard from './TemplateWizard'

export default function AdminPage() {
  return (
    <Card title="Administração">
      <Tabs items={[
        { key: 'wizard', label: '🧙 Assistente De-Para', children: <TemplateWizard /> },
        { key: 'dados-mestres', label: 'Dados Mestres', children: <DadosMestres /> },
        { key: 'templates', label: 'Templates', children: <Templates /> },
        { key: 'pipelines', label: 'Pipelines', children: <Pipelines /> },
        { key: 'usuarios', label: 'Usuários', children: <Usuarios /> },
      ]} />
    </Card>
  )
}
