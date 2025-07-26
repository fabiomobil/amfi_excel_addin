# Referência Técnica de Scripts AmFi

Documentação completa para desenvolvedores sobre todos os scripts e APIs disponíveis no sistema AmFi.

## 🚀 Scripts de Produção

### scripts/run_monitoring.py
**Propósito**: Execução do monitoramento diário via API

```bash
# Execução básica
python scripts/run_monitoring.py

# Com logging detalhado
python scripts/run_monitoring.py --verbose

# Forçar re-execução (ignora cache diário)
python scripts/run_monitoring.py --force
```

**Parâmetros avançados:**
- `--debug`: Modo debug (usa test_pools.json)
- `--pool "Nome"`: Processar apenas pool específico
- `--output-dir path`: Diretório customizado para resultados
- `--timeout 300`: Timeout em segundos

**Retorno:**
- **Exit code 0**: Sucesso
- **Exit code 1**: Erro crítico
- **Exit code 2**: Erro de configuração

### scripts/run_dashboard.py
**Propósito**: Servidor web interativo do dashboard

```bash
# Servidor local (porta 8080)
python scripts/run_dashboard.py

# Porta customizada
python scripts/run_dashboard.py --port 9000

# Bind em interface específica
python scripts/run_dashboard.py --host 0.0.0.0 --port 8080
```

**Endpoints disponíveis:**
- `GET /`: Dashboard principal
- `GET /api/pools`: Lista de pools
- `GET /api/pools/{name}`: Dados específicos do pool
- `GET /api/violations`: Violações ativas
- `GET /health`: Health check

### scripts/generate_dashboard.py
**Propósito**: Geração de dashboard HTML estático

```bash
# HTML básico
python scripts/generate_dashboard.py

# Com dados históricos
python scripts/generate_dashboard.py --include-history

# Apenas violações
python scripts/generate_dashboard.py --violations-only

# Arquivo customizado
python scripts/generate_dashboard.py --output custom_dashboard.html
```

## 📅 Scripts de Análise Histórica

### scripts/amfi_monitor.py
**Propósito**: Monitor unificado para todos os cenários de monitoramento

```bash
# Pool específico (preview primeiro)
python scripts/amfi_monitor.py --pool "Baru Pool #2" --preview
python scripts/amfi_monitor.py --pool "Baru Pool #2" --commit

# Carga histórica completa
python scripts/amfi_monitor.py --historical --preview
python scripts/amfi_monitor.py --historical --commit

# Rotina diária
python scripts/amfi_monitor.py --routine daily --preview
python scripts/amfi_monitor.py --routine daily --commit

# Pool específico + data histórica
python scripts/amfi_monitor.py --pool "Baru Pool #2" --date "14/07/2025" --preview
```

**Parâmetros avançados:**
- `--no-backup`: Desabilitar backup automático
- `--dry-run`: Simular execução sem modificar arquivos
- `--preview-dir path`: Diretório customizado para previews

**Estrutura de saída:**
```
# Preview (temporário)
temp/previews/
├── 2025-07-26_preview.json

# Commit (definitivo)
data/output/monitoring_results/daily_consolidated/
├── 2025-07-26.json    # JSON enriquecido
├── backups/
│   └── 2025-07-26_backup_20250726_143022.json
```

## 🔧 APIs Programáticas

### Monitoramento Direto
```python
from src.monitor.orchestrator import run_monitoring, run_liquidity_analysis

# Interface completa
resultado = run_monitoring(
    pool_name="AFA Pool #1",    # Pool específico ou None
    data="14/07/2025"          # Data específica ou None
)

# Análise de liquidez apenas
resultado_liquidez = run_liquidity_analysis(
    pool_name="LeCapital Pool #1",
    data="15/07/2025"
)
```

### Carregamento de Dados
```python
from src.monitor.utils.data_loader import load_pool_data

# Carregar dados atuais
dados = load_pool_data()

# Carregar dados históricos
dados_historicos = load_pool_data(data="14/07/2025")

# Estrutura retornada
{
    "sucesso": bool,
    "pools_processados": ["Pool 1", "Pool 2"],
    "pools_configs": {"Pool 1": {...}},
    "csv_data": DataFrame,
    "xlsx_data": DataFrame,
    "xlsx_enriched": DataFrame  # Com dias_atraso, grupo_de_risco
}
```

### Monitores Específicos
```python
# Monitor de subordinação
from src.monitor.base.monitor_subordinacao_oop import SubordinationMonitor
monitor = SubordinationMonitor()
result = monitor.calculate_subordination(csv_data, config)

# Monitor de inadimplência
from src.monitor.base.monitor_inadimplencia_oop import run_delinquency_monitoring
result = run_delinquency_monitoring(csv_data, xlsx_data, config)

# Monitor de PDD
from src.monitor.base.monitor_pdd_oop import run_pdd_monitoring
result = run_pdd_monitoring(csv_data, xlsx_data, config)

# Monitor de concentração
from src.monitor.base.monitor_concentracao_oop import run_concentration_monitoring
result = run_concentration_monitoring(csv_data, xlsx_data, config)
```

