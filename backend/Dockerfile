# Dockerfile para o backend do projeto bp-fast
# Usa Python 3.12 e uv para gerenciamento de dependências
#
# IMPORTANTE: Este Dockerfile deve ser construído a partir da RAIZ do projeto
# (onde está o pyproject.toml), não do diretório backend/
#
# Comando para construir:
#   docker build -f backend/Dockerfile -t bp-fast-backend .
#
# Ou usando docker-compose (recomendado):
#   docker-compose -f backend/compose.yaml build

# Estágio 1: Builder - instala dependências
FROM python:3.12-slim as builder

# Instala dependências do sistema necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instala uv (ferramenta rápida para gerenciar dependências Python)
# O uv só é necessário neste estágio para instalar as dependências
# No estágio final, usamos apenas o .venv criado aqui
RUN pip install --no-cache-dir uv

# Define o diretório de trabalho
WORKDIR /app

# Copia arquivos de dependências da raiz do projeto
COPY pyproject.toml uv.lock ./

# Instala dependências usando uv
RUN uv sync --frozen --no-dev

# Estágio 2: Runtime - imagem final otimizada
FROM python:3.12-slim

# Instala dependências de runtime do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Cria diretório de logs
RUN mkdir -p /app/backend/logs

# Define o diretório de trabalho
WORKDIR /app

# Copia o ambiente virtual do builder (já com todas as dependências instaladas)
COPY --from=builder /app/.venv /app/.venv

# Copia o código da aplicação (backend está na raiz do projeto)
COPY backend/ ./backend/

# Adiciona o .venv ao PATH para usar os binários instalados
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app/backend:/app" \
    PYTHONUNBUFFERED=1

# Expõe a porta da aplicação
EXPOSE 3000

# Healthcheck - verifica se a aplicação está respondendo
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import socket; s=socket.socket(); s.settimeout(5); s.connect(('localhost', 3000)); s.close()" || exit 1

# Comando para iniciar a aplicação
# O app está em backend/src/__init__.py e é chamado como 'app'
# Como o PYTHONPATH inclui /app/backend, podemos usar 'src:app'
WORKDIR /app/backend
CMD ["uvicorn", "src:app", "--host", "0.0.0.0", "--port", "3000"]
