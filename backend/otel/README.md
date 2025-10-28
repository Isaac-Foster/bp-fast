# 🔍 Stack de Observabilidade

Stack completa de observabilidade com **Grafana**, **Prometheus**, **Loki**, **Tempo** e **Jaeger** para monitoramento de aplicações.

## 📋 Componentes

| Serviço | Porta | Descrição |
|---------|-------|-----------|
| **Grafana** | 3000 | Dashboard e visualização de métricas, logs e traces |
| **Prometheus** | 9090 | Coleta e armazenamento de métricas |
| **Loki** | 3100 | Agregação de logs |
| **Tempo** | 3200 | Armazenamento de traces distribuídos |
| **Jaeger** | 16686 | Interface para visualização de traces |
| **Promtail** | 9080 | Coleta de logs dos containers |

## 🚀 Como Usar

### Iniciar a Stack

```bash
# Método 1: Script automático
./start.sh

# Método 2: Docker Compose manual
docker-compose up -d
```

### Parar a Stack

```bash
# Método 1: Script automático
./stop.sh

# Método 2: Docker Compose manual
docker-compose down
```

## 🌐 Acessos

### Grafana
- **URL**: http://localhost:3000
- **Usuário**: `admin`
- **Senha**: `admin123`

### Prometheus
- **URL**: http://localhost:9090
- **Targets**: http://localhost:9090/targets

### Loki
- **URL**: http://localhost:3100
- **API**: http://localhost:3100/ready

### Tempo
- **URL**: http://localhost:3200
- **API**: http://localhost:3200/ready

### Jaeger
- **URL**: http://localhost:16686
- **Interface**: http://localhost:16686/search

## 📊 Configuração

### Prometheus
- **Config**: `config/prometheus.yml`
- **Targets**: Configurado para monitorar aplicação backend na porta 8000
- **Retenção**: 200 horas

### Loki
- **Config**: `config/loki.yml`
- **Retenção**: 720 horas (30 dias)
- **Limites**: Configurados para desenvolvimento

### Tempo
- **Config**: `config/tempo.yml`
- **Retenção**: 1 hora para desenvolvimento
- **Protocolos**: Jaeger, OTLP, OpenCensus, Zipkin

### Grafana
- **Datasources**: Configurados automaticamente
- **Dashboards**: Provisionados automaticamente
- **Plugins**: Pie chart panel instalado

## 🔧 Integração com Aplicação

### Métricas (Prometheus)
Para expor métricas da sua aplicação Python:

```python
# Exemplo com prometheus_client
from prometheus_client import Counter, Histogram, start_http_server

# Métricas
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

# Iniciar servidor de métricas
start_http_server(8001)  # Porta para métricas
```

### Logs (Loki)
Configure sua aplicação para enviar logs estruturados:

```python
import logging
import json

# Configurar logging estruturado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

logger = logging.getLogger(__name__)
logger.info("Aplicação iniciada", extra={"service": "backend-app"})
```

### Traces (Tempo)
Para instrumentar sua aplicação com traces:

```python
# Exemplo com OpenTelemetry
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Configurar tracer
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Configurar exportador para Tempo
otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4317")
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)
```

## 📁 Estrutura de Arquivos

```
otel/
├── docker-compose.yml                    # Orquestração dos serviços
├── start.sh                             # Script de inicialização
├── stop.sh                              # Script de parada
├── README.md                            # Este arquivo
└── config/
    ├── prometheus.yml                   # Configuração do Prometheus
    ├── loki.yml                        # Configuração do Loki
    ├── tempo.yml                       # Configuração do Tempo
    ├── promtail.yml                    # Configuração do Promtail
    └── grafana/
        └── provisioning/
            ├── datasources/
            │   └── datasources.yml     # Datasources do Grafana
            └── dashboards/
                └── dashboards.yml      # Configuração de dashboards
        └── dashboards/
            └── observability-overview.json  # Dashboard exemplo
```

## 🛠️ Comandos Úteis

### Ver logs dos serviços
```bash
# Todos os serviços
docker-compose logs -f

# Serviço específico
docker-compose logs -f grafana
docker-compose logs -f prometheus
docker-compose logs -f loki
docker-compose logs -f tempo
```

### Reiniciar serviço específico
```bash
docker-compose restart grafana
```

### Ver status dos containers
```bash
docker-compose ps
```

### Limpar volumes (cuidado!)
```bash
docker-compose down -v
```

## 🔍 Troubleshooting

### Porta já em uso
Se alguma porta estiver em uso, edite o `docker-compose.yml` e altere as portas:

```yaml
ports:
  - "3001:3000"  # Grafana na porta 3001
```

### Problemas de permissão
```bash
sudo chown -R 472:472 config/grafana/
```

### Limpar cache do Grafana
```bash
docker-compose exec grafana grafana-cli admin reset-admin-password admin123
```

## 📈 Próximos Passos

1. **Configurar alertas** no Prometheus
2. **Criar dashboards customizados** no Grafana
3. **Integrar com aplicação backend** (métricas, logs, traces)
4. **Configurar backup** dos dados
5. **Adicionar autenticação** nos serviços
6. **Configurar SSL/TLS** para produção

## 🤝 Contribuição

Para melhorar esta stack de observabilidade:

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

---

**Desenvolvido com ❤️ para facilitar o monitoramento de aplicações**
