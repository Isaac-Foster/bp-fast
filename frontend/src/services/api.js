import axios from 'axios'

// Configuração base do axios
const api = axios.create({
  baseURL: 'http://localhost:8000', // Ajuste conforme necessário
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
})

// Interceptor para requisições
api.interceptors.request.use(
  (config) => {
    // Adicionar token de autenticação se existir
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Interceptor para respostas
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    // Tratar erros de autenticação
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token')
      // Redirecionar para login se necessário
    }
    return Promise.reject(error)
  }
)

// Serviços de autenticação
export const authService = {
  async login(credentials) {
    try {
      const response = await api.post('/auth/login', credentials)
      return response.data
    } catch (error) {
      throw error.response?.data || error.message
    }
  },

  async register(userData) {
    try {
      const response = await api.post('/auth/register', userData)
      return response.data
    } catch (error) {
      throw error.response?.data || error.message
    }
  },

  async logout() {
    try {
      await api.post('/auth/logout')
      localStorage.removeItem('auth_token')
    } catch (error) {
      // Mesmo com erro, remover token local
      localStorage.removeItem('auth_token')
      throw error.response?.data || error.message
    }
  }
}

export default api
