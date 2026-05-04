import { create } from 'zustand'
import { authService } from '../services/authService'

interface User {
  id: number
  tenant_id: number
  email: string
  nome: string
  role: string
  ativo: boolean
}

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  loadUser: () => Promise<void>
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: !!localStorage.getItem('access_token'),
  isLoading: false,

  login: async (email: string, password: string) => {
    set({ isLoading: true })
    try {
      const tokens = await authService.login({ email, senha: password })
      localStorage.setItem('access_token', tokens.access_token)
      localStorage.setItem('refresh_token', tokens.refresh_token)
      const user = await authService.me()
      set({ user, isAuthenticated: true, isLoading: false })
    } catch {
      set({ isLoading: false })
      throw new Error('Falha na autenticação')
    }
  },

  logout: () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    set({ user: null, isAuthenticated: false })
  },

  loadUser: async () => {
    try {
      const user = await authService.me()
      set({ user, isAuthenticated: true })
    } catch {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      set({ user: null, isAuthenticated: false })
    }
  },
}))
