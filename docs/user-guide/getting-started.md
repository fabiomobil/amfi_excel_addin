# Guia de Início Rápido - AmFi

## Visão Geral

O sistema AmFi fornece monitoramento automatizado de compliance para fundos de investimento estruturados. Este guia ajudará você a começar rapidamente com o uso diário e análise histórica.

## Requisitos

- Python 3.8+
- Dados CSV e XLSX atualizados em `data/input/`
- Configurações JSON dos pools em `config/pools/`

## 🚀 Uso Diário - Monitoramento Atual

### Execução Básica
```bash
# Monitoramento completo (todos os pools)
python scripts/run_monitoring.py

# Pool específico via Python
python -c "from src.monitor.orchestrator import run_monitoring; resultado = run_monitoring('AFA Pool #1'); print(f'Status: {resultado.get(\"sucesso\")}')"
```

### Dashboard Interativo
```bash
# Iniciar servidor web
python scripts/run_dashboard.py
# Acesse: http://localhost:8080

# Ou gerar HTML estático
python scripts/generate_dashboard.py
# Arquivo em: data/output/monitoring_results/dashboard/
```

### Interpretação de Resultados
- **✅ Sucesso**: Pool dentro dos limites configurados
- **⚠️ Violação Mínima**: Acima do limite mínimo, mas abaixo do crítico
- **❌ Violação Crítica**: Acima do limite crítico - ação imediata necessária

## 📅 Análise Histórica

### Quando Usar
- **Análise de tendências** - Identificar deterioração ao longo do tempo
- **Auditoria retrospectiva** - Verificar compliance em períodos passados
- **Comparação temporal** - Avaliar impacto de mudanças

### Monitor Unificado AmFi (Recomendado)
```python
# Importar no Spyder/Cursor
from scripts.amfi_monitor import AmFiMonitor
monitor = AmFiMonitor()

# 1. PREVIEW primeiro (seguro)
preview = monitor.run_historical_load(mode='preview')
print(f"Datas processadas: {preview['dates_processed']}")

# 2. COMMIT após análise
if input("Aplicar mudanças? (s/n): ").lower() == 's':
    commit = monitor.run_historical_load(mode='commit')
```


### Análise de Data Específica
```python
# Via Python - análise pontual
from src.monitor.orchestrator import run_monitoring

# Todos os pools em data específica
resultado = run_monitoring(data="14/07/2025")

# Pool específico em data específica
resultado = run_monitoring("Baru Pool #2", data="14/07/2025")

# Verificar se deu certo
if resultado.get('sucesso'):
    print(f"Pools processados: {len(resultado['pools_processados'])}")
    # Extrair dados específicos
    pool_result = resultado['resultados']['Baru Pool #2']
    print(f"Monitores executados: {pool_result['monitores_executados']}")
else:
    print(f"Erro: {resultado.get('erro')}")
```

## 📊 Estrutura de Resultados

### Arquivos Gerados
```
data/output/monitoring_results/
├── daily_consolidated/     # Histórico diário em JSON
│   ├── 2025-07-14.json    # Dados completos do dia
│   ├── 2025-07-15.json
│   └── ...
├── dashboard/              # Dashboards HTML
│   ├── table_dashboard.html
│   └── violations_dashboard.html
└── violations_index/       # Índices de violações
    ├── active_violations.json
    └── subordinacao_violations.json
```

### Dados por Pool
```json
{
  "Pool Name": {
    "sucesso": true,
    "monitores_executados": ["subordinacao", "inadimplencia", "pdd"],
    "resultados": {
      "subordinacao": {
        "subordination_ratio_percent": 25.18,
        "status_limite_minimo": "enquadrado",
        "aporte_necessario": {"para_limite_minimo": 0.0}
      },
      "inadimplencia": {
        "resultados": {
          "inadimplencia_30d": {"inadimplencia_percent": 2.5},
          "inadimplencia_90d": {"inadimplencia_percent": 1.2}
        }
      }
    }
  }
}
```

## 🔍 Casos de Uso Comuns

### 1. Monitoramento Diário
```bash
# Executar de manhã
python scripts/run_monitoring.py

# Ver dashboard
python scripts/run_dashboard.py
# Acessar http://localhost:8080
```

### 2. Análise Semanal de Tendências
```bash
# Últimos 7 dias
python scripts/amfi_monitor.py --historical --start-date 15/07/2025 --end-date 21/07/2025 --preview

# Comparar evolution via dashboard
python scripts/run_dashboard.py
```

### 3. Auditoria de Pool Específico
```python
# Análise histórica de um pool
from src.monitor.orchestrator import run_monitoring

pool_name = "Baru Pool #2"
datas = ["14/07/2025", "15/07/2025", "16/07/2025"]

for data in datas:
    resultado = run_monitoring(pool_name, data=data)
    if resultado.get('sucesso'):
        pool_data = resultado['resultados'][pool_name]
        sub_ratio = pool_data['resultados']['subordinacao']['subordination_ratio_percent']
        print(f"{data}: {sub_ratio:.2f}%")
```

### 4. Verificação de Compliance CCB
```python
# Verificar se pool usa lógica CCB (ex: Baru Pool #2)
resultado = run_monitoring("Baru Pool #2", data="14/07/2025")
if resultado.get('sucesso'):
    pdd_result = resultado['resultados']['Baru Pool #2']['resultados'].get('pdd')
    if pdd_result:
        tipo_ativo = pdd_result.get('tipo_ativo', 'Normal')
        print(f"Tipo de ativo: {tipo_ativo}")
        if tipo_ativo == 'CCB':
            print("✅ Usando lógica CCB (cálculo por ativo individual)")
```

## ⚠️ Solução de Problemas Comuns

### Dados Não Encontrados
```bash
# Verificar estrutura de arquivos
ls data/input/csv/
ls data/input/xlsx/

# Estrutura esperada:
# data/input/csv/AcompanhamentoDeOportunidades-dd-mm-yyyy.csv
# data/input/xlsx/Carteira Global yyyy-mm-dd HHMMSS.xlsx
```

### Erro de Encoding
```python
# Se aparecerem erros de caracteres especiais
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'
```

### Pool Não Encontrado
```bash
# Verificar se o JSON do pool existe
ls config/pools/"Nome do Pool.json"

# Nomes devem ser exatos, ex:
# "AFA Pool #1.json"
# "Baru Pool #2.json"
```

## 📞 Suporte

- **Documentação técnica**: `docs/CLAUDE.md`
- **APIs de integração**: `docs/api/`
- **Desenvolvimento**: `docs/developer/`