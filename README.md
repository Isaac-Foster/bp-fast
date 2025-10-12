# BP-Fast - Sistema de Autenticação Seguro

Um sistema de autenticação robusto e seguro construído com FastAPI, Vue.js e Redis, implementando as melhores práticas de segurança para autenticação moderna.

## 🎯 Objetivo

Este projeto serve como um template completo para sistemas de autenticação que implementam:

- **Autenticação JWT com invalidação por sessão**
- **Autenticação de dois fatores (2FA) com OTP**
- **Sistema de fingerprint para detecção de dispositivos**
- **Recuperação de senha via email**
- **Verificação de email para ativação de conta**
- **Monitoramento com OpenTelemetry**

## 🏗️ Arquitetura

### Backend (FastAPI + Python)
```
backend/
├── src/
│   ├── adapters/          # Implementações concretas
│   ├── core/              # Lógica de negócio
│   ├── infra/             # Infraestrutura
│   │   ├── connect/       # Conexões (DB, Redis)
│   │   ├── model/         # Modelos SQLAlchemy
│   │   ├── security/      # Módulos de segurança
│   │   │   ├── auth/      # JWT Manager
│   │   │   ├── session/   # Gerenciamento de sessões
│   │   │   ├── hashpass/  # Hash de senhas (bcrypt)
│   │   │   └── otp/       # Autenticação 2FA
│   │   └── security/
│   ├── interfaces/        # Controllers e Schemas
│   └── utils/             # Utilitários
├── tests/                 # Testes automatizados
└── otel/                  # Configuração OpenTelemetry
```

### Frontend (Vue.js)
```
frontend/
├── src/
│   ├── components/        # Componentes Vue
│   ├── services/          # API Services
│   └── assets/           # Recursos estáticos
└── public/               # Arquivos públicos
```

## 🔐 Recursos de Segurança

### 1. Sistema de Sessões com Redis
- **Session ID UUIDv7**: Identificador único para cada sessão
- **Invalidação centralizada**: JWT invalidadas via Redis, não no servidor
- **TTL configurável**: Sessões expiram automaticamente
- **Mapeamento bidirecional**: `session_id → user_id` e `user_id → session_id`

### 2. Autenticação JWT Aprimorada
```python
# Claims do JWT incluem session_id
{
    "id": user_id,
    "session_id": "uuid-v7-session-id",
    "exp": timestamp,
    "iat": timestamp
}
```

### 3. Autenticação de Dois Fatores (2FA)
- **TOTP com pyotp**: Códigos de 6 dígitos válidos por 30 segundos
- **QR Code**: Geração automática para Google Authenticator/Authy
- **Secret Base32**: Armazenamento seguro do secret no banco

### 4. Sistema de Fingerprint
- **Detecção de dispositivo**: Coleta informações do navegador/dispositivo
- **Notificações**: Alerta quando fingerprint não é reconhecido
- **Suporte desktop/mobile**: Adaptação automática ao tipo de dispositivo

### 5. Hash de Senhas
- **bcrypt**: Algoritmo seguro com salt automático
- **Validação de força**: Senhas devem atender critérios rigorosos
- **Verificação**: Comparação segura sem exposição da senha

### 6. Recuperação de Senha
- **Token temporário**: Link seguro com expiração
- **Email de recuperação**: Processo via email com validação
- **Reset seguro**: Nova senha com validação de força

### 7. Verificação de Email
- **Ativação de conta**: Email obrigatório para ativar conta
- **Validação de entrega**: Verificação se email é válido e entregável
- **Token de ativação**: Link seguro para ativação

## 🚀 Tecnologias

### Backend
- **FastAPI**: Framework web moderno e rápido
- **SQLAlchemy**: ORM com suporte assíncrono
- **PostgreSQL**: Banco de dados principal
- **Redis**: Cache e gerenciamento de sessões
- **JWT**: Tokens de autenticação
- **bcrypt**: Hash de senhas
- **pyotp**: Geração e validação de OTP
- **Alembic**: Sistema de migrações de banco de dados
- **OpenTelemetry**: Observabilidade (traces, logs, métricas)

### Frontend
- **Vue.js 3**: Framework reativo
- **Vite**: Build tool moderno
- **Axios**: Cliente HTTP
- **Tailwind CSS**: Framework CSS (recomendado)

### DevOps & Observabilidade
- **Docker Compose**: Orquestração de serviços
- **Grafana**: Dashboards de monitoramento
- **Prometheus**: Coleta de métricas
- **Loki**: Agregação de logs
- **Tempo**: Rastreamento distribuído

## 📋 Fluxo de Autenticação

```mermaid
graph TD
    A[Login: username + password] --> B[Verificar credenciais]
    B --> C[Gerar session_id UUIDv7]
    C --> D[Armazenar sessão no Redis]
    D --> E[Gerar JWT com session_id]
    E --> F[Verificar 2FA OTP]
    F --> G[Validar fingerprint]
    G --> H[Login realizado]
    
    I[Requisição autenticada] --> J[Validar JWT]
    J --> K[Extrair session_id]
    K --> L[Verificar sessão no Redis]
    L --> M[Sessão válida?]
    M -->|Sim| N[Processar requisição]
    M -->|Não| O[Retornar 401 Unauthorized]
```

