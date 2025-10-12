# Setup do Frontend - Login

## Estrutura do Projeto

```
frontend/
├── src/
│   ├── components/
│   │   └── Login.vue          # Componente de login principal
│   ├── services/
│   │   └── api.js            # Serviço de API com axios
│   ├── App.vue               # Componente raiz
│   └── main.js               # Ponto de entrada
├── package.json
└── vite.config.js
```

## Funcionalidades Implementadas

### 1. Componente Login (`Login.vue`)
- **Layout simplista e responsivo** com design moderno
- **Formulário com validação** usando Vue 3 Composition API
- **Event preventDefault** implementado no `@submit.prevent="handleLogin"`
- **Estados de loading** e tratamento de erros
- **Campos**: Email e Senha com validação
- **Estilos CSS** com gradientes e animações suaves

### 2. Serviço de API (`api.js`)
- **Configuração do axios** com interceptors
- **Base URL configurável** (padrão: http://localhost:8000)
- **Interceptors para requisições** (adiciona token automaticamente)
- **Interceptors para respostas** (trata erros 401)
- **Serviços de autenticação**:
  - `login(credentials)` - Fazer login
  - `register(userData)` - Registrar usuário
  - `logout()` - Fazer logout

### 3. Funcionalidades do Login
- ✅ **PreventDefault**: Formulário não recarrega a página
- ✅ **Axios**: Comunicação HTTP com o backend
- ✅ **Validação**: Campos obrigatórios e validação de email
- ✅ **Loading State**: Botão desabilitado durante requisição
- ✅ **Error Handling**: Exibição de erros do servidor
- ✅ **Token Storage**: Salva token no localStorage
- ✅ **Responsivo**: Funciona em desktop e mobile

## Como Usar

### 1. Instalar Dependências
```bash
pnpm install
```

### 2. Executar em Desenvolvimento
```bash
pnpm dev
```

### 3. Configurar Backend
Edite o arquivo `src/services/api.js` e ajuste a `baseURL` conforme necessário:
```javascript
const api = axios.create({
  baseURL: 'http://localhost:8000', // Ajuste aqui
  // ...
})
```

## Endpoints Esperados no Backend

O frontend espera os seguintes endpoints no backend:

### POST /auth/login
```json
{
  "email": "usuario@email.com",
  "password": "senha123"
}
```

**Resposta de sucesso:**
```json
{
  "token": "jwt_token_aqui",
  "user": {
    "id": 1,
    "email": "usuario@email.com",
    "name": "Nome do Usuário"
  }
}
```

### POST /auth/register
```json
{
  "email": "usuario@email.com",
  "password": "senha123",
  "name": "Nome do Usuário"
}
```

### POST /auth/logout
Endpoint para fazer logout (opcional)

## Recursos Implementados

- 🎨 **Design moderno** com gradientes e sombras
- 📱 **Responsivo** para mobile e desktop
- ⚡ **Performance** com lazy loading e otimizações
- 🔒 **Segurança** com interceptors para tokens
- 🚀 **UX** com estados de loading e feedback visual
- 🛡️ **Validação** de formulários
- 🌐 **Internacionalização** pronta (textos em português)

## Próximos Passos

1. **Implementar roteamento** (Vue Router)
2. **Adicionar página de registro**
3. **Implementar recuperação de senha**
4. **Adicionar testes unitários**
5. **Configurar CI/CD**
