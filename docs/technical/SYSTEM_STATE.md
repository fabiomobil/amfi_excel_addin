# Estado do Sistema AmFi - Snapshot Técnico

> **Documentação Consolidada:**
> - Estado técnico atual do sistema
> - Workflows operacionais de sincronização
> - Procedimentos de desenvolvimento

## Última Verificação: 2025-07-18 - Status Atualizado

### 🕒 Sistema de Validação de Datas (NOVO - 2025-07-18)

#### **Validação Automática de Consistência Temporal**
O sistema agora valida automaticamente que arquivos CSV e XLSX têm datas consistentes:

**Componentes**:
- `DateConsistencyValidator`: Classe para extração e validação de datas
- Integração em `data_loader.py`: Validação automática no Step 3
- Preservação em `daily_results_persistence.py`: Uso da data extraída

**Fluxo de Validação**:
```
1. Carregamento de arquivos (data_loader.py)
2. Extração de datas dos nomes dos arquivos
   - CSV: "AcompanhamentoDeOportunidades-2025-07-18.csv" → 2025-07-18
   - XLSX: "Carteira Global 2025-07-18.xlsx" → 2025-07-18
3. Validação de consistência CSV ↔ XLSX
4. Armazenamento de execution_date nos metadados
5. Persistência usando data extraída (não data atual)
   - Resultado: "/daily_consolidated/2025-07-18.json"
```

**Formatos Suportados**:
- `YYYY-MM-DD`: 2025-07-18
- `YYYY-MM-DD HH_MM_SS`: 2025-07-15 09_33_29 
- `YYYY-MM-DD HHMMSS`: 2025-07-15 070048
- `DD/MM/YYYY`: 18/07/2025

**Benefícios**:
- ✅ Arquivos históricos JSON com datas corretas dos dados fonte
- ✅ Detecta inconsistências temporais automaticamente
- ✅ Análise temporal delta (D-1) usa datas reais, não estimadas

### 📊 Estrutura de Dados Atual (Variável Diariamente)

#### **Dados de Entrada (Estado 2025-07-13)**
- **CSV Dashboard**: `/data/input/csv/AcompanhamentoDeOportunidades-2025-07-11.csv`
  - **45 registros** de pools (varia diariamente)
  - Colunas: `nome`, `sr`, `jr`, `pl`, `tipo_de_produto`
  - Coluna identificadora: `nome` (ex: "LeCapital Pool #1")
  
- **XLSX Portfolio**: `/data/input/xlsx/Carteira Global 2025-07-07.xlsx`
  - **79,735 registros** de recebíveis (varia diariamente)
  - **36 pools únicos** (varia diariamente)
  - Coluna identificadora: `pool` (minúscula, ex: "LeCapital Pool #1")
  - Colunas nativas: `pool`, `loan_id`, `id_do_ativo`, `data_de_aquisicao`, `vencimento_original`, `status`, `valor_presente`, `nome_do_cedente`, `nome_do_sacado`
  - **16 colunas originais** (estado inicial)

#### **Configurações de Pools**
- **JSONs ativos**: `/config/pools/*.json` (7 pools padronizados)
- **JSONs legacy**: `/config/pools/legacy/*.json` (versões antigas)
- **Config monitoramento**: `/config/monitoring/test_pools.json` (modo DEBUG)

### 🔄 Processo de Enriquecimento Progressivo (Não Permanente)

**IMPORTANTE**: O enriquecimento NÃO é um estado fixo. É um **processo que ocorre durante a execução** do orchestrator.

#### **Fluxo do Enriquecimento Durante Execução:**

