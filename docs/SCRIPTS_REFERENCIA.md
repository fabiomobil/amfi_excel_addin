# Scripts de Referência - Sistema AmFi

## 📋 Índice de Scripts

### 🎯 Scripts Principais

| Script | Função | Uso |
|--------|---------|-----|
| `orchestrator.py` | Motor de monitoramento | Processamento principal |
| `generate_table_dashboard.py` | Dashboard web | Interface visual |
| `run_full_historical_monitoring.py` | Processamento paralelo | Dados históricos completos |
| `run_sequential_historical_monitoring.py` | Processamento sequencial | Últimos 5 dias |

### 🛠️ Scripts Utilitários

| Script | Função | Localização |
|--------|---------|-------------|
| `exemplo_uso.py` | Exemplos práticos | `/monitor/` |
| `data_loader.py` | Carregamento de dados | `/monitor/utils/` |
| `data_converters.py` | Conversões brasileiras | `/monitor/utils/` |
| `alerts.py` | Sistema de logs | `/monitor/utils/` |

## 🚀 Scripts Principais

### 1. orchestrator.py

**Localização**: `/mnt/c/amfi/monitor/orchestrator.py`

**Função**: Motor principal do sistema de monitoramento

**Uso Básico**:
```python
import orchestrator

# Todos os pools
resultado = orchestrator.run_monitoring()

# Pool específico  
resultado = orchestrator.run_monitoring("AFA Pool #1")

# Com debug
resultado = orchestrator.run_monitoring(debug=True)
```

**Características**:
- **Arquitetura OOP**: Classes especializadas por monitor
- **Fallback automático**: Funciona em qualquer ambiente
- **Enriquecimento progressivo**: Reutiliza cálculos
- **Configuração flexível**: JSON por pool

### 2. generate_table_dashboard.py

**Localização**: `/mnt/c/amfi/generate_table_dashboard.py`

**Função**: Gera dashboard web interativo

**Uso**:
```bash
python3 generate_table_dashboard.py
```

**Saída**: `/mnt/c/amfi/data/output/monitoring_results/dashboard/table_dashboard.html`

**Recursos**:
- **Interface responsiva**: HTML + CSS + JavaScript
- **Drilldown interativo**: Análise detalhada por pool
- **Dados históricos**: Últimos 7 dias
- **Auto-refresh**: Atualização automática
- **Cálculos inteligentes**: Aporte vs Saque disponível

### 3. run_full_historical_monitoring.py

**Localização**: `/mnt/c/amfi/run_full_historical_monitoring.py`

**Função**: Processamento histórico completo com paralelização

**Uso**:
```bash
# Padrão (4 workers)
python3 run_full_historical_monitoring.py

# 12 workers simultâneos
python3 run_full_historical_monitoring.py --max-workers 12

# Pular datas processadas
python3 run_full_historical_monitoring.py --skip-existing

# Apenas testar
python3 run_full_historical_monitoring.py --dry-run
```

**Características**:
- **Paralelização**: ThreadPoolExecutor
- **Descoberta automática**: Encontra todas as datas
- **Técnica de movimentação**: Pasta 'files' para histórico
- **Thread-safe**: Logs e progress tracking
- **Modo debug**: Desabilita temporariamente

### 4. run_sequential_historical_monitoring.py

**Localização**: `/mnt/c/amfi/run_sequential_historical_monitoring.py`

**Função**: Processamento sequencial dos últimos 5 dias

**Uso**:
```bash
python3 run_sequential_historical_monitoring.py
```

**Características**:
- **Sequencial**: Um arquivo por vez
- **Últimos 5 dias**: Período limitado
- **Menor overhead**: Para datasets menores
- **Logs detalhados**: Progress tracking

## 🔧 Scripts de Configuração

### Estrutura de Arquivos de Config

```
config/
├── monitoring/
│   ├── test_pools.json           # Modo debug
│   ├── ignore_pools.json         # Pools ignorados
│   └── _test_pools.json.backup_* # Backups automáticos
└── pools/
    ├── {Pool Name}.json          # Config específica
    └── README.md                 # Documentação
```

### test_pools.json - Controle de Debug

```json
{
  "metadata": {
    "description": "Configuração de debug para sistema de monitoramento",
    "version": "2.0",
    "last_updated": "2025-01-07"
  },
  "debug_pools": [
    "AFA Pool #1",
    "LeCapital Pool #1", 
    "Up Vendas Pool #2",
    "E-ctare Pool #1"
  ]
}
```

**Estados**:
- **Debug Ativo**: `debug_pools` com pools listados → Processa apenas estes
- **Debug Inativo**: `debug_pools` vazio ou arquivo renomeado → Processa todos

## 📊 Scripts de Análise

### Monitor Classes (OOP)

**Localização**: `/mnt/c/amfi/monitor/base/`

| Classe | Arquivo | Função |
|--------|---------|---------|
| `MonitorSubordinacao` | `monitor_subordinacao.py` | Índice SR |
| `MonitorInadimplencia` | `monitor_inadimplencia.py` | Janelas temporais |
| `MonitorPDD` | `monitor_pdd.py` | Provisão por grupos |
| `MonitorConcentracao` | `monitor_concentracao.py` | Limites por sacado |

### Exemplo de Uso Direto:

