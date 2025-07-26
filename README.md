# Sistema de Monitoramento AmFi

## 🎯 Visão Geral

Sistema completo de monitoramento de pools de recebíveis com dashboard interativo, processamento histórico paralelo e análise de compliance em tempo real.

## 🚀 Quick Start

### 1. Monitoramento Diário
```bash
# Execução completa
python scripts/run_monitoring.py

# Dashboard interativo
python scripts/run_dashboard.py
# Acesse: http://localhost:8080
```

### 2. Análise Histórica (Monitor Unificado)
```python
# Importar no Spyder/Cursor (Recomendado)
from scripts.amfi_monitor import AmFiMonitor
monitor = AmFiMonitor()

# Preview seguro primeiro
preview = monitor.run_single_pool("Baru Pool #2", date="14/07/2025", mode='preview')

# Commit após análise
commit = monitor.run_single_pool("Baru Pool #2", date="14/07/2025", mode='commit')
```

### 2b. Análise Histórica (CLI)
```bash
# Preview primeiro
python scripts/amfi_monitor.py --pool "Baru Pool #2" --date "14/07/2025" --preview

# Commit após aprovação
python scripts/amfi_monitor.py --pool "Baru Pool #2" --date "14/07/2025" --commit
```

### 3. Uso Programático
```python
from src.monitor.orchestrator import run_monitoring

# Monitoramento atual
resultado = run_monitoring()  # Todos os pools
resultado = run_monitoring("AFA Pool #1")  # Pool específico

# NOVA: Análise histórica
resultado = run_monitoring(data="14/07/2025")  # Todos os pools, data específica
resultado = run_monitoring("Baru Pool #2", data="15/07/2025")  # Pool + data
```

### 2. Dashboard Interativo
```bash
python3 scripts/run_dashboard.py
# Acesse: http://localhost:8080
```

### 3. Processamento Histórico (Monitor Unificado)
```python
# Carga histórica completa (Recomendado)
from scripts.amfi_monitor import AmFiMonitor
monitor = AmFiMonitor()

# Preview todas as datas
preview = monitor.run_historical_load(mode='preview')

# Commit após análise
commit = monitor.run_historical_load(mode='commit')
```

## 📊 Funcionalidades Principais

### ✅ Monitores Implementados
- **📈 Subordinação**: Índice SR com limites mínimo/crítico
- **💸 Inadimplência**: Janelas configuráveis + enriquecimento progressivo
- **📋 PDD**: Provisão por grupos de risco
- **🎯 Concentração**: Limites individuais e top-N por sacado/cedente

### ✅ Dashboard Web
- **Interface Responsiva**: HTML + CSS + JavaScript
- **Drilldown Interativo**: Análise detalhada por pool
- **Histórico Temporal**: Últimos 7 dias por pool
- **Status Visual**: VIOLADO CRÍTICO/MÍNIMO, ENQUADRADO
- **Cálculos Inteligentes**: Aporte para enquadrar vs Saque disponível
- **Auto-refresh**: Atualização automática a cada 5 minutos

### ✅ Processamento Histórico
- **Paralelização**: Até 12 workers simultâneos
- **Descoberta Automática**: Encontra todas as datas disponíveis
- **Técnica de Movimentação**: Sistema de pastas 'files' para dados históricos
- **Thread-safe**: Logs e progress tracking seguros
- **Modo Debug**: Removível para processar todos os 77+ pools

## 🏗️ Arquitetura