```
1. run_monitoring() inicia [INTERFACE ÚNICA]
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
| **monitor_subordinacao_oop.py** | ✅ FUNCIONAL | 2025-07-18 | <1s por pool | Calcula IS |
| **monitor_inadimplencia_oop.py** | ✅ FUNCIONAL | 2025-07-18 | Enriquece 79k registros | Calcula inadimplência + enriquece |
| **monitor_pdd_oop.py** | ✅ FUNCIONAL | 2025-07-18 | <1s por pool | Calcula PDD |
| **monitor_concentracao_oop.py** | ✅ FUNCIONAL | 2025-07-18 | <1s por pool | Calcula concentração |

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
from monitor_subordinacao_oop import run_subordination_monitoring  # ✅ Funcional
from monitor_inadimplencia_oop import run_delinquency_monitoring   # ✅ Funcional + enriquece
from monitor_pdd_oop import run_pdd_monitoring                     # ✅ Funcional
from monitor_concentracao_oop import run_concentration_monitoring  # ✅ Funcional

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

## 🧪 **Verificação de Sistema - Comandos de Teste**

### Verificação Diária de Estado
```bash
# 1. Verificar quantos pools e registros existem HOJE
python3 -c "
from data_loader import load_pool_data
resultado = load_pool_data()
print(f'Pools: {len(resultado[\"pools_processados\"])}')
print(f'XLSX: {resultado[\"xlsx_data\"].shape}')
print(f'CSV: {resultado[\"csv_data\"].shape}')
"

# 2. Teste rápido do sistema
python3 -c "
from orchestrator import run_monitoring
resultado = run_monitoring('LeCapital Pool #1')
print(f'Sucesso: {resultado[\"sucesso\"]}')
"
```

### Interfaces de Referência
```python
# Interface principal (TESTADA 2025-07-13)
from orchestrator import run_monitoring
resultado = run_monitoring()                      # Todos os pools (modo DEBUG)
resultado = run_monitoring("LeCapital Pool #1")   # Pool específico