## 🛠️ Instalação e Configuração

### Pré-requisitos
- Python 3.12+
- Node.js 18+
- Docker e Docker Compose
- PostgreSQL 15+
- Redis 6+

### 1. Clone o repositório
```bash
git clone <repository-url>
cd bp-fast
```

### 2. Configuração do Backend
```bash
cd backend

# Copie o arquivo de exemplo
cp env.example .env

# Edite as configurações
nano .env
```

**Configurações importantes no `.env`:**
```env
# JWT Configuration
jwt_secret=your-super-secret-key-here
jwt_algorithm=HS256
jwt_expiration_time=3600

# Redis Configuration
redis_host=localhost
redis_port=6379
redis_db=0
ttl_redis=3600

# Database Configuration
postgres_drivername=postgresql+psycopg2
postgres_db_user=user
postgres_db_password=secure_password
postgres_db_host=localhost
postgres_db_port=5432
postgres_db_name=bp_fast_db
```

### 3. Instalação das dependências
```bash
# Backend
cd backend
uv sync

# Frontend
cd ../frontend
pnpm install
```

### 4. Executar com Docker Compose
```bash
# Na raiz do projeto
docker compose up -d
```

### 5. Executar migrações com Alembic
```bash
cd backend

# Gerar nova migração (quando houver mudanças nos modelos)
alembic revision --autogenerate -m "Descrição da mudança"

# Aplicar migrações pendentes
alembic upgrade head

# Ver histórico de migrações
alembic history

# Voltar para uma versão específica (se necessário)
alembic downgrade -1
```

**Configuração do Alembic:**
- Migrações automáticas baseadas nos modelos SQLAlchemy
- Versionamento do banco de dados
- Rollback seguro de mudanças
- Histórico completo de alterações

### 6. Iniciar aplicação
```bash
# Backend
cd backend
uvicorn src:app --reload

# Frontend (em outro terminal)
cd frontend
pnpm dev
```

## 📊 Monitoramento

O projeto inclui configuração completa do OpenTelemetry com:

- **Grafana**: Dashboards para métricas e logs
- **Prometheus**: Coleta de métricas da aplicação
- **Loki**: Agregação e consulta de logs
- **Tempo**: Rastreamento distribuído de requisições

### Acessar dashboards:
- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090
- Loki: http://localhost:3100

## 🧪 Testes

```bash
# Executar todos os testes
cd backend
pytest --cov -vv

# Executar testes específicos
pytest tests/test_auth.py -v

# Gerar relatório de cobertura
coverage html

# Verificar cobertura no terminal
coverage report
```

## 📈 Progresso do Projeto

Veja o arquivo [TODO.md](./TODO.md) para acompanhar o progresso de desenvolvimento e próximas funcionalidades.

## 📚 API Endpoints

### Autenticação
- `POST /api/auth/signup` - Registro de usuário
- `POST /api/auth/signin` - Login
- `POST /api/auth/logout` - Logout
- `POST /api/auth/verify-email` - Verificação de email
- `POST /api/auth/reset-password` - Solicitar reset de senha
- `POST /api/auth/confirm-reset` - Confirmar reset de senha

### 2FA
- `POST /api/auth/otp/setup` - Configurar 2FA
- `POST /api/auth/otp/verify` - Verificar código OTP
- `GET /api/auth/otp/qr` - Obter QR Code para 2FA

### Fingerprint
- `POST /api/auth/fingerprint/register` - Registrar fingerprint
- `POST /api/auth/fingerprint/verify` - Verificar fingerprint

### Usuário
- `GET /api/user/profile` - Perfil do usuário
- `PUT /api/user/profile` - Atualizar perfil
- `POST /api/user/change-password` - Alterar senha

## 🔒 Considerações de Segurança

### Implementadas
- ✅ Hash de senhas com bcrypt
- ✅ JWT com invalidação por sessão
- ✅ Rate limiting (recomendado implementar)
- ✅ Validação de entrada rigorosa
- ✅ Headers de segurança
- ✅ CORS configurado
- ✅ Logs de segurança

### Recomendações Adicionais
- Implementar rate limiting
- Adicionar captcha para tentativas de login
- Configurar HTTPS em produção
- Implementar logging de auditoria
- Adicionar headers de segurança (HSTS, CSP)
- Configurar backup automático do Redis

## 📝 Estrutura do Banco de Dados

### Tabela `users`
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(64) UNIQUE NOT NULL,
    password VARCHAR(128) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    logged_in BOOLEAN DEFAULT FALSE,
    secret_otp VARCHAR(128),
    otp_enabled BOOLEAN DEFAULT FALSE,
    allowed BOOLEAN DEFAULT TRUE,
    attempts INTEGER DEFAULT 0,
    blocked BOOLEAN DEFAULT FALSE,
    email_verified BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Tabela `fingerprints`
```sql
CREATE TABLE fingerprints (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    fingerprint VARCHAR(255) NOT NULL,
    device_type VARCHAR(50),
    allowed BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🆘 Suporte

Para dúvidas ou problemas:
1. Verifique a documentação
2. Procure nas issues existentes
3. Crie uma nova issue com detalhes do problema

---

**Desenvolvido com ❤️ para segurança e performance**
