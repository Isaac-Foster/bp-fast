#!/bin/bash

echo "🛑 Parando stack de observabilidade..."

# Parar os serviços
docker-compose down

echo "✅ Stack de observabilidade parada com sucesso!"
echo ""
echo "💡 Para remover os volumes também, execute:"
echo "   docker-compose down -v"
echo ""
echo "💡 Para remover as imagens também, execute:"
echo "   docker-compose down --rmi all"
