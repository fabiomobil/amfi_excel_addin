# Referência Rápida de Scripts - Sistema AmFi

## 🎯 Scripts Principais

| Script | Localização | Função |
|--------|-------------|---------|
| **orchestrator.py** | `src/monitor/` | Motor principal de monitoramento |
| **run_dashboard.py** | `scripts/` | Servidor web do dashboard |
| **generate_dashboard.py** | `scripts/` | Gerador de dashboard HTML |
| **run_monitoring.py** | `scripts/` | API de execução do monitoramento |

## 🛠️ Utilitários por Categoria

### Monitoramento Core
- `src/monitor/orchestrator.py` - Interface principal `run_monitoring()`
- `src/monitor/base/` - Monitores especializados (PDD, concentração, etc)
- `src/monitor/utils/` - Utilitários de dados e análise

### Dashboard & Interface
- `src/dashboard/server.py` - Servidor HTTP com APIs
- `src/dashboard/generator.py` - Geração de HTML e relatórios
- `scripts/run_dashboard.py` - Entry point do servidor

### Dados & Configuração
- `config/pools/` - Configurações JSON por pool
- `data/input/` - Dados de entrada (CSV/XLSX)
- `data/output/` - Resultados e dashboards

### Documentação & Desenvolvimento
- `docs/` - Documentação completa do sistema
- `logs/` - Logs operacionais

## 🚀 Comandos Essenciais

```bash
# Executar monitoramento
python scripts/run_monitoring.py

# Iniciar dashboard web
python scripts/run_dashboard.py

# Gerar dashboard HTML
python scripts/generate_dashboard.py
```

## 📖 Documentação Detalhada

- **Uso do sistema**: Ver [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md)
- **Arquitetura técnica**: Ver [CLAUDE.md](CLAUDE.md)
- **Guia do dashboard**: Ver [DASHBOARD_GUIA.md](DASHBOARD_GUIA.md)
- **Processamento histórico**: Ver [PROCESSAMENTO_HISTORICO.md](PROCESSAMENTO_HISTORICO.md)

---

**💡 Esta é uma referência rápida. Para exemplos detalhados de código e configuração, consulte os arquivos de documentação específicos listados acima.**