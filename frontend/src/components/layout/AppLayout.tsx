import { Layout, Menu, Typography, Button, Dropdown } from 'antd'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import {
  DashboardOutlined, BankOutlined, DollarOutlined, ShoppingCartOutlined,
  ShoppingOutlined, ExperimentOutlined, CarOutlined, UploadOutlined,
  SettingOutlined, LogoutOutlined, UserOutlined,
} from '@ant-design/icons'
import { useAuthStore } from '../../store/authStore'

const { Sider, Content, Header } = Layout

const menuItems = [
  { key: '/', icon: <DashboardOutlined />, label: 'Dashboard' },
  { key: '/contabil', icon: <BankOutlined />, label: 'Contabilidade' },
  { key: '/financeiro', icon: <DollarOutlined />, label: 'Financeiro' },
  { key: '/vendas', icon: <ShoppingCartOutlined />, label: 'Vendas' },
  { key: '/compras', icon: <ShoppingOutlined />, label: 'Compras' },
  { key: '/producao', icon: <ExperimentOutlined />, label: 'Produção' },
  { key: '/logistica', icon: <CarOutlined />, label: 'Logística' },
  { key: '/importacao', icon: <UploadOutlined />, label: 'Importação' },
  { key: '/admin', icon: <SettingOutlined />, label: 'Administração' },
]

export default function AppLayout() {
  const navigate = useNavigate()
  const location = useLocation()
  const { user, logout } = useAuthStore()

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider breakpoint="lg" collapsedWidth="0">
        <div style={{ height: 64, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Typography.Text strong style={{ color: '#fff', fontSize: 18 }}>
            BI Agro
          </Typography.Text>
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname === '/' ? '/' : `/${location.pathname.split('/')[1]}`]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
        />
      </Sider>
      <Layout>
        <Header style={{ background: '#fff', padding: '0 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography.Title level={4} style={{ margin: 0 }}>
            Plataforma de BI - Agronegócio
          </Typography.Title>
          <Dropdown
            menu={{
              items: [{ key: 'logout', icon: <LogoutOutlined />, label: 'Sair', onClick: () => { logout(); navigate('/login') } }],
            }}
          >
            <Button type="text" icon={<UserOutlined />}>
              {user?.nome || 'Usuário'}
            </Button>
          </Dropdown>
        </Header>
        <Content style={{ margin: 24 }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  )
}