```python
from monitor.base.monitor_subordinacao import MonitorSubordinacao

# Inicializar monitor
monitor = MonitorSubordinacao()

# Carregar dados
csv_data = load_csv_data()
xlsx_data = load_xlsx_data()
config = load_pool_config("AFA Pool #1")

# Executar análise
resultado = monitor.analisar(csv_data, xlsx_data, config)

# Acessar resultados
print(f"Status: {resultado['status_geral']}")
print(f"IS: {resultado['subordination_ratio_percent']}%")
```

## 🗂️ Scripts Utilitários

### data_loader.py

**Funções principais**:
```python
# Carregamento inteligente
csv_data, xlsx_data = load_data()

# Configurações por pool
configs = load_pools_configs()

# Modo debug automático
pools_to_process = get_pools_list(debug_mode=False)
```

### data_converters.py

**Conversões brasileiras**:
```python
# Números brasileiros → float
valor = convert_brazilian_number("1.234.567,89")  # → 1234567.89

# Datas brasileiras → datetime  
data = convert_brazilian_date("15/07/2025")  # → datetime

# Percentuais → decimal
percent = convert_percentage("12,34%")  # → 0.1234
```

### alerts.py

**Sistema de logs**:
```python
from monitor.utils.alerts import AlertManager

# Configurar alertas
alerts = AlertManager()

# Log estruturado
alerts.log_info("Processamento iniciado", pool="AFA Pool #1")
alerts.log_warning("Limite próximo", valor_atual=19.5, limite=20.0)
alerts.log_error("Falha no carregamento", erro=str(e))

# Recuperar alertas
todos_alertas = alerts.get_all_alerts()
alertas_pool = alerts.get_pool_alerts("AFA Pool #1")
```

## ⚡ Scripts de Performance

### Otimizações Implementadas

#### Conversões Vetorizadas
```python
# Antes: Loop lento
for index, row in df.iterrows():
    df.at[index, 'valor'] = convert_brazilian_number(row['valor_str'])

# Depois: Vetorizado (50-100x mais rápido)
df['valor'] = df['valor_str'].apply(convert_brazilian_number_vectorized)
```

#### Enriquecimento Progressivo
```python
# Calcula uma vez, reutiliza para todos os monitores
xlsx_enriched = enrich_xlsx_data(xlsx_data, csv_data)

# Cada monitor recebe dados já enriquecidos
resultado_sub = monitor_sub.analisar(csv_data, xlsx_enriched, config)
resultado_inad = monitor_inad.analisar(csv_data, xlsx_enriched, config)
```

#### Processamento Paralelo
```python
# ThreadPoolExecutor para I/O bound
with ThreadPoolExecutor(max_workers=12) as executor:
    futures = [executor.submit(process_date, date) for date in dates]
    
# Tracking thread-safe
with threading.Lock():
    progress_counter.increment()
    print_progress_update()
```

## 🔍 Scripts de Debug

### Modo Debug Ativo

```python
# Verificar status
def check_debug_mode():
    try:
        with open('config/monitoring/test_pools.json', 'r') as f:
            config = json.load(f)
            return len(config.get('debug_pools', [])) > 0
    except FileNotFoundError:
        return False  # Debug inativo

# Ativar debug temporariamente
def enable_debug_temporarily():
    backup_file = f"_test_pools.json.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.move('config/monitoring/test_pools.json', backup_file)
    return backup_file

# Restaurar debug
def restore_debug(backup_file):
    shutil.move(backup_file, 'config/monitoring/test_pools.json')
```

### Logs de Desenvolvimento

```bash
# Logs detalhados do sistema
tail -f /mnt/c/amfi/logs/full_historical_monitoring.log

# Filtrar por worker específico
grep "DateWorker_0" /mnt/c/amfi/logs/full_historical_monitoring.log

# Apenas erros
grep "ERROR" /mnt/c/amfi/logs/full_historical_monitoring.log
```

## 📈 Scripts de Relatórios

### Relatório de Performance

```python
def generate_performance_report():
    return {
        "processamento_total": "2min 15s",
        "pools_processados": 73,
        "workers_utilizados": 12,
        "taxa_sucesso": "85.2%",
        "throughput": "32.4 pools/min",
        "memoria_pico": "1.2GB",
        "cpu_medio": "78%"
    }
```

### Relatório de Compliance

```python
def generate_compliance_report():
    return {
        "data_referencia": "2025-07-19",
        "pools_total": 7,
        "pools_enquadrados": 4,
        "pools_violados": 3,
        "taxa_compliance": "57.1%",
        "violacoes_criticas": 1,
        "violacoes_minimas": 2,
        "valor_total_aportes": "R$ 6.038.735,78"
    }
```

## 🚀 Execução em Produção

### Script de Deploy
```bash
#!/bin/bash
# deploy_amfi.sh

# Backup configurações
cp config/monitoring/test_pools.json config/monitoring/test_pools.json.backup

# Limpar modo debug
echo '{"debug_pools": []}' > config/monitoring/test_pools.json

# Executar processamento completo
python3 run_full_historical_monitoring.py --max-workers 8

# Gerar dashboard
python3 generate_table_dashboard.py

# Restaurar configurações
mv config/monitoring/test_pools.json.backup config/monitoring/test_pools.json

echo "Deploy concluído: $(date)"
```

### Monitoramento Contínuo
```bash
#!/bin/bash
# monitor_system.sh

while true; do
    # Verificar se há novos dados
    if [ "$(find data/input/csv/ -name '*.csv' -newer last_run.marker)" ]; then
        echo "Novos dados detectados, iniciando processamento..."
        python3 orchestrator.py
        python3 generate_table_dashboard.py
        touch last_run.marker
    fi
    
    sleep 300  # Verificar a cada 5 minutos
done
```