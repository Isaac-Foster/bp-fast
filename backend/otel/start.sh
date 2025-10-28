#!/bin/bash

echo "🚀 Iniciando stack de observabilidade..."

# Verificar se o Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker não está rodando. Por favor, inicie o Docker primeiro."
    exit 1
fi

# Criar volumes se não existirem
echo "📦 Criando volumes..."
docker volume create prometheus_data 2>/dev/null || true
docker volume create loki_data 2>/dev/null || true
docker volume create tempo_data 2>/dev/null || true
docker volume create grafana_data 2>/dev/null || true

# Iniciar os serviços
echo "🔧 Iniciando serviços..."
docker-compose up -d

# Aguardar os serviços ficarem prontos
echo "⏳ Aguardando serviços ficarem prontos..."
sleep 10

# Verificar status dos serviços
echo "📊 Status dos serviços:"
docker-compose ps

echo ""
echo "✅ Stack de observabilidade iniciada com sucesso!"
echo ""
echo "🌐 Acesse os serviços:"
echo "   📊 Grafana:     http://localhost:3000 (admin/admin123)"
echo "   📈 Prometheus:  http://localhost:9090"
echo "   📝 Loki:        http://localhost:3100"
echo "   🔍 Tempo:       http://localhost:3200"
echo "   🕵️  Jaeger:      http://localhost:16686"
echo ""
echo "Para parar os serviços: docker-compose down"
echo "Para ver logs: docker-compose logs -f [serviço]"
