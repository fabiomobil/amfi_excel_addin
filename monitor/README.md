# Sistema de Monitoramento AmFi

Sistema refatorado em arquitetura OOP para monitoramento de pools de recebíveis.

## 🚀 Quick Start

```python
import orchestrator
resultado = orchestrator.run_monitoring()  # Todos os pools
resultado = orchestrator.run_monitoring("AFA Pool #1")  # Pool específico
```

## 📊 Como Usar

### Verificar Resultados
```python
if resultado.get("sucesso"):
    print(f"Pools processados: {resultado['estatisticas']['total']}")
    print(f"Taxa de sucesso: {resultado['estatisticas']['taxa_sucesso']}%")
```

### Acessar Monitor Específico
```python
pool_result = resultado["resultados"]["AFA Pool #1"]
conc_result = pool_result["resultados"]["concentracao"]
print(f"Status: {conc_result['status_geral']}")
```

## 🔧 Monitores Disponíveis

- **Subordinação**: Índice SR com limites mínimo/crítico
- **Inadimplência**: Janelas configuráveis + enriquecimento progressivo
- **PDD**: Provisão por grupos de risco
- **Concentração**: Limites individuais e top-N por sacado/cedente

## 🏗️ Arquitetura

```
monitor/
├── orchestrator.py              # Interface principal
├── exemplo_uso.py               # Exemplos práticos
├── base/                        # Monitores OOP
│   ├── base_monitor.py          # Classe base
│   ├── result_builder.py        # Padronização
│   └── monitor_*_oop.py         # Monitores específicos
└── utils/                       # Utilitários
    ├── data_loader.py           # Carregamento
    ├── data_converters.py       # Conversões brasileiras
    └── alerts.py                # Sistema de logs
```

## ⚙️ Configuração

- **Modo Debug**: `test_pools.json` (pools específicos) - remover para processar todos
- **Configuração por Pool**: `{Pool Name}.json`
- **Pools Ignorados**: `ignore_pools.json`
- **Processamento Histórico**: Scripts especializados para dados temporais

## 📈 Performance

- **Conversões vetorizadas**: 50-100x mais rápido
- **Enriquecimento progressivo**: Cálculos reutilizados
- **Código reduzido**: 40% menos linhas no orchestrator

## 🔍 Estrutura de Resultados

```python
{
    "sucesso": bool,
    "estatisticas": {"total": int, "taxa_sucesso": float},
    "resultados": {
        "Pool Name": {
            "monitores_executados": ["subordinacao", "inadimplencia", "pdd", "concentracao"],
            "resultados": {
                "concentracao": {"status_geral": "enquadrado", "resumo": {...}},
                "inadimplencia": {"inadimplencia_30d": {...}, "inadimplencia_90d": {...}},
                "pdd": {"pdd_analysis": {...}},
                "subordinacao": {"subordination_ratio_percent": float}
            }
        }
    },
    "xlsx_enriched": DataFrame  # Dados globalmente enriquecidos
}
```

## 🛠️ Troubleshooting

**Import Error**: Sistema tem fallback automático para diferentes contextos
**Performance**: Modo automático para datasets >1000 registros  
**Dados não encontrados**: Verificar arquivos CSV/XLSX e configurações JSON

## 📊 Dashboard e Histórico

### Dashboard Interativo
```bash
python3 generate_table_dashboard.py
```
- **Interface Web**: Tabelas com drilldown
- **Dados Financeiros**: PL, SR, JR detalhados
- **Análise Histórica**: Últimos 7 dias por pool
- **Status Visual**: VIOLADO CRÍTICO, VIOLADO MÍNIMO, ENQUADRADO

### Processamento Histórico
```bash
# Processamento paralelo completo
python3 run_full_historical_monitoring.py --max-workers 12

# Pular datas já processadas
python3 run_full_historical_monitoring.py --skip-existing

# Processamento sequencial (últimos 5 dias)
python3 run_sequential_historical_monitoring.py
```

## ✅ Sistema Completo

- ✅ **Orchestrator**: Funcionando 100%
- ✅ **4 Monitores**: Subordinação, Inadimplência, PDD, Concentração
- ✅ **Dashboard Web**: Interface interativa com histórico
- ✅ **Processamento Paralelo**: Até 12 workers simultâneos
- ✅ **Dados Históricos**: Técnica de movimentação de arquivos
- ✅ **77 Pools**: Modo debug removível
- ✅ **Compatibilidade**: Spyder, IPython, Terminal
- ✅ **Performance**: Otimizada para datasets grandes

**Comando único**: `import orchestrator; orchestrator.run_monitoring()`