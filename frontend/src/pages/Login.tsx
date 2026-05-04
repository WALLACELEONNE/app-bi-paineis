import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, Form, Input, Button, Typography, message } from 'antd'
import { UserOutlined, LockOutlined } from '@ant-design/icons'
import { useAuthStore } from '../store/authStore'

export default function Login() {
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()
  const login = useAuthStore((s) => s.login)

  const onSubmit = async (values: { email: string; senha: string }) => {
    setLoading(true)
    try {
      await login(values.email, values.senha)
      message.success('Login realizado com sucesso')
      navigate('/')
    } catch {
      message.error('Email ou senha inválidos')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      display: 'flex', justifyContent: 'center', alignItems: 'center',
      minHeight: '100vh', background: 'linear-gradient(135deg, #166534 0%, #22c55e 100%)',
    }}>
      <Card
        title={<span style={{ fontSize: 20 }}>BI Agro Platform</span>}
        style={{ width: 400, boxShadow: '0 4px 24px rgba(0,0,0,0.15)' }}
      >
        <Form layout="vertical" onFinish={onSubmit} autoComplete="off">
          <Form.Item name="email" rules={[{ required: true, message: 'Informe seu email' }, { type: 'email', message: 'Email inválido' }]}>
            <Input prefix={<UserOutlined />} placeholder="Email" size="large" />
          </Form.Item>
          <Form.Item name="senha" rules={[{ required: true, message: 'Informe sua senha' }]}>
            <Input.Password prefix={<LockOutlined />} placeholder="Senha" size="large" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block size="large">
              Entrar
            </Button>
          </Form.Item>
        </Form>
        <Typography.Text type="secondary" style={{ display: 'block', textAlign: 'center' }}>
          admin@biagro.com.br / admin123
        </Typography.Text>
      </Card>
    </div>
  )
}
