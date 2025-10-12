<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h1>Login</h1>
        <p>Entre com suas credenciais</p>
      </div>
      
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="email">Email</label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            placeholder="Digite seu email"
            required
            :disabled="loading"
          />
        </div>
        
        <div class="form-group">
          <label for="password">Senha</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            placeholder="Digite sua senha"
            required
            :disabled="loading"
          />
        </div>
        
        <button 
          type="submit" 
          class="login-button"
          :disabled="loading || !isFormValid"
        >
          <span v-if="loading">Entrando...</span>
          <span v-else>Entrar</span>
        </button>
      </form>
      
      <div v-if="error" class="error-message">
        {{ error }}
      </div>
      
      <div class="login-footer">
        <p>Não tem uma conta? <a href="#" @click.prevent="goToRegister">Cadastre-se</a></p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { authService } from '../services/api.js'

// Estado do formulário
const form = ref({
  email: '',
  password: ''
})

// Estado da aplicação
const loading = ref(false)
const error = ref('')

// Computed para validar se o formulário está válido
const isFormValid = computed(() => {
  return form.value.email && form.value.password
})

// Função para lidar com o login
const handleLogin = async () => {
  if (!isFormValid.value) return
  
  loading.value = true
  error.value = ''
  
  try {
    const response = await authService.login({
      email: form.value.email,
      password: form.value.password
    })
    
    // Salvar token se retornado
    if (response.token) {
      localStorage.setItem('auth_token', response.token)
    }
    
    // Sucesso - redirecionar ou emitir evento
    console.log('Login realizado com sucesso:', response)
    alert('Login realizado com sucesso!')
    
    // Limpar formulário
    form.value = { email: '', password: '' }
    
  } catch (err) {
    console.error('Erro no login:', err)
    error.value = err.message || 'Erro ao fazer login. Tente novamente.'
  } finally {
    loading.value = false
  }
}

// Função para ir para registro (placeholder)
const goToRegister = () => {
  console.log('Ir para página de registro')
  // Implementar navegação para registro
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  padding: 40px;
  width: 100%;
  max-width: 400px;
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h1 {
  color: #333;
  font-size: 28px;
  font-weight: 600;
  margin: 0 0 8px 0;
}

.login-header p {
  color: #666;
  font-size: 14px;
  margin: 0;
}

.login-form {
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  color: #333;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 6px;
}

.form-group input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.2s ease;
  box-sizing: border-box;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
}

.form-group input:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.login-button {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.login-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}

.login-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.error-message {
  background-color: #fee;
  color: #c33;
  padding: 12px;
  border-radius: 6px;
  font-size: 14px;
  margin-bottom: 20px;
  border: 1px solid #fcc;
}

.login-footer {
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.login-footer p {
  color: #666;
  font-size: 14px;
  margin: 0;
}

.login-footer a {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
}

.login-footer a:hover {
  text-decoration: underline;
}

/* Responsividade */
@media (max-width: 480px) {
  .login-card {
    padding: 30px 20px;
    margin: 10px;
  }
  
  .login-header h1 {
    font-size: 24px;
  }
}
</style>
