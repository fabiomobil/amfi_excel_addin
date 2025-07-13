# Estado do Sistema AmFi - Snapshot Técnico

## Última Verificação: 2025-07-13 10:13

### 📊 Estrutura de Dados Atual (Variável Diariamente)

#### **Dados de Entrada (Estado 2025-07-13)**
- **CSV Dashboard**: `AcompanhamentoDeOportunidades-2025-07-11.csv`
  - **45 registros** de pools (varia diariamente)
  - Colunas: `nome`, `sr`, `jr`, `pl`, `tipo_de_produto`
  - Coluna identificadora: `nome` (ex: "LeCapital Pool #1")
  
- **XLSX Portfolio**: `Carteira Global 2025-07-07.xlsx`
  - **79,735 registros** de recebíveis (varia diariamente)
  - **36 pools únicos** (varia diariamente)
  - Coluna identificadora: `pool` (minúscula, ex: "LeCapital Pool #1")
  - Colunas nativas: `pool`, `loan_id`, `id_do_ativo`, `data_de_aquisicao`, `vencimento_original`, `status`, `valor_presente`, `nome_do_cedente`, `nome_do_sacado`
  - **16 colunas originais** (estado inicial)

### 🔄 Processo de Enriquecimento Progressivo (Não Permanente)

**IMPORTANTE**: O enriquecimento NÃO é um estado fixo. É um **processo que ocorre durante a execução** do orchestrator.

#### **Fluxo do Enriquecimento Durante Execução:**

```
1. orchestrator.run_monitoring() inicia
2. data_loader carrega XLSX com 16 colunas originais
3. Para cada pool processado:
   a) Monitor subordinação executa (não modifica XLSX)
   b) Monitor inadimplência executa:
      - Se 'dias_atraso' NÃO existe → calcula para TODA a carteira + adiciona coluna
      - Se 'grupo_de_risco' NÃO existe → classifica TODA a carteira + adiciona coluna
      - Se campos JÁ existem → reutiliza (não recalcula)
4. XLSX final tem 18 colunas (16 originais + 2 calculadas)
5. Fim da execução: DataFrame enriquecido existe apenas na memória
```

#### **Estados do XLSX Durante Execução:**

| Momento | Colunas | Descrição |
|---------|---------|-----------|
| **Carregamento inicial** | 16 | Estado original do arquivo |
| **1º pool c/ inadimplência** | 18 | +dias_atraso, +grupo_de_risco |
| **2º pool c/ inadimplência** | 18 | Reutiliza campos já calculados |
| **Fim da execução** | 18 | DataFrame final na memória |
| **Próxima execução** | 16 | Reinicia do arquivo original |

#### **Campos Adicionados Durante Processamento:**

**`dias_atraso` (int)**:
- **Cálculo**: `(data_atual - vencimento_original).days`
- **Escopo**: Toda a carteira (todos os 79k registros)
- **Quando**: Primeiro pool que executa monitor de inadimplência
- **Valores típicos**: 0-200+ dias
- **Distribuição observada**: 0 dias (17k), 6 dias (20k), 12 dias (12k)

**`grupo_de_risco` (str)**:
- **Cálculo**: Baseado em `dias_atraso` vs configuração PDD do pool
- **Valores**: AA, A, B, C, D, E, F, G, H
- **Escopo**: Toda a carteira (todos os 79k registros)
- **Quando**: Primeiro pool que executa monitor de inadimplência
- **Distribuição observada**: A (52k), D (7k), C (6k)

### ✅ Arquivos Testados e Funcionais

| Arquivo | Status | Última Execução | Performance | Funcionalidade |
|---------|--------|-----------------|-------------|----------------|
| **data_loader.py** | ✅ FUNCIONAL | 2025-07-13 10:13 | 79k registros em ~10s | Centraliza carregamento |
| **orchestrator.py** | ✅ FUNCIONAL | 2025-07-13 10:13 | 2 pools, 100% sucesso | Coordena monitores |
| **monitor_subordinacao.py** | ✅ FUNCIONAL | 2025-07-13 10:13 | <1s por pool | Calcula IS |
| **monitor_inadimplencia.py** | ✅ FUNCIONAL | 2025-07-13 10:13 | Enriquece 79k registros | Calcula inadimplência + enriquece |

### 🎯 Configurações de Teste (Modo DEBUG)

**Arquivo**: `/mnt/c/amfi/data/config/test_pools.json`
**Pools testados**: `['AFA Pool #1', 'LeCapital Pool #1']`
**Dados reais confirmados**:
- AFA Pool #1: 168 registros no XLSX
- LeCapital Pool #1: 93 registros no XLSX

### 🔧 Interfaces Funcionais Confirmadas

```python
# TESTADAS COM SUCESSO (2025-07-13):

# Interface principal
from orchestrator import run_monitoring
resultado = run_monitoring("LeCapital Pool #1")  # ✅ Sucesso, 1 pool
resultado = run_monitoring()                      # ✅ Sucesso, 2 pools

# Monitores individuais  
from monitor_subordinacao import run_subordination_monitoring  # ✅ Funcional
from monitor_inadimplencia import run_delinquency_monitoring   # ✅ Funcional + enriquece

# Funções auxiliares
from orchestrator import _has_subordination_monitoring         # ✅ Funcional
from orchestrator import _has_delinquency_monitoring          # ✅ Funcional
```

### 📈 Performance Confirmada (2025-07-13)

**Carregamento**:
- CSV (45 registros): ~1 segundo
- XLSX (79k registros): ~9 segundos
- JSONs (2 pools): ~1 segundo

**Processamento**:
- Monitor subordinação: <1 segundo por pool
- Monitor inadimplência (1º pool): ~1 segundo (inclui enriquecimento global)
- Monitor inadimplência (2º pool): <1 segundo (reutiliza enriquecimento)

**Total**: ~12 segundos para carregar + processar 2 pools com enriquecimento

### ⚠️ Limitações e Considerações

1. **Enriquecimento é temporário**: Existe apenas durante execução, não persiste
2. **Números variam diariamente**: 79k registros e 36 pools são do snapshot 2025-07-13
3. **PDD depende do pool**: Grupo de risco usa configuração do primeiro pool processado
4. **Modo DEBUG ativo**: Sistema usa apenas 2 pools para testes

### 🔄 Próximos Arquivos a Implementar

- **monitor_concentracao.py**: Poderá usar `grupo_de_risco` já calculado
- **monitor_elegibilidade.py**: Poderá usar `dias_atraso` já calculado
- **Monitores customizados**: Reutilizarão campos enriquecidos

### 📝 Última Execução Detalhada

```
Data: 2025-07-13 10:13
Comando: run_monitoring()
Resultado: 
- Pools processados: 2
- Taxa de sucesso: 100%
- Enriquecimento: dias_atraso (201 valores únicos), grupo_de_risco (8 grupos)
- XLSX final: 79,735 registros, 18 colunas (16+2)
- Tempo total: ~12 segundos
```

---

**Nota Importante**: Esta documentação reflete o estado específico de 2025-07-13. Números de pools e registros VARIAM DIARIAMENTE conforme novos dados são carregados.