## 🤖 Automação e Scheduling

### Cron Jobs (Linux/Mac)
```bash
# Monitoramento diário às 8h
0 8 * * * cd /path/to/amfi && python scripts/run_monitoring.py

# Histórico semanal aos domingos
0 9 * * 0 cd /path/to/amfi && python scripts/amfi_monitor.py --historical --commit

# Dashboard sempre ativo
@reboot cd /path/to/amfi && python scripts/run_dashboard.py
```

### Task Scheduler (Windows)
```cmd
# Criar tarefa diária
schtasks /create /tn "AmFi Daily Monitoring" /tr "python C:\amfi\scripts\run_monitoring.py" /sc daily /st 08:00

# Criar tarefa semanal
schtasks /create /tn "AmFi Weekly History" /tr "python C:\amfi\scripts\amfi_monitor.py --historical --commit" /sc weekly /d SUN /st 09:00
```

### Docker Automation
```dockerfile
# Dockerfile exemplo
FROM python:3.9
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

# Execução diária
CMD ["python", "scripts/run_monitoring.py"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  amfi-monitoring:
    build: .
    volumes:
      - ./data:/app/data
    environment:
      - PYTHONIOENCODING=utf-8
    restart: unless-stopped
```

## 🔍 Troubleshooting Avançado

### Logs e Debugging
```bash
# Habilitar logging detalhado
export AMFI_LOG_LEVEL=DEBUG
python scripts/run_monitoring.py

# Logs por categoria
export AMFI_LOG_MONITOR=DEBUG
export AMFI_LOG_DATA=INFO

# Arquivo de log customizado
export AMFI_LOG_FILE=/path/to/custom.log
```

### Verificação de Sistema
```python
# Health check completo
from src.monitor.utils.data_loader import load_pool_data
from src.monitor.orchestrator import run_monitoring

# Verificar carregamento
try:
    dados = load_pool_data()
    print(f"✅ Carregamento OK: {len(dados['pools_processados'])} pools")
except Exception as e:
    print(f"❌ Erro no carregamento: {e}")

# Verificar monitoramento
try:
    resultado = run_monitoring()
    print(f"✅ Monitoramento OK: {resultado['estatisticas']['taxa_sucesso']}% sucesso")
except Exception as e:
    print(f"❌ Erro no monitoramento: {e}")
```

### Performance Profiling
```python
import cProfile
import pstats
from src.monitor.orchestrator import run_monitoring

# Profile de execução
cp = cProfile.Profile()
cp.enable()
resultado = run_monitoring()
cp.disable()

# Análise de performance
stats = pstats.Stats(cp)
stats.sort_stats('cumulative')
stats.print_stats(10)  # Top 10 funções mais lentas
```

## 📊 Monitoramento de Sistema

### Métricas de Performance
```python
# Tempo de execução por pool
from datetime import datetime
start = datetime.now()
resultado = run_monitoring("AFA Pool #1")
end = datetime.now()
print(f"Tempo: {(end-start).total_seconds():.2f}s")

# Uso de memória
import psutil
import os
process = psutil.Process(os.getpid())
print(f"Memória: {process.memory_info().rss / 1024 / 1024:.1f} MB")
```

### Alertas de Sistema
```python
# Configurar alertas por email
from src.monitor.utils.alerts import log_alerta

# Alert customizado
log_alerta({
    "tipo": "erro_critico",
    "titulo": "Falha no Monitoramento",
    "mensagem": "Sistema não consegui processar dados",
    "detalhes": {"pool": "AFA Pool #1", "erro": "Timeout"}
})
```

## 🔐 Segurança e Compliance

### Audit Trail
Todos os scripts geram logs auditáveis em:
```
logs/
├── monitoring_YYYYMMDD.log     # Execuções diárias
├── historical_YYYYMMDD.log     # Processamento histórico
└── dashboard_access.log        # Acessos ao dashboard
```

### Backup e Recovery
```bash
# Backup de resultados
tar -czf backup_$(date +%Y%m%d).tar.gz data/output/

# Restore
tar -xzf backup_20250726.tar.gz
```

### Validação de Integridade
```python
# Verificar integridade dos dados
from src.monitor.utils.data_handler import data_validation

result = data_validation(csv_data, xlsx_data)
if not result['valid']:
    print(f"⚠️ Problemas encontrados: {result['issues']}")
```