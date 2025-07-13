# ⚠️ SISTEMA LEGACY - NÃO USAR

## 🚨 AVISO IMPORTANTE
Esta pasta contém o **sistema antigo** baseado em xlwings + Excel UDFs que foi **SUBSTITUÍDO** pelo novo sistema de monitoramento Python puro.

## 📂 Conteúdo Legacy (NÃO MODIFICAR):
- `udfs/` - Funções definidas pelo usuário para Excel (xlwings)
- `amfi.xlam` - Add-in Excel antigo
- `Monitoramento.xlsm` - Workbook Excel antigo

## ⛔ O QUE NÃO FAZER:
- ❌ **NÃO USAR** para desenvolvimento novo
- ❌ **NÃO MODIFICAR** arquivos desta pasta
- ❌ **NÃO REFERENCIAR** código legacy em desenvolvimento atual
- ❌ **NÃO IMPORTAR** módulos desta pasta

## ✅ SISTEMA ATUAL - USE ISTO:

### **Local do Sistema Atual:**
```
/monitor/                    # Sistema Python moderno
├── base/                   # Monitores base
├── custom/                 # Monitores customizados  
├── utils/                  # Utilitários
└── orchestrator.py         # Interface principal
```

### **Como Usar o Sistema Atual:**
```python
# Interface principal
from monitor.orchestrator import run_monitoring

# Executar todos os pools (modo DEBUG)
resultado = run_monitoring()

# Executar pool específico
resultado = run_monitoring("LeCapital Pool #1")
```

### **Configurações Atuais:**
- **Pools**: `/config/pools/` (JSONs organizados)
- **Dados**: `/data/input/` (CSVs e XLSXs diários)
- **Resultados**: `/data/output/monitoring_results/`

## 🔄 MIGRAÇÃO DE FUNCIONALIDADES

Se você está procurando funcionalidades do sistema antigo:

| **Função Legacy (udfs/)** | **Equivalente Atual (monitor/)** |
|---------------------------|----------------------------------|
| `AmfiDashboard()` | `orchestrator.run_monitoring()` |
| `AmfiXLSX()` | `utils/data_loader.load_pool_data()` |
| `AmfiConcentracao()` | `base/monitor_concentracao.py` |
| `AmfiCalcularIS()` | `base/monitor_subordinacao.py` |
| `cache_manager.py` | Sistema integrado no data_loader |

## 📊 ARQUITETURA NOVA vs ANTIGA

### **❌ Arquitetura Antiga (Legacy):**
```
Excel → xlwings → UDFs Python → Resultados Excel
```
- Dependente do Excel
- UDFs complexas e difíceis de manter
- Cache manual
- Monitoramento fragmentado

### **✅ Arquitetura Nova (Atual):**
```
Data Files → Python Core → JSON Results → Dashboard/Reports
```
- **Python puro** - independente do Excel
- **Modular** - monitores especializados
- **Configurável** - JSONs de pool
- **Escalável** - fácil adicionar novos monitores
- **Testável** - testes unitários e integração

## 📝 HISTÓRICO

**Data de Legacy**: 2025-07-13  
**Razão da Substituição**: 
- Arquitetura xlwings complexa e difícil de manter
- Dependência do Excel limitava escalabilidade
- Duplicação de código entre UDFs
- Sistema Python puro mais robusto e testável

**Desenvolvedor**: Claude Sonnet 4.0  
**Sistema Novo**: Arquitetura Python + JSON configs + Progressive enrichment

---

## 🎯 PRÓXIMOS PASSOS

1. **Para desenvolvimento**: Use apenas `/monitor/`
2. **Para configuração**: Use JSONs em `/config/pools/`  
3. **Para execução**: Execute `orchestrator.run_monitoring()`
4. **Para testes**: Use arquivos em `/tests/unit/`

## 📞 SUPORTE

Se você precisa de funcionalidades específicas do sistema legacy que não estão implementadas no sistema atual, consulte:
- **Documentação**: `/docs/CLAUDE.md`
- **Status do sistema**: `/docs/SYSTEM_STATE.md`
- **To-dos**: `/docs/sessions/to_do_*.md`

---
**⚠️ IMPORTANTE: Esta pasta existe apenas para preservação histórica. TODO desenvolvimento deve usar o sistema em `/monitor/`**