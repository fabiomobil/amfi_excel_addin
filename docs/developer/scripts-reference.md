# Referência Rápida de Scripts - Sistema AmFi

## 🎯 Scripts Principais

| Script | Localização | Função |
|--------|-------------|---------|
| **run_dashboard.py** | `scripts/` | Servidor web do dashboard (anteriormente dashboard_server.py) |
| **run_monitoring.py** | `scripts/` | API de monitoramento (anteriormente run_monitoring_api.py) |
| **generate_dashboard.py** | `scripts/` | Gerador HTML (anteriormente generate_table_dashboard.py) |

## 🏗️ Estrutura de Código Fonte

### Diretório `src/`
```
src/
├── dashboard/
│   ├── server.py          # Código do servidor HTTP
│   └── generator.py       # Código de geração HTML
└── monitor/
    ├── orchestrator.py    # Interface principal run_monitoring()
    ├── base/             # Monitores OOP (PDD, concentração, inadimplência, subordinação)
    ├── utils/            # Utilitários de análise e dados
    └── cash_flow/        # Engines de análise de liquidez
```

## 🛠️ Utilitários por Categoria

### Monitoramento Core
- `src/monitor/orchestrator.py` - Interface principal `run_monitoring()`
- `src/monitor/base/base_monitor.py` - Classe base para monitores
- `src/monitor/base/monitor_concentracao_oop.py` - Monitor de concentração
- `src/monitor/base/monitor_inadimplencia_oop.py` - Monitor de inadimplência  
- `src/monitor/base/monitor_pdd_oop.py` - Monitor PDD
- `src/monitor/base/monitor_subordinacao_oop.py` - Monitor subordinação

### Utilitários de Análise (src/monitor/utils/)
- `concentration_analysis.py` - Contém `gen_concentration_table()` (renomeada)
- `pdd_analysis.py` - Análise detalhada de PDD
- `data_loader.py` - Carregamento de dados CSV/XLSX
- `data_converters.py` - Conversão e transformação de dados
- `date_consistency_validator.py` - Validação de consistência temporal
- `daily_results_persistence.py` - Persistência de resultados diários
- `alerts.py` - Sistema de alertas e notificações

### Dashboard & Interface (src/dashboard/)
- `server.py` - Servidor HTTP com APIs REST
- `generator.py` - Contém `calc_consecutive_violations()` (renomeada)

### Análise de Liquidez (src/monitor/cash_flow/)
- `cash_flow_orchestrator.py` - Orquestrador principal (3 funções removidas)
- `liquidity_analyzer.py` - Analisador de liquidez
- `pu_analysis_engine.py` - Engine de análise PU
- `pl_percentage_engine.py` - Engine de percentual PL
- `liquidity_scenarios.py` - Cenários de liquidez

### Dados & Configuração
- `config/pools/` - Configurações JSON por pool
- `config/monitoring/` - Filtros e configurações de monitoramento
- `data/input/csv/` - Dados CSV de entrada
- `data/input/xlsx/` - Dados XLSX de entrada
- `data/output/monitoring_results/` - Resultados de monitoramento

## 🚀 Comandos Essenciais

```bash
# Executar monitoramento completo
python scripts/run_monitoring.py

# Iniciar servidor web do dashboard
python scripts/run_dashboard.py

# Gerar dashboard HTML estático
python scripts/generate_dashboard.py
```

## 📝 Funções Renomeadas (IMPORTANTE)

### Utilitários de Concentração
```python
# NOVA função em src/monitor/utils/concentration_analysis.py
def gen_concentration_table(monitoring_results: Dict) -> pd.DataFrame:
    # Anteriormente: generate_concentration_summary_table()
```

### Cálculo de Violações Consecutivas  
```python
# NOVA função em src/dashboard/generator.py
def calc_consecutive_violations(pool_name: str, status: str) -> int:
    # Anteriormente: calculate_concentration_consecutive_violation_days()
```

## 🔧 Exemplos de Import

```python
# Scripts principais
from scripts.run_monitoring import run_monitoring_api
from scripts.run_dashboard import start_dashboard_server
from scripts.generate_dashboard import generate_html_dashboard

# Monitoramento
from src.monitor.orchestrator import run_monitoring
from src.monitor.base.monitor_concentracao_oop import MonitorConcentracao
from src.monitor.utils.concentration_analysis import gen_concentration_table
from src.monitor.utils.pdd_analysis import extract_pdd_analysis

# Dashboard
from src.dashboard.server import DashboardServer
from src.dashboard.generator import calc_consecutive_violations

# Análise de liquidez
from src.monitor.cash_flow.cash_flow_orchestrator import run_cash_flow_analysis
from src.monitor.cash_flow.liquidity_analyzer import LiquidityAnalyzer
```

## ⚠️ Arquivos Removidos/Modificados

### Arquivos Removidos
- ~~`import_helper.py`~~ - Funcionalidade integrada aos módulos
- ~~`path_resolver.py`~~ - Funcionalidade integrada aos módulos

### Scripts Movidos/Renomeados
- `dashboard_server.py` → `scripts/run_dashboard.py`
- `run_monitoring_api.py` → `scripts/run_monitoring.py`  
- `generate_table_dashboard.py` → `scripts/generate_dashboard.py`

### Funções Removidas do cash_flow_orchestrator.py
3 funções foram removidas durante a refatoração (detalhes no código fonte).

## 📖 Documentação Detalhada

- **Guia de início**: Ver `docs/user-guide/getting-started.md`
- **Exemplos práticos**: Ver `docs/user-guide/examples.md`
- **Arquitetura técnica**: Ver `docs/CLAUDE.md`
- **Processamento de dados**: Ver `docs/developer/data-processing.md`
- **Estado do sistema**: Ver `docs/technical/SYSTEM_STATE.md`

## 🎯 Referência Rápida de Desenvolvimento

### Executar um monitor específico
```python
from src.monitor.base.monitor_concentracao_oop import MonitorConcentracao

monitor = MonitorConcentracao("AFA Pool #1")
resultado = monitor.executar()
```

### Gerar tabela de concentração
```python
from src.monitor.utils.concentration_analysis import gen_concentration_table

# monitoring_results já carregado
tabela = gen_concentration_table(monitoring_results)
```

### Calcular dias consecutivos de violação
```python
from src.dashboard.generator import calc_consecutive_violations

dias = calc_consecutive_violations("AFA Pool #1", "VIOLATION")
```

---

**💡 Esta referência reflete a estrutura atual do sistema após a reorganização completa dos scripts e módulos. Para implementação detalhada, consulte o código fonte nos diretórios `src/` e `scripts/`.**