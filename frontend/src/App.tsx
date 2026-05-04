import { useEffect } from 'react'
import { Routes, Route, Navigate, Outlet } from 'react-router-dom'
import { Spin } from 'antd'
import { useAuthStore } from './store/authStore'
import AppLayout from './components/layout/AppLayout'
import DashboardPage from './pages/DashboardPage'
import Login from './pages/Login'
import AdminPage from './pages/Admin'
import ImportacaoPage from './pages/Importacao'

function ProtectedRoute() {
  const { isAuthenticated, isLoading } = useAuthStore()

  if (isLoading) {
    return <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}><Spin size="large" /></div>
  }
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  return <Outlet />
}

function App() {
  const { isAuthenticated, loadUser } = useAuthStore()

  useEffect(() => {
    if (localStorage.getItem('access_token')) {
      loadUser()
    }
  }, [loadUser])

  return (
    <Routes>
      <Route path="/login" element={isAuthenticated ? <Navigate to="/" replace /> : <Login />} />
      <Route element={<ProtectedRoute />}>
        <Route path="/" element={<AppLayout />}>
          <Route index element={<DashboardPage />} />
          <Route path="contabil" element={<DashboardPage />} />
          <Route path="financeiro" element={<DashboardPage />} />
          <Route path="vendas" element={<DashboardPage />} />
          <Route path="compras" element={<DashboardPage />} />
          <Route path="producao" element={<DashboardPage />} />
          <Route path="logistica" element={<DashboardPage />} />
          <Route path="importacao" element={<ImportacaoPage />} />
          <Route path="admin/*" element={<AdminPage />} />
        </Route>
      </Route>
    </Routes>
  )
}

export default App