```
amfi/
├── 📁 monitor/                    # Sistema OOP de monitoramento
│   ├── orchestrator.py           # 🎯 Interface principal
│   ├── exemplo_uso.py             # 📖 Exemplos práticos
│   ├── base/                      # 🔧 Monitores OOP
│   │   ├── base_monitor.py        # 📋 Classe base
│   │   ├── result_builder.py      # 🔄 Padronização
│   │   └── monitor_*_oop.py       # 📊 Monitores específicos
│   └── utils/                     # 🛠️ Utilitários
│       ├── data_loader.py         # 📥 Carregamento
│       ├── data_converters.py     # 🔄 Conversões brasileiras
│       └── alerts.py              # 📢 Sistema de logs
├── 📁 config/                     # ⚙️ Configurações
│   ├── monitoring/                # 🔧 Controle do sistema
│   │   ├── test_pools.json        # 🐛 Modo debug (removível)
│   │   └── ignore_pools.json      # ❌ Pools ignorados
│   └── pools/                     # 🏊 Configuração por pool
│       └── {Pool Name}.json       # 📋 Config específica
├── 📁 data/                       # 💾 Dados
│   ├── input/                     # 📥 Dados de entrada
│   │   ├── csv/files/             # 📂 CSVs históricos
│   │   └── xlsx/files/            # 📂 XLSXs históricos
│   └── output/                    # 📤 Resultados
│       └── monitoring_results/    # 📊 Dados processados
│           ├── daily_consolidated/ # 📅 JSONs por data
│           └── dashboard/         # 🌐 HTML gerado
├── 📁 docs/                       # 📚 Documentação
│   ├── PROCESSAMENTO_HISTORICO.md # 📖 Guia de processamento
│   ├── DASHBOARD_GUIA.md          # 🎨 Guia do dashboard
│   └── SCRIPTS_REFERENCIA.md     # 🔧 Referência de scripts
├── 📁 logs/                       # 📜 Logs do sistema
├── 📁 scripts/                    # 🚀 Entry points executáveis
│   ├── run_monitoring.py          # 📊 API de monitoramento
│   ├── run_dashboard.py           # 🌐 Servidor web do dashboard
│   └── generate_dashboard.py      # 📋 Gerador de dashboard HTML
├── scripts/amfi_monitor.py        # 🎯 Monitor unificado (6 cenários)
└── README.md                      # 📋 Este arquivo
```

## 📈 Performance

### ⚡ Otimizações Implementadas
- **Conversões Vetorizadas**: 50-100x mais rápido que loops
- **Enriquecimento Progressivo**: Cálculos reutilizados entre monitores
- **Processamento Paralelo**: ThreadPoolExecutor para I/O
- **Código Reduzido**: 40% menos linhas no orchestrator

### 📊 Métricas Típicas
- **Processamento Completo**: 18 datas em 2-4 minutos (12 workers)
- **Taxa de Sucesso**: 77-85% (dependendo da qualidade dos dados)
- **Pools por Minuto**: 25-35 pools/min
- **Dashboard**: Geração em <5 segundos

## ⚙️ Configuração

### 🐛 Modo Debug
```json
// config/monitoring/test_pools.json
{
  "debug_pools": []  // Vazio = todos os pools, ou remover arquivo
}
```

### 🏊 Configuração por Pool
```json
// config/pools/AFA Pool #1.json
{
  "subordinacao": {
    "limite_minimo": 0.25,
    "limite_critico": 0.20
  },
  "concentracao": {
    "limite_individual": 0.05,
    "limite_top10": 0.30
  }
}
```

### 🔧 Controle de Paralelização
- **CPU-bound**: workers = núcleos da CPU
- **I/O-bound**: workers = 2x núcleos da CPU  
- **Padrão**: 4 workers
- **Máximo testado**: 12 workers

## 📊 Estrutura de Resultados

### JSON Consolidado Diário
```json
{
  "2025-07-19": {
    "AFA Pool #1": {
      "subordinacao": {
        "valor_atual": 9.83,
        "status": "VIOLADO CRÍTICO",
        "dias_consecutivos": 4,
        "aporte_enquadrar": 5973648.94
      }
    }
  }
}
```

### Dashboard HTML
- **Tabela Principal**: Status, dias consecutivos, valores financeiros
- **Drilldown**: Dados detalhados + histórico por pool
- **Responsivo**: Desktop, tablet e mobile
- **Auto-refresh**: Atualização automática

