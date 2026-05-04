import api from './api'

interface LoginRequest {
  email: string
  senha: string
}

interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

interface UserData {
  id: number
  tenant_id: number
  email: string
  nome: string
  role: string
  ativo: boolean
}

export const authService = {
  async login(data: LoginRequest): Promise<TokenResponse> {
    const formData = new URLSearchParams()
    formData.append('username', data.email)
    formData.append('password', data.senha)
    const response = await api.post('/auth/login', data)
    return response.data
  },

  async refresh(refreshToken: string): Promise<TokenResponse> {
    const response = await api.post('/auth/refresh', { refresh_token: refreshToken })
    return response.data
  },

  async me(): Promise<UserData> {
    const response = await api.get('/auth/me')
    return response.data
  },
}