# Monitores individuais (TESTADOS 2025-07-13)
from monitor_subordinacao import run_subordination_monitoring
from monitor_inadimplencia import run_delinquency_monitoring
```

### Arquivos Funcionais Validados (2025-07-18)
- ✅ **data_loader.py**: Centralizador (79k registros em ~10s)
- ✅ **orchestrator.py**: Interface principal (100% sucesso, 4 monitores integrados)
- ✅ **monitor_subordinacao_oop.py**: Monitor base funcional
- ✅ **monitor_inadimplencia_oop.py**: Monitor + enriquecimento progressivo
- ✅ **monitor_pdd_oop.py**: Monitor + arquitetura inteligente
- ✅ **monitor_concentracao_oop.py**: Monitor + análise sequencial

---

### 📂 Reestruturação Arquitetural (2025-07-13)

#### **Mudanças Implementadas:**
1. **Sistema Legacy Isolado**:
   - `/udfs/`, `amfi.xlam`, `Monitoramento.xlsm` → `/legacy/`
   - Documentado como "NÃO USAR" com README explicativo

2. **Reorganização por Responsabilidade**:
   - `/data/config/` → `/config/` (configurações estáticas)
   - `/data/escrituras/` → `/config/pools/` (JSONs de pools)
   - `/data/escrituras_md/` → `/assets/legal_docs/` (documentos legais)
   - `/screenshots/` → `/assets/screenshots/` (evidências)
   - `/data/csv/` → `/data/input/csv/` (dados de entrada)
   - `/data/xlsx/` → `/data/input/xlsx/` (dados de entrada)
   - `/data/monitoring_results/` → `/data/output/monitoring_results/` (resultados)

3. **Estrutura Final**:
   - `/legacy/` - Sistema antigo isolado
   - `/monitor/` - Sistema atual (Python puro)
   - `/config/` - Apenas configurações
   - `/data/` - Apenas dados dinâmicos (input/output)
   - `/assets/` - Recursos estáticos

---

## 📝 **Workflows Operacionais**

### Framework de Sincronização Diária (15-20 min)

**Processo de 7 Etapas para Inicialização Consistente:**

#### **ETAPA 1: Contextualização Principal (5 min)**
```bash
# Sequência obrigatória de leitura
1. CLAUDE.md → Contexto técnico completo
2. PRD.md → Objetivos e roadmap  
3. technical/SYSTEM_STATE.md → Estado atual
4. USAGE_EXAMPLES.md → Padrões de uso
```

**Checklist de Validação:**
- [ ] Compreendi a arquitetura atual
- [ ] Conheço os objetivos de negócio
- [ ] Sei o estado dos dados (métricas)
- [ ] Entendo as interfaces disponíveis

#### **ETAPA 2: Documentação Especializada (3 min)**
```bash
# Leitura seletiva baseada no foco da sessão
docs/processos/ → Para trabalho operacional
docs/technical/ → Para implementação técnica
```

#### **ETAPA 3: Sincronização de Documentos (2 min)**
```bash
# Verificar consistência entre documentos principais
1. Métricas CLAUDE.md == technical/SYSTEM_STATE.md
2. Objetivos CLAUDE.md == PRD.md  
3. Exemplos USAGE_EXAMPLES.md funcionais
```

#### **ETAPA 4: Organização Temporal (3 min)**
```bash
# Gestão de sessões anteriores
1. Listar arquivos docs/sessions/
2. Renomear expirados: to_do_YYYYMMDD.md → exp_to_do_YYYYMMDD.md
3. Verificar se há arquivos sem prefixo exp_ de dias anteriores
```

#### **ETAPA 5: Consolidação de Tarefas (5 min)**
```bash
# Extração de tarefas pendentes
1. Ler APENAS arquivos docs/sessions/ que NÃO possuem 'exp_'
2. Extrair tarefas não concluídas dos arquivos ativos
3. Consolidar por prioridade (Alto/Médio/Baixo)
4. Adicionar novas tarefas identificadas
```

#### **ETAPA 6: Criação do To-Do Atual (2 min)**
```bash
# Arquivo: docs/sessions/to_do_YYYYMMDD.md
1. Usar template padrão
2. Incluir métricas de progresso
3. Definir foco da sessão
4. Estabelecer próxima ação prioritária
```

#### **ETAPA 7: Definição de Foco (2 min)**
```bash
# Escolher foco da sessão
1. Revisar prioridades Alto no to-do
2. Verificar dependências técnicas
3. Estimar complexidade vs tempo disponível
4. Definir critério de sucesso da sessão
```

### Princípios Fundamentais

1. **Contextualização Total**: Nunca começar trabalho sem contexto completo
2. **Continuidade Garantida**: Zero perda de progresso entre sessões
3. **Priorização Baseada em Dados**: Decisões baseadas em métricas e progresso real
4. **Documentação Como Fonte de Verdade**: Documentos sempre refletem a realidade atual
5. **Escalabilidade Humana**: Qualquer pessoa pode executar o protocolo

### Métricas de Sucesso do Framework

**Eficiência:**
- Tempo de inicialização: < 20 minutos
- Tarefas perdidas entre sessões: 0%
- Documentação desatualizada: < 5%

**Qualidade:**
- Contexto completo carregado: 100%
- Próxima ação sempre clara: 100%
- Continuidade entre sessões: 100%

### Template de To-Do Diário

```markdown
# To-Do - [DATA] - AmFi

## 📊 Métricas de Progresso (Herdadas)
- **Monitores base**: X/5 (Subordinação ✅, Inadimplência ✅, PDD ✅)
- **Monitores customizados**: X/20+
- **Pools auditados**: X/7
- **Documentação**: Sincronizada ✅

## 🎯 Foco da Sessão
**Prioridade**: [DEFINIR]
**Critério de Sucesso**: [DEFINIR]

## 📋 Tarefas por Prioridade

### 🔥 ALTA PRIORIDADE
- [ ] [TAREFA PRINCIPAL DO DIA]

### ⚡ MÉDIA PRIORIDADE
- [ ] [TAREFAS IMPORTANTES]

### 💡 BAIXA PRIORIDADE
- [ ] [TAREFAS OPCIONAIS]

## 🚀 Próxima Ação Recomendada
[DEFINIR PRIMEIRA AÇÃO ESPECÍFICA]
```

---

**Sessão**: 2025-07-18  
**Responsável**: Claude Sonnet 4.0  
**Status**: Sistema integrado e funcional ✅  
**Reestruturação**: Concluída com legacy isolado ✅  
**Workflows**: Consolidados e operacionais ✅  
**Monitores**: 4/5 implementados (80% - falta apenas elegibilidade) ✅  
**Documentação**: Consolidada e atualizada ✅  
**Nota**: Números de pools e registros VARIAM DIARIAMENTE conforme novos dados são carregados.