## 🔧 Comandos Principais

### Monitoramento
```bash
# Execução via script (recomendado)
python3 scripts/run_monitoring.py

# Execução programática
python3 -c "from src.monitor.orchestrator import run_monitoring; run_monitoring()"

# Pool específico
python3 -c "from src.monitor.orchestrator import run_monitoring; run_monitoring('AFA Pool #1')"

# Análise histórica
python3 -c "from src.monitor.orchestrator import run_monitoring; run_monitoring('AFA Pool #1', data='14/07/2025')"
```

### Dashboard
```bash
# Servidor web interativo
python3 scripts/run_dashboard.py
# Acesse: http://localhost:8080

# Ou gerar HTML estático
python3 scripts/generate_dashboard.py
```

### Processamento Histórico (Monitor Unificado)
```python
# Interface programática unificada (Recomendado)
from scripts.amfi_monitor import AmFiMonitor
monitor = AmFiMonitor()

# Carga histórica completa
historical = monitor.run_historical_load(mode='preview')  # Preview primeiro
historical = monitor.run_historical_load(mode='commit')   # Aplicar mudanças

# Período específico
period = monitor.run_date_range(
    start_date="14/07/2025", 
    end_date="18/07/2025", 
    mode='preview'
)
```

### Processamento Histórico (CLI)
```bash
# CLI alternativo
python scripts/amfi_monitor.py --historical --preview
python scripts/amfi_monitor.py --historical --commit

```

## 🛠️ Troubleshooting

### Problemas Comuns

**📊 Dashboard mostra poucos pools**
```bash
# Verificar modo debug
cat config/monitoring/test_pools.json
# Solução: Remover arquivo ou esvaziar debug_pools
```

**⚡ Processamento histórico falha**
```bash
# Verificar logs
tail -f logs/full_historical_monitoring.log
# Soluções: Verificar arquivos XLSX corrompidos
```

**💾 Dados não carregam**
```bash
# Verificar estrutura de arquivos
ls -la data/input/csv/
ls -la data/input/xlsx/
# Solução: Verificar caminhos e permissões
```

## 📚 Documentação Detalhada

- **📖 [Processamento Histórico](docs/PROCESSAMENTO_HISTORICO.md)**: Guia completo de processamento
- **🎨 [Dashboard](docs/DASHBOARD_GUIA.md)**: Manual do dashboard interativo  
- **🔧 [Scripts](docs/SCRIPTS_REFERENCIA.md)**: Referência de todos os scripts
- **📋 [Monitor](monitor/README.md)**: Documentação do sistema de monitoramento

## 🚀 Próximos Passos

### Em Desenvolvimento
- **📧 Alertas**: Email automático para violações
- **📱 Mobile**: Versão nativa iOS/Android
- **🔌 API REST**: Endpoints para consumo externo
- **📈 Gráficos**: Visualização temporal avançada

### Integração
- **⏰ Automação**: Agendamento via cron/Windows Task Scheduler
- **💬 Slack/Teams**: Notificações integradas
- **☁️ Cloud**: Deploy AWS/Azure
- **🔄 CI/CD**: Pipeline automatizado

## ✅ Status Atual

- ✅ **Sistema OOP**: 100% funcional
- ✅ **4 Monitores**: Subordinação, Inadimplência, PDD, Concentração
- ✅ **Dashboard Web**: Interface completa com drilldown
- ✅ **Processamento Paralelo**: Até 12 workers simultâneos
- ✅ **77+ Pools**: Modo debug removível
- ✅ **Dados Históricos**: Técnica de movimentação implementada
- ✅ **Performance**: Otimizada para datasets grandes
- ✅ **Compatibilidade**: Spyder, IPython, Terminal

---

**🎯 Sistema Pronto para Produção**

*AmFi Monitoring System - 2025 | Monitoramento Completo de Pools de Recebíveis*