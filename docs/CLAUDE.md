# AmFi - Sistema de Monitoramento de Portfólio

> **IMPORTANTE**: Sempre utilizar Claude Sonnet 4.0 para trabalhar neste projeto.

## 🚨 Mudanças Principais (Reorganização 2025-07-24)

**ESTRUTURA COMPLETAMENTE REORGANIZADA:**
- **Código fonte**: Movido para `src/monitor/` (estrutura modular limpa)
- **Scripts executáveis**: Centralizados em `scripts/` (run_monitoring.py, run_dashboard.py, generate_dashboard.py)
- **Documentação**: Reorganizada em `docs/` com 40% redução de redundância
- **Sistema legacy**: Diretório `legacy/` **REMOVIDO COMPLETAMENTE**
- **Arquivos obsoletos**: `import_helper.py`, `path_resolver.py` **ELIMINADOS**
- **Funções limpas**: 3 funções não utilizadas **REMOVIDAS**

**NOVOS CAMINHOS DE IMPORTAÇÃO:**
```python
# ANTES (não funciona mais):
from monitor.orchestrator import run_monitoring

# AGORA (novo caminho):
from src.monitor.orchestrator import run_monitoring

# OU usar scripts:
python scripts/run_monitoring.py
```

**DOCUMENTAÇÃO MODULAR:**
- `docs/user-guide/` - Para usuários finais
- `docs/api/` - Para integradores
- `docs/developer/` - Para desenvolvedores
- `docs/technical/` - Análises técnicas avançadas

## Contexto do Projeto
Sistema de monitoramento automatizado para fundos de investimento estruturados no Brasil. Processa escrituras de debêntures (PDFs) em configurações JSON para executar monitoramento de compliance, análise de fluxo de caixa e verificação de liquidez.

## Arquitetura do Sistema

### Fluxo de Dados Principal
```
Escritura (PDF) → JSON Config → Monitoramento Python → JSON Resultados → Dashboard
     ↓               ↓                    ↓                    ↓
  Manual         Automático         5 Componentes        Consolidado
```

### Componentes Principais
1. **Monitoramento Individual**: Verifica compliance por pool
2. **Dashboard de Exceções**: Consolida apenas violações
3. **Análise Comparativa**: Evolução temporal dia-a-dia
4. **Fluxo de Caixa**: Projeção de recebíveis (adimplentes/inadimplentes)
5. **Análise de Liquidez**: Cobertura de amortizações futuras (3 cenários implementados)

## Estrutura de Diretórios
```
C:\amfi\
├── README.md                    # Documentação principal do projeto
├── src/                         # ✅ CÓDIGO FONTE MODULAR (Reorganizado)
│   ├── __init__.py
│   ├── dashboard/              # Interface web e APIs
│   │   ├── __init__.py
│   │   ├── server.py          # Servidor HTTP + endpoints
│   │   └── generator.py       # Geração de dashboards HTML
│   └── monitor/               # ✅ SISTEMA DE MONITORAMENTO (Python puro)
│       ├── README.md
│       ├── base/               # Monitores padrão OOP
│       │   ├── __init__.py
│       │   ├── base_monitor.py
│       │   ├── data_handler.py
│       │   ├── monitor_concentracao_oop.py
│       │   ├── monitor_inadimplencia_oop.py
│       │   ├── monitor_pdd_oop.py
│       │   ├── monitor_subordinacao_oop.py
│       │   └── result_builder.py
│       ├── cash_flow/          # Análise de fluxo de caixa e liquidez
│       │   ├── __init__.py
│       │   ├── base_cash_flow_engine.py
│       │   ├── cash_flow_orchestrator.py
│       │   ├── liquidity_analyzer.py
│       │   ├── liquidity_scenarios.py
│       │   ├── pl_percentage_engine.py
│       │   └── pu_analysis_engine.py
│       ├── orchestrator.py     # Interface principal do sistema
│       └── utils/              # Utilitários compartilhados
│           ├── __init__.py
│           ├── alerts.py
│           ├── concentration_analysis.py
│           ├── daily_results_persistence.py
│           ├── data_converters.py
│           ├── data_handler.py
│           ├── data_loader.py
│           ├── date_consistency_validator.py
│           ├── file_loaders.py
│           ├── pdd_analysis.py
│           └── pdd_api_endpoints.py
├── scripts/                     # 🚀 ENTRY POINTS EXECUTÁVEIS (Reorganizado)
│   ├── run_dashboard.py        # Servidor web do dashboard
│   ├── run_monitoring.py       # API de execução do monitoramento
│   └── generate_dashboard.py   # Gerador de dashboard HTML
├── config/                      # ⚙️ CONFIGURAÇÕES ESTÁTICAS
│   ├── monitoring/             # Configurações de monitoramento
│   │   ├── _test_pools.json   # Pools para modo DEBUG
│   │   ├── concentration_filters.json # Filtros de concentração
│   │   └── ignore_pools.json  # Pools a ignorar
│   └── pools/                  # Configurações de pools (9 pools ativos)
│       ├── README.md
│       └── *.json             # JSONs dos pools (legacy removido)
├── data/                        # 💾 DADOS DINÂMICOS APENAS
│   ├── input/                  # Dados de entrada diários
│   │   ├── csv/               # CSVs diários (PL, SR, JR)
│   │   └── xlsx/              # Carteiras detalhadas (recebíveis)
│   └── output/                # Resultados processados
│       └── monitoring_results/ # Outputs de monitoramento por pool
│           ├── daily_consolidated/ # Resultados consolidados diários
│           ├── dashboard/      # Dashboards HTML gerados
│           └── violations_index/ # Índices de violações
├── docs/                        # 📚 DOCUMENTAÇÃO REORGANIZADA (40% redução)
│   ├── README.md              # 🏠 Índice principal navegável
│   ├── CLAUDE.md              # 📖 Documento técnico principal
│   ├── PRD.md                 # 🎯 Visão de produto
│   ├── user-guide/            # 👥 Para usuários finais
│   │   ├── getting-started.md
│   │   └── examples.md
│   ├── api/                   # 🔌 Para integradores
│   │   ├── drilldown.md
│   │   └── pdd-hierarchy.md
│   ├── developer/             # 👨‍💻 Para desenvolvedores
│   │   ├── data-processing.md
│   │   └── scripts-reference.md
│   ├── technical/             # 🛠️ Análises técnicas avançadas
│   │   ├── LOGICA_CCB_PDD.md
│   │   ├── SYSTEM_STATE.md
│   │   ├── VALIDACAO_SCHEMA_JSON.md
│   │   └── liquidity_analyzer_integration.md
│   ├── legal/                 # ⚖️ Documentação legal
│   │   └── documents/         # Documentos legais processados
│   └── assets/                # 🖼️ Recursos visuais e assets
│       └── images/
│           └── logo.svg
```

## ⚠️ Sistema Legacy vs Sistema Atual

### **❌ Sistema Legacy (REMOVIDO)**
- **Local**: `legacy/` - **DIRETÓRIO REMOVIDO COMPLETAMENTE**
- **Tecnologia**: xlwings + Excel UDFs
- **Arquivos**: `udfs/`, `amfi.xlam`, `Monitoramento.xlsm` - **TODOS REMOVIDOS**
- **Status**: **REMOVIDO** - Sistema Excel antigo completamente eliminado
- **Motivo**: Dependente do Excel, difícil manutenção, duplicação de código

### **✅ Sistema Atual (USAR ESTE)**
- **Local**: `src/monitor/` - **REORGANIZADO**
- **Tecnologia**: Python puro + JSON configs
- **Interface**: `run_monitoring()` - ÚNICA função oficial
- **Entry Points**: Scripts movidos para `scripts/` (run_dashboard.py, run_monitoring.py, generate_dashboard.py)
- **Status**: **ATIVO** - Monitores subordinação + inadimplência + PDD + concentração + liquidez implementados
- **Vantagens**: Independente do Excel, modular, testável, escalável, estrutura limpa

### **🔄 Migração de Funcionalidades Completa**

| **Função Legacy** | **Sistema Atual** | **Status** |
|-------------------|-------------------|------------|
| `udfs/amfi.py` (UDFs Excel) | `src/src/monitor/orchestrator.py` | ✅ Substituído |
| `AmfiDashboard()` | `run_monitoring()` | ✅ Implementado |
| `AmfiXLSX()` | `src/monitor/utils/data_loader.py` | ✅ Melhorado |
| `AmfiConcentracao()` | `src/monitor/base/monitor_concentracao_oop.py` | ✅ Implementado |
| `AmfiCalcularIS()` | `src/monitor/base/monitor_subordinacao_oop.py` | ✅ Implementado |
| Cache manual | Cache integrado no data_loader | ✅ Automatizado |
| **Arquivos removidos**: | **Eliminados:** | **Status** |
| `import_helper.py` | N/A | ❌ Removido |
| `path_resolver.py` | N/A | ❌ Removido |
| 3 funções não utilizadas | N/A | ❌ Removidas |

### **📝 Interface Principal: run_monitoring()**

**ÚNICA função oficial do sistema** - Funções legacy removidas em 2025-07-14.

```python
from src.monitor.orchestrator import run_monitoring

# 1. PROCESSAR TODOS OS POOLS (modo debug)
resultado = run_monitoring()
print(f"Pools: {resultado['pools_processados']}")
print(f"Taxa sucesso: {resultado['estatisticas']['taxa_sucesso']}%")

# 2. PROCESSAR POOL ESPECÍFICO
resultado = run_monitoring("LeCapital Pool #1")
pool_result = resultado['resultados']['LeCapital Pool #1']

# 3. VERIFICAR SUBORDINAÇÃO
sub_result = pool_result['resultados']['subordinacao']
print(f"Subordinação: {sub_result['subordination_ratio_percent']}%")

# 4. VERIFICAR INADIMPLÊNCIA (todas as janelas configuradas)
inad_result = pool_result['resultados']['inadimplencia']['resultados']
for janela, dados in inad_result.items():
    print(f"{janela}: {dados['inadimplencia_percent']}% (limite: {dados['limite_configurado']*100}%)")

# 5. ACESSAR DADOS ENRIQUECIDOS
xlsx_enriched = resultado['xlsx_enriched']  # DataFrame com novos campos
print(f"Campos adicionados: dias_atraso, grupo_de_risco")

# 6. VERIFICAR ANÁLISE DE LIQUIDEZ (se configurado)
if 'liquidez' in pool_result['resultados']:
    liquidez_result = pool_result['resultados']['liquidez']
    if liquidez_result.get('success'):
        print(f"Próximo pagamento: {liquidez_result['next_payment']['date']} (R$ {liquidez_result['next_payment']['amount']:,.2f})")
        scenarios = liquidez_result['scenarios']
        print(f"Todos os cenários suficientes: {liquidez_result['summary']['all_scenarios_sufficient']}")
        for scenario_name, scenario_data in scenarios.items():
            status = '✅' if scenario_data['sufficient'] else '❌'
            print(f"  {scenario_name}: {status} (cobertura: {scenario_data['coverage_ratio']:.2f}x)")
```

**Monitores Executados Automaticamente:**
- ✅ **Subordinação**: Índice de subordinação com limites (**IMPLEMENTADO**)
- ✅ **Inadimplência**: Janelas customizáveis (30d, 90d, etc.) (**IMPLEMENTADO**)
- ✅ **PDD**: Provisão para devedores duvidosos com lógica por cedente (**IMPLEMENTADO - 2025-07-14**)
- ✅ **Concentração**: Sacados/cedentes individuais e top-N (**IMPLEMENTADO - 2025-07-18**)
- ✅ **Análise de Liquidez**: Cobertura de amortizações (3 cenários) (**IMPLEMENTADO - 2025-07-18**)
- 🔄 **Vencimento médio**: Prazo médio ponderado (planejado)
- 🔄 **Elegibilidade**: Critérios de ativos (planejado)
```

## Estado Atual da Implementação

### 🎆 Melhorias de Qualidade Implementadas (Reorganização 2025-07-24)
- **Estrutura reorganizada**: Código fonte movido para `src/`, scripts para `scripts/`
- **Documentação otimizada**: 40% de redução de redundância com estrutura modular em `docs/`
- **Legacy removido**: Diretório `legacy/` completamente eliminado (sistema Excel antigo)
- **Arquivos obsoletos removidos**: `import_helper.py`, `path_resolver.py` eliminados
- **Funções limpas**: 3 funções não utilizadas removidas (`run_cash_flow_comparison`, `run_multi_pool_analysis`, `integrate_with_main_orchestrator`)
- **Nomes encurtados**: Funções renomeadas para melhor legibilidade
- **Cache limpo**: Arquivos Python cache removidos
- **Documentação de exceções**: Adicionada ao `run_monitoring()`
- **Entry points centralizados**: Scripts executivos organizados em `scripts/`

### ✅ Concluído no Sistema Atual (src/monitor/)
- **Arquitetura modular** com monitores especializados
- **Data loader centralizado** com descoberta automática
- **Monitor de subordinação** com cálculo IS correto ✅ **IMPLEMENTADO**
- **Monitor de inadimplência** com enriquecimento progressivo, matriz detalhada de atrasos e aging configurável ✅ **IMPLEMENTADO - Atualizado 2025-07-15**
- **Monitor de PDD** com arquitetura inteligente e lógica por cedente ✅ **IMPLEMENTADO - 2025-07-14** ⚠️ **CCB não implementada**
- **Sistema de cache** integrado automaticamente
- **Orquestrador** com execução condicional de monitores (5 monitores integrados: subordinação, inadimplência, PDD, concentração, liquidez)
- **7 pools auditados e padronizados** em JSON v2.2
- **JSON otimizado para monitoramento** (template v2.2 organizado em 5 seções)
- **Estrutura flexível de concentração** (top_N genérico)
- **Consolidação de limites** dispersos em `limites_monitoramento`
- **Mapeamento de eventos de monitoramento** organizados por categoria (7 base + customizados)
- **Auditoria sistemática completa**: 100% de dados verificados contra escrituras originais
- **Padronização de formatos**: Percentuais em decimal, cronogramas corrigidos
- **Template como fonte única de verdade**: Reorganizado em 5 seções lógicas
- **Enriquecimento progressivo**: Sistema de dados globais otimizado (dias_atraso, grupo_de_risco)
- **Arquitetura inteligente PDD**: Lógica por cedente com reutilização de dados enriquecidos
- **Separação de responsabilidades**: PDD como monitor independente mas dependente do enriquecimento
- **Matriz detalhada de atrasos**: Lista completa de títulos atrasados com consolidações por cedente/sacado (2025-07-15)
- **Aging configurável**: Faixas de aging baseadas na configuração PDD de cada pool (2025-07-15)

- **Monitor de concentração** com arquitetura OOP e compatibilidade 100% ✅ **IMPLEMENTADO - 2025-07-17**
- **Análise de liquidez** com 3 cenários (otimista, prevista, conservadora) ✅ **IMPLEMENTADO - 2025-07-18**
- **Integração híbrida** da análise de liquidez (standalone + integrada) ✅ **IMPLEMENTADO - 2025-07-18**

### 🔄 Em Desenvolvimento
- **Monitor de elegibilidade** (critérios gerais de ativos)
- **Monitores customizados específicos** (20+ identificados por pool)
- **Dashboard de exceções** (HTML gerado em `data/output/monitoring_results/dashboard/`)
- Sistema de histórico de resultados
- **Estratégia de armazenamento** (daily_consolidated implementada)

### 🔄 Funções Renomeadas (Refatoração de Legibilidade)
- `calculate_concentration_consecutive_violation_days` → `calc_consecutive_violations`
- `generate_concentration_summary_table` → `gen_concentration_table`
- **Motivo**: Nomes encurtados para melhor legibilidade e manutenção
- **Compatibilidade**: Funções antigas removidas, apenas novas interfaces disponíveis

### 📁 Documentação Reorganizada (40% Redução de Redundância)

**Nova estrutura modular em `docs/`:**
- **`docs/user-guide/`** - Para usuários finais (getting-started.md, examples.md)
- **`docs/api/`** - Para integradores (drilldown.md, pdd-hierarchy.md) 
- **`docs/developer/`** - Para desenvolvedores (scripts-reference.md, data-processing.md)
- **`docs/technical/`** - Análises técnicas avançadas (SYSTEM_STATE.md, VALIDACAO_SCHEMA_JSON.md)
- **`docs/legal/`** - Documentação legal processada
- **`docs/assets/`** - Recursos visuais centralizados

**Benefícios:**
- ✅ Eliminação de duplicação entre documentos
- ✅ Navegação clara por tipo de usuário
- ✅ Índice principal navegável em `docs/README.md`
- ✅ Separação entre documentação técnica e operacional

### 📋 Mapeamento Real de Eventos de Monitoramento

#### **🏗️ Eventos Base (7 principais - Template v2.2)**
Padronizados e implementados em todos os pools via `monitoramentos_ativos`:

**1. SUBORDINAÇÃO (2 eventos base)**
- `subordinacao` - Índice mínimo de subordinação ✅ **IMPLEMENTADO**
- `subordinacao_critica` - Limite crítico de subordinação ✅ **IMPLEMENTADO**

**2. INADIMPLÊNCIA (2 eventos base)**
- `inadimplencia_30_dias` - Inadimplência 30+ dias (limite: 3-4%) ✅ **IMPLEMENTADO**
- `inadimplencia_90_dias` - Inadimplência 90+ dias (limite: 2%) ✅ **IMPLEMENTADO**

**3. PDD (1 evento base)**
- `pdd` - Provisão para Devedores Duvidosos (grupos AA-H) ✅ **IMPLEMENTADO**

**4. CONCENTRAÇÃO (2 eventos base)**
- `concentracao_sacados` - Concentração máxima por sacado individual ✅ **IMPLEMENTADO - 2025-07-18**
- `concentracao_cedentes` - Concentração máxima por cedente individual ✅ **IMPLEMENTADO - 2025-07-18**

**5. LIQUIDEZ (1 evento base)**
- `analise_liquidez` - Análise de cobertura de amortizações (3 cenários) ✅ **IMPLEMENTADO - 2025-07-18**

**6. ELEGIBILIDADE (1 evento base)**
- `elegibilidade_geral` - Critérios gerais de elegibilidade de ativos 🔄 **PLANEJADO**

#### **⚙️ Eventos Customizados por Pool (20+ identificados)**
Específicos por características de cada pool:

**🔧 SUPERSIM POOL #1 (Custom)**
- `recovery_rate_mensal` - Taxa de recuperação mínima 95%
- `concentracao_socinal` - Limite específico SOCINAL
- `concentracao_bmp` - Limite específico BMP

**🔧 UPVENDAS POOL #2 (Custom)**
- `substituicao_pix_parcelado` - Substituição PIX → URs
- `despesas_adicionais_maximas` - Limite despesas extras

**🔧 AFA POOL #1 (Custom)**
- `sacados_especificos_bmp` - Limites diferenciados BMP
- `sacados_especificos_socinal` - Limites diferenciados SOCINAL

**🔧 COMUM A MÚLTIPLOS POOLS (Legacy)**
- `vencimento_medio_carteira` - Prazo médio ponderado (80-90 dias)
- `valor_minimo_direito_creditorio` - Valor mínimo por ativo (R$ 100-1.000)
- `valor_individual_maximo` - Valor máximo por ativo (R$ 300k-500k)
- `taxa_minima_financiamento` - Taxa mínima (150% CDI)
- `periodo_formacao_carteira` - Período inicial (30-90 dias)
- `prazo_limite_aquisicoes` - Prazo para aquisições (11-36 meses)
- `provisoes_pdd` - Provisões grupos AA-H
- `fundos_reserva` - Reservas obrigatórias
- `concentracao_top_10_sacados` - Top 10 sacados
- `concentracao_top_10_cedentes` - Top 10 cedentes
- `vencimento_individual_minimo` - Vencimento mínimo (3-15 dias)
- `vencimento_individual_maximo` - Vencimento máximo (45-360 dias)

#### **📊 Estatísticas Reais (Atualização 2025-07-18)**
- **Eventos base padronizados**: 7 (template v2.2)
- **Eventos base implementados**: 6/7 (86% - Subordinação + Inadimplência + PDD + Concentração)
- **Eventos customizados identificados**: 20+ (JSONs legacy)
- **Total de combinações únicas**: 25+ eventos distintos
- **Pools com eventos customizados**: 100% (todos têm particularidades)
- **Sistema de enriquecimento**: Operacional (dias_atraso, grupo_de_risco)
- **Arquitetura inteligente**: PDD implementado com dependência otimizada

## Problemas Técnicos Resolvidos

### ✅ 1. Inconsistência de Nomenclatura (RESOLVIDO - 2025-07-11)
**Problema**: Dados CSV/XLSX usavam `LeCapital Pool #1`, mas JSONs eram `lecapital_pool_1_monitoring.json`
**Impacto**: Sistema precisava de mapeamentos manuais, falhas de matching automático
**Solução**: Padronização total para formato dos dados de produção
**Resultado**: 7/7 pools com matching automático 100% funcional

**Arquivos Renomeados**:
- `lecapital_pool_1_monitoring.json` → `LeCapital Pool #1.json`
- `afa_pool_1_monitoring.json` → `AFA Pool #1.json`
- `credmei_pool_1_monitoring.json` → `Credmei Pool #1.json`
- `supersim_pool_1_monitoring.json` → `SuperSim Pool #1.json`
- `a55_pool_cartao_2_monitoring.json` → `a55 Pool #2.json`
- `formento_pool_3_monitoring.json` → `Formento Pool #3.json`
- `upvendas_pool_2_monitoring.json` → `Up Vendas Pool #2.json`

**Benefícios Alcançados**:
- ✅ Eliminou mapeamentos manuais hardcoded
- ✅ Sistema de descoberta automática funcional  
- ✅ Compatibilidade total CSV ↔ JSON ↔ XLSX
- ✅ Facilita debug e manutenção
- ✅ Escalabilidade para novos pools

### ✅ 2. Incompatibilidade de Estruturas OOP (RESOLVIDO - 2025-07-17)
**Problema**: Monitor de concentração OOP tinha diferenças críticas com versão original
**Impacto**: Testes falhando, sistema de filtros incorreto, campos com nomes diferentes
**Solução**: Correções em 4 áreas críticas aplicadas
**Resultado**: 100% compatibilidade alcançada (2/2 pools testados)

**Correções Aplicadas**:
- **Sistema de filtros**: `entity_type` → `f"{entity_type}s"` (plural)
- **Estrutura de campos**: `concentracao_agregada` → `concentracao_top_n`
- **Sub-campos**: `valor_total` → `valor_absoluto`
- **Compatibilidade**: Removido `detalhes_top_n` inexistente no original
- **Lógica de cálculo**: Correção para espaço negativo = 0

**Benefícios Alcançados**:
- ✅ Monitor de concentração 100% compatível
- ✅ Testes de regressão aprovados
- ✅ Sistema pronto para produção
- ✅ Infraestrutura OOP validada para outros monitores

### ✅ 3. Integração da Análise de Liquidez (RESOLVIDO - 2025-07-18)
**Problema**: Análise de liquidez implementada mas não integrada ao orquestrador
**Impacto**: Funcionalidade isolada, sem integração com outros monitores
**Solução**: Integração híbrida com duas interfaces
**Resultado**: 100% funcional em modo standalone e integrado

**Implementação Híbrida**:
- **Interface Standalone**: `run_liquidity_analysis()` para análises independentes
- **Interface Integrada**: Automática dentro de `run_monitoring()` quando cronograma existe
- **Enriquecimento Compartilhado**: Reutiliza dados enriquecidos (dias_atraso, grupo_de_risco)
- **Cenários Implementados**: Otimista, Prevista, Conservadora com cobertura completa

**Benefícios Alcançados**:
- ✅ Duas interfaces funcionais (standalone + integrada)
- ✅ Compatibilidade com variações de colunas CSV/XLSX
- ✅ Enriquecimento automático de dados quando necessário
- ✅ Integração com 5 monitores no orquestrador principal

### ✅ 3. Validação de Consistência de Datas (RESOLVIDO - 2025-07-18)
**Problema**: Arquivos CSV e XLSX podiam ter datas diferentes, causando inconsistências nos dados históricos
**Impacto**: Data do JSON histórico podia estar incorreta, dificultando análises temporais
**Solução**: Sistema automático de validação e extração de datas dos nomes dos arquivos
**Resultado**: 100% consistência temporal e data correta nos arquivos de histórico

**Sistema Implementado**:
- **DateConsistencyValidator**: Extrai datas dos nomes de arquivos usando regex
- **Validação automática**: Integrada no pipeline de carregamento (data_loader.py)
- **Preservação de metadados**: execution_date preservado através do sistema
- **Persistência correta**: Arquivos JSON salvos com data extraída dos arquivos fonte

**Fluxo de Validação**:
```python
# 1. Extração automática de datas
csv_date = validator.extract_date_from_filename("AcompanhamentoDeOportunidades-2025-07-18.csv")
xlsx_date = validator.extract_date_from_filename("Carteira Global 2025-07-18.xlsx")

# 2. Validação de consistência
validation = validator.validate_date_consistency(csv_path, xlsx_path)
if validation["consistent"]:
    execution_date = validation["recommended_execution_date"]
    
# 3. Uso na persistência
persistence.save_daily_results(results)  # Salva em "2025-07-18.json"
```

**Formatos Suportados**:
- `YYYY-MM-DD` (2025-07-18)
- `YYYY-MM-DD HH_MM_SS` (2025-07-15 09_33_29)
- `YYYY-MM-DD HHMMSS` (2025-07-15 070048)
- `DD/MM/YYYY` (18/07/2025)

**Benefícios Alcançados**:
- ✅ Arquivos JSON históricos com datas corretas dos dados fonte
- ✅ Validação automática de consistência CSV ↔ XLSX
- ✅ Alertas para inconsistências temporais
- ✅ Metadados preservados através do pipeline completo
- ✅ Análise temporal delta (D-1) agora utiliza datas reais dos arquivos

## Problemas Técnicos a Resolver

### 1. Gestão de Particularidades (20% Customizado)
**Problema**: Cada escritura tem regras específicas além do padrão comum.
**Solução Proposta**: Sistema de plugins de monitoramento
```python
# monitors/base/ - Monitores padrão (80%)
# monitors/custom/pool_name/ - Monitores específicos (20%)
# monitors/cash_flow/ - Análise de fluxo de caixa e liquidez
```

### 2. Performance com Arquivos Grandes
**Problema**: XLSX diários podem ter >100MB e >50k linhas.
**Soluções**:
- Processamento incremental (delta apenas)
- Leitura seletiva de colunas
- Cache com TTL inteligente
- Processamento paralelo por pool

### 3. Versionamento e Auditoria
**Problema**: Compliance exige histórico completo de mudanças.
**Solução**: Adicionar metadados em cada execução
```json
{
  "execution_id": "uuid",
  "timestamp": "ISO-8601",
  "data_sources": {"csv": "hash", "xlsx": "hash"},
  "changes_detected": []
}
```

### 4. Limites Dinâmicos por Período
**Problema**: Alguns limites mudam (ex: formação vs operação).
**Solução**: Configuração temporal de limites
```json
"limites": [
  {"vigencia": "2025-03-18/2025-05-17", "valor": 0.50},
  {"vigencia": "2025-05-18/null", "valor": 0.35}
]
```

### 5. Parsing de PDFs de Escrituras
**Problema**: Extrair dados estruturados de documentos legais.
**Desafios**:
- Variação de formato entre escrituras
- Termos legais em português jurídico
- Tabelas e anexos complexos
- Aditamentos que modificam termos

## Padrões de Código

### Nomenclatura
- Funções: `snake_case`
- Classes: `PascalCase`
- Constantes: `UPPER_SNAKE_CASE`
- Arquivos: `snake_case.py`

### Estrutura de Monitores
```python
class MonitorBase:
    def validar_dados(self, df): pass
    def calcular(self, df, config): pass
    def gerar_resultado(self, valor, limite): pass
```

### Tratamento de Erros
- Validação de entrada em todas as funções
- Mensagens claras em português
- Fallback para valores seguros
- Log detalhado para debug

## Princípios de Desenvolvimento e Arquitetura

### 🎯 Mentalidade de Desenvolvimento Sênior
- **SEMPRE pensar como dev senior e arquiteto de soluções**
- **NUNCA ser agreeable se houver propostas melhores**
- **Questionar decisões técnicas** e propor alternativas superiores
- **Priorizar qualidade de código** sobre velocidade de entrega
- **Focar em performance** desde o design inicial
- **Cobrir pontos cegos** através de análise crítica e revisão sistemática

### 🏗️ Princípios Arquiteturais SOLID
- **Single Responsibility**: Cada classe/função tem UMA responsabilidade
- **Open/Closed**: Extensível via novos componentes, fechado para modificação
- **Liskov Substitution**: Interfaces consistentes e substituíveis
- **Interface Segregation**: Interfaces específicas por necessidade
- **Dependency Inversion**: Dependências em abstrações, não implementações

### ⚡ Foco em Performance
- **Processamento paralelo** quando possível (pools independentes)
- **Cache inteligente** com TTL adequado
- **Leitura seletiva** de colunas em DataFrames grandes
- **Lazy loading** de configurações e dados
- **Profiling regular** para identificar gargalos

### 🚫 Anti-patterns Proibidos
- **God Classes** (como data_loader.py atual - deve ser refatorado)
- **Business logic em utilitários** (separar responsabilidades)
- **Tight coupling** entre módulos (usar injeção de dependência)
- **Funções com >20 linhas** (quebrar em funções menores)
- **Responsabilidades misturadas** (um arquivo = uma responsabilidade)

### 🔍 Cobertura de Pontos Cegos
- **Code review rigoroso** questionando cada decisão
- **Análise de edge cases** antes da implementação
- **Testes de carga** com datasets grandes (>50k registros)
- **Validação de memória** para operações com DataFrames
- **Disaster recovery** e fallbacks para falhas de sistema

### 📏 Métricas de Qualidade Técnica
- **Cobertura de testes** > 80%
- **Complexidade ciclomática** < 10 por função
- **Duplicação de código** < 5%
- **Tempo de execução** < 30s para processamento completo
- **Uso de memória** < 2GB para datasets padrão

## Arquitetura de Monitoramento

### Estrutura Hierárquica:
```
C:\amfi\
├── src/monitor/
│   ├── base/                          # Monitores padrão (6 eventos base)
│   │   ├── monitor_subordinacao_oop.py    # 2 eventos ✅ IMPLEMENTADO
│   │   ├── monitor_concentracao_oop.py    # 2 eventos ✅ IMPLEMENTADO
│   │   ├── monitor_inadimplencia_oop.py   # 2 eventos ✅ IMPLEMENTADO
│   │   ├── monitor_pdd_oop.py         # 1 evento ✅ IMPLEMENTADO
│   │   ├── monitor_elegibilidade.py   # 1 evento base
│   │   └── monitor_operacional.py     # Eventos legacy/customizados
│   ├── cash_flow/                     # Análise de fluxo de caixa e liquidez
│   │   ├── liquidity_analyzer.py      # ✅ Análise de liquidez (3 cenários)
│   │   ├── base_cash_flow_engine.py   # ✅ Engine base para fluxo de caixa
│   │   ├── pu_analysis_engine.py      # ✅ Modalidade 1: Análise por PU
│   │   ├── pl_percentage_engine.py    # ✅ Modalidade 2: Análise por % PL
│   │   ├── liquidity_scenarios.py     # ✅ Cenários de liquidez
│   │   └── cash_flow_orchestrator.py  # ✅ Orquestrador de fluxo de caixa
│   ├── custom/                        # Monitores específicos por pool
│   │   ├── supersim_pool_1_recovery_rate.py    # 🔧 Taxa de recuperação SuperSim
│   │   ├── afa_pool_1_sacados_especificos.py   # 🔧 Limites especiais BMP, SOCINAL
│   │   ├── upvendas_pool_2_substituicao_pix.py # 🔧 Substituição PIX→URs UpVendas
│   │   └── {pool_id}_{funcionalidade}.py       # Padrão de nomenclatura
│   ├── utils/                         # Utilitários compartilhados
│   │   ├── __init__.py
│   │   ├── alerts.py                  # ✅ Sistema de alertas
│   │   ├── concentration_analysis.py  # ✅ Análise de concentração
│   │   ├── daily_results_persistence.py # ✅ Persistência de resultados
│   │   ├── data_converters.py         # ✅ Conversores de dados
│   │   ├── data_handler.py            # ✅ Validações e metadados
│   │   ├── data_loader.py             # ✅ Carregamento principal (9 etapas)
│   │   ├── date_consistency_validator.py # ✅ Validação de consistência
│   │   ├── file_loaders.py            # ✅ Carregamento CSV/XLSX
│   │   ├── pdd_analysis.py            # ✅ Análise PDD
│   │   └── pdd_api_endpoints.py       # ✅ Endpoints API PDD
│   ├── orchestrator.py                # ✅ Orquestração de monitores (5 monitores integrados)
│   └── [arquivos legacy removidos]    # pool_discovery, monitoring_engine, etc.
└── data/
    ├── config/                        # 📁 Configurações do sistema
    │   └── monitoring/                # Configurações de monitoramento
    │       ├── ignore_pools.json      # Pools ignorados
    │       └── test_pools.json        # Cenários de teste
    ├── csv/                           # Dados gerais dos pools
    ├── xlsx/                          # Dados detalhadas das carteiras
    ├── escrituras/                    # Configurações específicas por pool
    │   └── legacy/                    # JSONs no formato antigo (arquivados)
    └── templates/                     # Templates para novos pools
        └── pool_monitoring_template.json
```

### Estado dos Arquivos Principais (Última Verificação: 2025-07-14)

#### **Estrutura de Dados Real (Variável Diariamente)**
- **CSV Dashboard**: ~45 registros de pools, colunas `nome/sr/jr/pl`
- **XLSX Portfolio**: ~79k registros de recebíveis, 36+ pools, coluna identificadora `pool`
- **Enriquecimento**: Processo temporário durante execução (+2 colunas calculadas)

#### **Arquivos Funcionais Confirmados**
| Arquivo | Status | Interface | Última Verificação |
|---------|--------|-----------|-------------------|
| **data_loader.py** | ✅ FUNCIONAL | `load_pool_data()` | 2025-07-14 (79k registros em 10s) |
| **orchestrator.py** | ✅ FUNCIONAL | `run_monitoring()` | 2025-07-14 (3 monitores integrados) |
| **monitor_subordinacao_oop.py** | ✅ FUNCIONAL | `run_subordination_monitoring()` | 2025-07-14 (integrado) |
| **monitor_inadimplencia_oop.py** | ✅ FUNCIONAL | `run_delinquency_monitoring()` | 2025-07-14 (c/ enriquecimento) |
| **monitor_pdd_oop.py** | ✅ FUNCIONAL | `run_pdd_monitoring()` | 2025-07-14 (arquitetura inteligente) |

### Fluxo de Execução Integrado (Testado e Funcionando):

```
run_monitoring(pool_name=None) [INTERFACE ÚNICA]
    ↓
src.monitor.utils.data_loader.load_pool_data() [CENTRALIZADOR]
    ├── Carrega CSV (~45 pools) + XLSX (~79k registros) + JSONs
    ├── Modo DEBUG: test_pools.json → ['AFA Pool #1', 'LeCapital Pool #1']
    ├── Modo NORMAL: descoberta automática + ignore_pools.json
    └── Retorna: DataFrame XLSX com 16 colunas originais
    ↓
Para cada pool configurado:
    ├── _has_subordination_monitoring(config) ? → run_subordination_monitoring()
    ├── _has_delinquency_monitoring(config) ? → run_delinquency_monitoring()
    │   ├── 1º pool: ENRIQUECE XLSX globalmente (16→18 colunas)
    │   │   ├── +dias_atraso: calculado para todos os 79k registros
    │   │   └── +grupo_de_risco: classificação AA-H para todos
    │   └── 2º pool: REUTILIZA campos já calculados (performance)
    ├── _has_pdd_monitoring(config) ? → run_pdd_monitoring() [USA DADOS ENRIQUECIDOS]
    ├── _has_concentration_monitoring(config) ? → run_concentration_monitoring()
    ├── _has_liquidity_monitoring(config) ? → run_liquidity_monitoring() [USA DADOS ENRIQUECIDOS]
    └── [futuros monitores: usam XLSX já enriquecido]
    ↓
Resultado: DataFrame na memória com 18 colunas (temporário)
Próxima execução: reinicia com 16 colunas originais
```

#### **Processo de Enriquecimento Progressivo (Não Permanente)**
⚠️ **IMPORTANTE**: Enriquecimento acontece DURANTE a execução, não é estado permanente.

**Estados do XLSX**:
- **Inicial**: 16 colunas (dados do arquivo)
- **Durante execução**: 18 colunas (16 + dias_atraso + grupo_de_risco)
- **Fim da execução**: DataFrame enriquecido existe apenas na memória
- **Próxima execução**: Volta ao estado inicial (16 colunas)

### Sistema de Carregamento Refinado:
- **Fluxo de 9 etapas**: CSV → XLSX → Validações → Pools → Ignore List → Filtros → JSON → Filtro XLSX → Validações Pool
- **Sistema de filtros**: Executa todos os pools, pools específicos ou cenários de teste
- **Ignore list**: Pools excluídos automaticamente do monitoramento
- **Log detalhado**: Registro completo de todas as operações
- **Sem hardcode**: Descobre pools automaticamente via arquivos existentes
- **Configuração flexível**: JSON por pool com limites específicos
- **Customizações**: Pools podem ter monitores únicos além dos padrão

### Estratégia de Enriquecimento Progressivo de Dados

#### **Conceito Central**
- **DataFrame XLSX** é passado por referência entre monitores
- **Cada monitor** pode adicionar colunas calculadas
- **Dados enriquecidos** ficam disponíveis para monitores posteriores
- **Evita recálculos** desnecessários e melhora performance

#### **Campos Adicionados por Monitor**
```
Data Original (XLSX):
├── status, vencimento_original, valor_presente, sacado, cedente...

Monitor de Inadimplência adiciona:
├── dias_atraso: int (calculado vs data atual)
├── grupo_de_risco: str (AA, A, B, C, D, E, F, G, H)
└── [PDD fields ficam para v2.0]

Monitores que usam dados enriquecidos:
├── Concentração: usa grupo_de_risco para análise (opcional)
├── Liquidez: usa dias_atraso para cenário conservador
├── Elegibilidade: usará dias_atraso para filtros (futuro)
└── Customizados: usar qualquer campo calculado
```

#### **Vantagens da Abordagem**
- ✅ **Performance**: Cálculos feitos uma vez, usados sempre
- ✅ **Consistência**: Única fonte de verdade para cada cálculo  
- ✅ **Extensibilidade**: Novos monitores reutilizam campos existentes
- ✅ **Auditoria**: Dados enriquecidos persistem na memória

### Funções Padrão por Monitor:

#### **Monitores Base (Padrão 7 eventos)**
- `_find_{monitor_name}_monitor(s)(config)` - Buscar configuração no JSON
- `_has_{monitor_name}_monitoring(config)` - Verificar se monitor está ativo
- `validate_data(df, config)` - Verificação de entrada
- `calculate_{monitor_name}(df, config)` - Cálculo principal  
- `run_{monitor_name}_monitoring(df, config)` - Interface para orquestrador
- **Exemplos**: 
  - `monitor_subordinacao_oop.py` ✅ implementado
  - `monitor_inadimplencia_oop.py` ✅ pronto (aguarda integração)

#### **Monitores Customizados (20+ eventos específicos)**
- Implementação específica por pool conforme necessidade
- Nomenclatura: `{pool_id}_{funcionalidade}.py`
- **🔧 Custom** - Indica monitor específico de pool
- **Exemplos**: 
  - `supersim_pool_1_recovery_rate.py` 
  - `afa_pool_1_sacados_especificos.py`
  - `upvendas_pool_2_substituicao_pix.py`

## Integração com Orquestrador

### Nova Arquitetura Integrada - data_loader como Centralizador

#### **Interface Principal Unificada:**

```python
from src.monitor.orchestrator import run_monitoring

# Processar todos os pools (modo normal ou debug)
resultado = run_monitoring()

# Processar pool específico
resultado = run_monitoring("LeCapital Pool #1")
```

#### **Fluxo Interno do Orquestrador:**

```python
def run_monitoring(pool_name: str = None) -> Dict:
    # 1. data_loader centraliza tudo (descoberta + configuração + carregamento)
    dados = src.monitor.utils.data_loader.load_pool_data()
    
    # 2. Filtrar por pool específico se solicitado
    pools_para_processar = [pool_name] if pool_name else dados["pools_processados"]
    
    # 3. Para cada pool configurado:
    for pool in pools_para_processar:
        config = dados["pools_configs"][pool]
        pool_csv = filter_csv_by_pool(dados["csv_data"], pool)
        
        # 4. Execução condicional baseada no JSON de configuração
        if _has_subordination_monitoring(config):
            resultado_sub = run_subordination_monitoring(pool_csv, config)
            
        if _has_delinquency_monitoring(config):
            # ENRIQUECE o DataFrame XLSX com novos campos
            dados["xlsx_data"] = run_delinquency_monitoring(
                pool_csv, dados["xlsx_data"], config
            )
            
        # Executar monitores que usam dados enriquecidos
        if _has_pdd_monitoring(config):
            resultado_pdd = run_pdd_monitoring(pool_csv, dados["xlsx_data"], config)
            
        if _has_concentration_monitoring(config):
            resultado_conc = run_concentration_monitoring(pool_csv, dados["xlsx_data"], config)
            
        if _has_liquidity_monitoring(config):
            resultado_liquidez = run_liquidity_monitoring(pool_csv, dados["xlsx_data"], config)
```

### Monitor de Subordinação - Interface Atual

O monitor de subordinação está **100% funcional** e integrado ao orquestrador.

#### **Execução Condicional:**
```python
def _has_subordination_monitoring(config: Dict) -> bool:
    """Verifica se monitor de subordinação está ativo no JSON"""
    try:
        monitor = _find_subordination_monitor(config)
        return monitor is not None and monitor.get('ativo', False)
    except ValueError:
        return False
```

### Monitor de Inadimplência - Enriquecimento de Dados

O monitor de inadimplência está **funcionalmente completo** e integrado.

### Monitor de Liquidez - Integração Híbrida

O monitor de liquidez está **100% funcional** com integração híbrida implementada.

#### **Interfaces Disponíveis:**
```python
# Interface Standalone - Para análises independentes
from src.monitor.orchestrator import run_liquidity_analysis
result = run_liquidity_analysis('LeCapital Pool #1')

# Interface Integrada - Dentro do monitoramento completo
from src.monitor.orchestrator import run_monitoring
result = run_monitoring('LeCapital Pool #1')
liquidez_result = result['resultados']['LeCapital Pool #1']['resultados']['liquidez']
```

#### **Cenários Implementados:**
- **Otimista**: Apenas caixa atual vs próximo pagamento
- **Prevista**: Caixa + recebimentos previstos até próximo pagamento
- **Conservadora**: Excluir cedentes/sacados com histórico de atraso (usa dias_atraso)

#### **Estratégia de Enriquecimento (Inadimplência):**
```python
def _has_delinquency_monitoring(config: Dict) -> bool:
    """Verifica se monitores de inadimplência estão ativos no JSON"""
    try:
        monitors = _find_delinquency_monitors(config)  # Função já existe
        return len(monitors) > 0
    except ValueError:
        return False

def run_delinquency_monitoring(csv_df, xlsx_df, config) -> pd.DataFrame:
    """
    Interface para orquestrador - ENRIQUECE DataFrame XLSX
    
    Args:
        csv_df: Dados do pool (PL, SR, JR)
        xlsx_df: Carteira detalhada (será enriquecida)
        config: Configuração JSON do pool
        
    Returns:
        DataFrame XLSX enriquecido com campos adicionais
    """
    # 1. Calcular campos de enriquecimento
    xlsx_enriched = calculate_days_overdue(xlsx_df)  # Adiciona 'dias_atraso'
    
    # 2. Classificar grupos de risco baseado em PDD config
    pdd_grupos = _find_pdd_config(config)
    xlsx_enriched['grupo_de_risco'] = classify_risk_groups(
        xlsx_enriched['dias_atraso'], pdd_grupos
    )
    
    # 3. Executar monitoramento de inadimplência
    resultado_monitoring = calculate_delinquency_analysis(
        xlsx_enriched, csv_df, config
    )
    
    # 4. Retornar DataFrame enriquecido + resultado
    return xlsx_enriched, resultado_monitoring
```

#### **Campos Adicionados ao DataFrame:**
- **`dias_atraso`**: Dias de atraso calculados vs `vencimento_original`
- **`grupo_de_risco`**: Classificação AA-H baseada na configuração PDD
- **[PDD fields]**: Ficam para implementação v2.0

#### **Nova Funcionalidade - Aging Configurável + Drill-down (2025-07-15)**
O sistema de aging analysis agora é configurável baseado na estrutura PDD de cada pool com funcionalidade de drill-down completa:

**Faixas Derivadas do PDD:**
- Cada pool usa suas próprias faixas de aging baseadas em `provisoes_pdd.grupos_risco`
- Exemplo Up Vendas: 1-15, 16-30, 31-60, 61-90, 91-120, 121-150, 151-180, 181+
- Fallback para faixas padrão quando não há configuração PDD

**Drill-down de Ativos (2025-07-15):**
Cada faixa de aging inclui duas formas de acesso aos detalhes dos ativos:
- `detalhes_ativos`: Lista de dicionários (formato original)
- `detalhes_ativos_df`: DataFrame pandas ordenado por cedente, vencimento (antigo primeiro), valor (maior primeiro)

**Estrutura de Retorno:**
```json
{
  "faixas": {
    "31-60": {
      "quantidade": 5,
      "valor": 125000.00,
      "percentual": 15.5,
      "detalhes_ativos": [...],           // Lista de dicionários
      "detalhes_ativos_df": DataFrame     // DataFrame ordenado para análise
    }
  }
}
```

**Benefícios:**
- ✅ Consistência entre análise de risco e monitoramento
- ✅ Flexibilidade por pool
- ✅ Distribuição configurável na matriz de atrasos
- ✅ Drill-down operacional completo por faixa
- ✅ DataFrame pronto para análises avançadas

#### **Nova Funcionalidade - Matriz Detalhada de Atrasos (2025-07-15)**
O monitor de inadimplência agora retorna uma matriz completa de atrasos em `resultado['matriz_atrasos']`:

**Estrutura da Matriz:**
```json
{
  "lista_titulos_atrasados": [
    {
      "cedente": "Nome do Cedente",
      "sacado": "Nome do Sacado",
      "valor_presente": 10000.00,
      "dias_atraso": 45,
      "data_vencimento": "2025-06-01",
      "grupo_de_risco": "D"
    }
  ],
  "consolidado_por_cedente": {
    "Cedente XYZ": {
      "quantidade_titulos": 15,
      "valor_total_atraso": 150000.00,
      "maior_atraso_dias": 120,
      "distribuicao_faixas": {
        "1-30": 5,
        "31-60": 7,
        "61-90": 2,
        "90+": 1
      }
    }
  },
  "consolidado_por_sacado": {
    "Sacado ABC": {
      "quantidade_titulos": 8,
      "valor_total_atraso": 80000.00,
      "quantidade_cedentes": 3,
      "lista_cedentes": ["Cedente X", "Cedente Y", "Cedente Z"]
    }
  },
  "estatisticas_gerais": {
    "total_titulos_atrasados": 150,
    "valor_total_em_atraso": 1500000.00,
    "atraso_medio_dias": 42.5,
    "quantidade_cedentes_afetados": 25,
    "quantidade_sacados_afetados": 85
  }
}
```

**Utilidades:**
- ✅ Análise granular de atrasos por título
- ✅ Visão consolidada por cedente e sacado
- ✅ Base para relatórios gerenciais de inadimplência
- ✅ Identificação de padrões de atraso

#### **Contrato de Dados:**

**Input:**
- `df`: DataFrame com colunas obrigatórias: `sr`, `jr`, `pl` (minúsculas, valores numéricos)
- `config`: JSON com estrutura `monitoramentos_ativos` contendo monitor `id="subordinacao"`

**Output de Sucesso:**
```json
{
  "sucesso": true,
  "monitor": "subordination_ratio",
  "subordination_ratio": 0.2518,
  "subordination_ratio_percent": 25.18,
  "limite_minimo": 0.25,
  "limite_critico": 0.20,
  "status_limite_minimo": "enquadrado",
  "status_limite_critico": "enquadrado",
  "aporte_necessario": {
    "para_limite_minimo": 0.0,
    "para_limite_critico": 0.0
  },
  "dados_financeiros": {
    "pl_atual": 8761240.59,
    "sr_atual": 6555273.93,
    "jr_atual": 2205966.66,
    "denominador_calculo": 8761240.59
  }
}
```

**Output de Erro:**
```json
{
  "sucesso": false,
  "monitor": "subordination_ratio",
  "erro": "Falha na validação de dados"
}
```

#### **Separação de Responsabilidades:**

| Componente | Responsabilidade |
|------------|------------------|
| **Monitor** | • Validar estrutura de dados<br>• Calcular subordination ratio<br>• Verificar limites<br>• Calcular aportes necessários |
| **Orquestrador** | • Carregar dados (CSV/JSON)<br>• Chamar monitor<br>• Logar resultados<br>• Enviar alertas<br>• Persistir resultados |

#### **Estratégia de Tratamento de Erros:**

**Categorização por Severidade:**

**🔥 CRÍTICOS (Parar execução completa):**
- Data source indisponível (CSV não encontrado)
- Sistema de logging falhando  
- Configuração global corrompida
- **Ação**: `return {"sucesso": false, "erro_critico": true}`

**⚠️ ALTOS (Log detalhado + Continue próximo pool):**
- Pool sem JSON de configuração
- Dados malformados em pool específico
- Cálculo com divisão por zero
- **Ação**: Log erro + marcar pool como "erro" + continuar

**💡 BAIXOS (Log simples + Continue):**
- Campos opcionais ausentes
- Valores fora do range esperado
- Timeouts temporários
- **Ação**: Log warning + continuar processamento

**Implementação no Orquestrador:**
1. **Dados Inválidos**: Monitor retorna `{"sucesso": false, "erro": "Falha na validação"}` → Continue próximo pool
2. **Cálculo com Erro**: Monitor retorna `{"sucesso": false, "erro": "Denominador zero"}` → Continue próximo pool  
3. **JSON Malformado**: Monitor retorna `{"sucesso": false, "erro": "Monitor não encontrado"}` → Continue próximo pool
4. **CSV Indisponível**: Orquestrador retorna `{"sucesso": false, "erro_critico": true}` → Parar tudo
5. **Sistema de Retry**: 3 tentativas com backoff exponencial para erros temporários

#### **Exemplo de Integração Completa:**

```python
# monitoring_engine.py
def executar_monitoramento_diario():
    pools = descobrir_pools_ativos()
    
    for pool_name in pools:
        try:
            # NOVO: Execução integrada - TODOS os monitores de uma vez
            resultado = run_monitoring(pool_name)
            
            # Extrair resultados por tipo de monitor
            pool_result = resultado['resultados'][pool_name]
            resultado_sub = pool_result['resultados'].get('subordinacao', {})
            resultado_conc = pool_result['resultados'].get('concentracao', {})
            resultado_inad = pool_result['resultados'].get('inadimplencia', {})
            resultado_pdd = pool_result['resultados'].get('pdd', {})
            resultado_liquidez = pool_result['resultados'].get('liquidez', {})
            
            # Consolidar resultados
            relatorio_pool = {
                "pool": pool_name,
                "data": datetime.now().isoformat(),
                "subordinacao": resultado_sub,
                "concentracao": resultado_conc,
                "inadimplencia": resultado_inad,
                "pdd": resultado_pdd,
                "liquidez": resultado_liquidez
            }
            
            gerar_relatorio_pool(relatorio_pool)
            
        except Exception as e:
            log_alerta({
                "tipo": "erro_critico",
                "pool": pool_name,
                "erro": str(e)
            })
```

#### **Status de Implementação (Atualização 2025-07-18):**

- ✅ **monitor_subordinacao_oop.py**: 100% funcional e testado
- ✅ **monitor_inadimplencia_oop.py**: 100% funcional com enriquecimento
- ✅ **monitor_pdd_oop.py**: 100% funcional com arquitetura inteligente
- ✅ **monitor_concentracao_oop.py**: 100% funcional com arquitetura OOP
- ✅ **liquidity_analyzer.py**: 100% funcional com 3 cenários
- ✅ **Orquestrador**: 100% implementado com 5 monitores integrados
- ✅ **Sistema de enriquecimento**: Operacional (dias_atraso, grupo_de_risco)
- ✅ **Arquitetura de dependências**: PDD e Liquidez usam dados já enriquecidos
- ✅ **Integração híbrida**: Liquidez com interfaces standalone + integrada
- ✅ **Documentação**: Interfaces e contratos atualizados
- ❌ **Classes de erro específicas**: Aguardando implementação
- ❌ **Sistema de retry**: Aguardando implementação
- ❌ **monitoring_engine.py**: Aguardando implementação

## Tracking de Implementação

### ✅ Concluído
- [x] 5 arquivos base criados com funções documentadas
- [x] Estrutura flexível de concentração (top_N genérico)
- [x] JSON otimizado para monitoramento (padrão definido)
- [x] Consolidação de limites em `limites_monitoramento`
- [x] Documentação atualizada com arquitetura
- [x] **Estrutura reorganizada**: Monitores movidos para `/base/` e `/custom/` criado
- [x] **Sistema de utilitários**: 5 arquivos em `/utils/` com esqueletos completos
- [x] **Fluxo de carregamento refinado**: Definido fluxo completo com 9 etapas
- [x] **Sistema de ignore list**: Estrutura para pools ignorados e testes
- [x] **Arquitetura de filtros**: Sistema flexível para executar pools específicos
- [x] **Pasta config/monitoring/**: Criada com ignore_pools.json e test_pools.json
- [x] **data_loader.py**: ✅ COMPLETO - Implementado com fluxo de 9 etapas, todas funções funcionais, código limpo
- [x] **Refatoração para módulos**: data_loader fragmentado em file_loaders, data_handler, alerts, file_discovery
- [x] **Compatibilidade Spyder**: Sistema de imports robusto com fallback automático
- [x] **Funções implementadas**: log_alerta, validar_data_d1, gerar_alerta_nao_d1
- [x] **Auditoria sistemática completa**: 7/7 pools verificados contra escrituras originais
- [x] **Template v2.2**: Reorganizado em 5 seções lógicas com instruções detalhadas
- [x] **Padronização de dados**: Formatos decimais corrigidos, dados inventados removidos
- [x] **Monitores customizados identificados**: 20+ monitores específicos mapeados
- [x] **Monitor de subordinação**: 100% implementado e testado
- [x] **Orquestrador de subordinação**: Implementado com logging e alertas
- [x] **Estratégia de tratamento de erros**: Definida por severidade e categoria
- [x] **Monitor de inadimplência**: 100% implementado com enriquecimento progressivo
- [x] **Monitor de PDD**: 100% implementado com arquitetura inteligente (2025-07-14)
- [x] **Arquitetura de enriquecimento**: Sistema operacional (dias_atraso, grupo_de_risco)
- [x] **Padrões de nomenclatura**: `_find_*_monitor()`, `_has_*_monitoring()`, `run_*_monitoring()`
- [x] **Integração data_loader + orchestrator**: Fluxo centralizado com 5 monitores
- [x] **Monitor de concentração**: 100% implementado com arquitetura OOP (2025-07-18)
- [x] **Análise de liquidez**: 100% implementada com 3 cenários (2025-07-18)
- [x] **Integração híbrida**: Liquidez com interfaces standalone + integrada (2025-07-18)
- [x] **Compatibilidade de colunas**: Sistema flexível para variações CSV/XLSX (2025-07-18)
- [x] **Enriquecimento automático**: Sistema trigger para liquidity analysis (2025-07-18)

### 🔄 Em Desenvolvimento
- [ ] **Classes de erro específicas**: Implementar enum de severidade e classes customizadas
- [ ] **Sistema de retry**: Backoff exponencial para erros temporários
- [ ] Sistema de descoberta automática de pools (`pool_discovery.py`)
- [ ] Engine de orquestração (`monitoring_engine.py`)
- [ ] Carregador de configurações (`config_loader.py`)
- [ ] Gerenciador de alertas (`alert_manager.py`)
- [ ] Implementação das funções nos utilitários
- [ ] Implementação das funções nos monitores base

### ⚠️ Limitações Conhecidas - CCB (Cédula de Crédito Bancário)

**Status**: Lógica CCB **NÃO IMPLEMENTADA** no Monitor PDD

**Problema**: 
- Sistema atual calcula PDD por cedente (lógica padrão)
- CCB requer cálculo PDD por ativo individual
- Todos os títulos CCB recebem provisão do pior ativo do cedente (incorreto)

**Impacto**:
- CCB com 0 dias atraso pode receber provisão alta indevidamente
- Superprovisão em carteiras com CCB misturadas
- Análise de risco distorcida para pools com CCB

**Solução Futura**:
- Implementar detecção de tipo de ativo (CCB vs outros)
- Aplicar lógica por ativo apenas para CCB
- Manter lógica por cedente para demais tipos

**Workaround Atual**:
- Documentação clara sobre limitação
- Monitoramento manual para pools com CCB
- Análise separada quando necessário

**Localização**: `C:\amfi\src\monitor\base\monitor_pdd_oop.py` (docstring atualizado com esta limitação)

### 🚀 Scripts Reorganizados (Entry Points Centralizados)

**Nova localização em `scripts/`:**
- **`scripts/run_monitoring.py`** - API para execução do monitoramento via dashboard
- **`scripts/run_dashboard.py`** - Servidor web do dashboard
- **`scripts/generate_dashboard.py`** - Gerador de dashboard HTML

**Execução dos scripts:**
```bash
# Executar monitoramento completo
python scripts/run_monitoring.py

# Forçar re-execução mesmo se já rodou hoje
python scripts/run_monitoring.py --force

# Iniciar servidor do dashboard
python scripts/run_dashboard.py

# Gerar dashboard HTML estático
python scripts/generate_dashboard.py
```

**Benefícios:**
- ✅ Entry points claramente separados do código fonte
- ✅ Scripts executáveis organizados em um local
- ✅ Imports corrigidos para nova estrutura `src/`
- ✅ Compatibilidade com automação e CI/CD

### 📁 Reorganização de Arquivos (2025-07-15)

**Limpeza de Configurações**:
- ❌ Removido: `config/monitoring/exampl_test_pools.json` (typo)
- ❌ Removido: `config/monitoring/example_ignore_pools.json` (desnecessário)
- ✅ Mantido: `config/monitoring/ignore_pools.json` e `test_pools.json`

**Documentação Técnica Centralizada**:
- 📁 Movido: `docs/SYSTEM_STATE.md` → `docs/technical/SYSTEM_STATE.md`
- 📚 Pasta `docs/technical/` agora contém toda documentação técnica

**Testes Organizados por Tipo**:
- 📁 Movido: `tests/test_inadimplencia_results.py` → `tests/integration/`
- 📁 Movido: `tests/test_spyder_json_loading.py` → `tests/integration/`
- 📂 Estrutura final: `unit/`, `integration/`, `performance/`, `fixtures/`

### 📋 Próximos Passos (Atualização 2025-07-18)
1. ✅ **Criar pasta config/monitoring/** com ignore_pools.json e test_pools.json
2. ✅ **Implementar data_loader.py** com fluxo refinado de 9 etapas - COMPLETO
3. ✅ **Implementar monitor_subordinacao_oop.py** - COMPLETO
4. ✅ **Implementar orquestrador de subordinação** - COMPLETO
5. ✅ **Definir arquitetura de enriquecimento progressivo** - COMPLETO
6. ✅ **Implementar run_monitoring()** - Interface única implementada e testada
7. ✅ **Integrar monitor_inadimplencia_oop.py** com enriquecimento de DataFrame - COMPLETO
8. ✅ **Implementar funções auxiliares** (`_has_*_monitoring()` para cada monitor) - COMPLETO
9. ✅ **Implementar monitor_pdd_oop.py** com arquitetura inteligente - COMPLETO
10. ✅ **Implementar monitor_concentracao_oop.py** (2 eventos base) - COMPLETO
11. **Implementar monitor_elegibilidade.py** (1 evento base)
12. **Criar supersim_pool_1_recovery_rate.py** (🔧 Custom SuperSim)
13. **Criar afa_pool_1_sacados_especificos.py** (🔧 Custom AFA)
14. **Criar upvendas_pool_2_substituicao_pix.py** (🔧 Custom UpVendas)

### 📊 Métricas de Progresso (Atualização 2025-07-24)
- **Pools mapeados**: 9 (lecapital, afa, supersim, credmei, formento, upvendas, a55, dinie, ectare)
- **Pools com JSON otimizado**: 9/9 (100% - template v2.2 aplicado)
- **Auditoria de dados**: 9/9 pools (100% verificados contra escrituras originais)
- **Integridade de dados**: 100% - Zero dados inventados ou incorretos
- **Estrutura reorganizada**: ✅ `src/monitor/`, `scripts/`, `docs/`
- **Monitores base**: 5/6 (83% implementados - apenas elegibilidade restante)
- **Monitores custom**: 0/20+ identificados (recovery_rate, sacados_especificos, veto_aquisicoes, etc.)
- **Utilitários reorganizados**: 10/10 ✅ (todos refatorados e funcionais em `src/monitor/utils/`)
  - data_loader.py: ✅ Orquestrador principal
  - file_loaders.py: ✅ Carregamento CSV/XLSX
  - data_handler.py: ✅ Validações e metadados
  - alerts.py: ✅ Sistema de alertas
  - daily_results_persistence.py: ✅ Persistência de resultados
  - date_consistency_validator.py: ✅ Validação temporal
  - concentration_analysis.py: ✅ Análise de concentração
  - data_converters.py: ✅ Conversores de dados
  - pdd_analysis.py: ✅ Análise PDD
  - pdd_api_endpoints.py: ✅ Endpoints API PDD
- **Scripts executáveis**: ✅ 3/3 (run_monitoring.py, run_dashboard.py, generate_dashboard.py)
- **Fluxo de carregamento**: ✅ COMPLETO - 9 etapas + filtros + ignore list + validações
- **Compatibilidade Spyder**: ✅ COMPLETO - Sistema de imports com fallback
- **Arquivos de configuração**: ✅ 2/2 (ignore_pools.json, test_pools.json)
- **Documentação reorganizada**: ✅ 40% redução de redundância com estrutura modular
- **Template atualizado**: v2.2 com 5 seções lógicas e instruções detalhadas
- **Eventos base mapeados**: 7/7 (template v2.2)
- **Eventos base implementados**: 6/7 (subordinação + inadimplência + PDD + concentração + liquidez ✅)
- **Eventos customizados identificados**: 20+ (específicos por pool)
- **Monitores base implementados**: 5/6 (subordinação ✅, inadimplência ✅, PDD ✅, concentração ✅, liquidez ✅)
- **Monitores customizados implementados**: 0/20+
- **Orquestradores implementados**: 1/1 (5 monitores integrados)
- **Estratégia de enriquecimento**: 100% operacional (dias_atraso, grupo_de_risco)
- **Arquitetura inteligente**: PDD e Liquidez implementados com dependência otimizada
- **Compatibilidade OOP**: 100% validada (concentração testado em 2 pools)
- **Integração híbrida**: 100% funcional (liquidez standalone + integrada)
- **Compatibilidade de colunas**: Sistema flexível para variações CSV/XLSX

## Dependências Principais
- xlwings: Interface Excel
- pandas: Processamento de dados
- openpyxl: Leitura de XLSX
- json: Configurações
- **Spyder**: IDE principal para desenvolvimento e testes

## Ambiente de Desenvolvimento

### Execução no Spyder
O sistema foi desenvolvido e é testado principalmente no **Spyder IDE**. Para executar o data_loader:

```python
# No console do Spyder, navegue até o diretório do projeto
cd C:\amfi

# Execute o data_loader
from src.monitor.utils.data_loader import load_pool_data
resultado = load_pool_data()

# Para debug específico de pools
from src.monitor.utils.data_loader import load_pool_data
resultado = load_pool_data(data="07/07/2025")  # Data específica

# Execute análise de liquidez
from src.monitor.orchestrator import run_liquidity_analysis
resultado_liquidez = run_liquidity_analysis('LeCapital Pool #1')

# Execute monitoramento completo
from src.monitor.orchestrator import run_monitoring
resultado_completo = run_monitoring('LeCapital Pool #1')

# Alternativamente, use os scripts reorganizados:
python scripts/run_monitoring.py
```

### Compatibilidade de Imports
O código foi refatorado para suportar diferentes contextos de execução:
- **Imports relativos**: Para execução como módulo Python
- **Imports diretos**: Para execução no Spyder (fallback automático)
- **Imports absolutos**: Para execução em outros ambientes

### Estrutura de Imports Robusta
Todos os arquivos em `monitor/utils/` usam o seguinte padrão:
```python
# Tentar imports relativos primeiro
try:
    from .modulo import funcao
except (ImportError, ValueError):
    # Fallback para imports diretos (Spyder)
    if os.path.dirname(__file__) not in sys.path:
        sys.path.insert(0, os.path.dirname(__file__))
    from modulo import funcao
```

## Documentação Disponível

### Documentação Principal
- **[CLAUDE.md](./CLAUDE.md)** - Documentação principal do sistema (este arquivo)
- **[PRD.md](./PRD.md)** - Product Requirements Document com objetivos e roadmap

### Processos Operacionais (`docs/processos/`)
- **[PROCESSO_EXTRACAO_SISTEMATICA.md](./processos/PROCESSO_EXTRACAO_SISTEMATICA.md)** - Metodologia para extrair features de documentos legais
- **[CHECKLIST_EXTRACAO_FEATURES.md](./processos/CHECKLIST_EXTRACAO_FEATURES.md)** - Checklist operacional para extração de features

### Documentação Técnica (`docs/technical/`)
- **[VALIDACAO_SCHEMA_JSON.md](./technical/VALIDACAO_SCHEMA_JSON.md)** - Diretrizes para validação de schema JSON e compatibilidade Python

### Documentação de Sessões (`docs/sessions/`)
- **[refatoracao_concentracao_20250717.md](./sessions/refatoracao_concentracao_20250717.md)** - Refatoração completa do monitor de concentração com compatibilidade 100%

## Contato e Sessões
- **Última atualização**: 2025-07-24
- **Sessão atual**: Reorganização completa da estrutura de arquivos e documentação
- **Próxima revisão**: Monitor de elegibilidade ou estratégia de armazenamento
- **Status da reorganização**: ✅ COMPLETA - Sistema legacy removido, estrutura limpa implementada

### 📁 **Filosofia do docs/sessions/**

**PROPÓSITO EXCLUSIVO**: Lista de tarefas organizadas por data de sessão

**CONTEÚDO PERMITIDO**:
- ✅ To-dos priorizados com checkboxes [ ]
- ✅ Status de progresso (x/y tarefas concluídas)
- ✅ Próxima tarefa prioritária a executar
- ✅ Ordem de implementação recomendada

**CONTEÚDO ESTRITAMENTE PROIBIDO**:
- ❌ Descobertas técnicas → docs/technical/SYSTEM_STATE.md
- ❌ Definições de arquitetura → docs/CLAUDE.md  
- ❌ Checklists e processos → docs/processos/
- ❌ Documentação detalhada → docs/technical/
- ❌ Métricas de performance → docs/technical/SYSTEM_STATE.md
- ❌ Interfaces e código → docs/CLAUDE.md
- ❌ Análises e explicações → docs/technical/

**FORMATO PADRÃO**: Apenas listas estruturadas com prioridades (Alta/Média/Baixa)

### 📋 **Sistema de To-Do por Sessão**
**TODA NOVA SESSÃO** deve seguir este processo:
1. **Criar arquivo**: `docs/sessions/to_do_YYYYMMDD.md`
2. **Listar tarefas**: Incluir tarefas pendentes + novas do dia
3. **Escolher foco**: Selecionar quais tarefas abordar na sessão
4. **Adicionar dinamicamente**: Conforme surgem novas demandas
5. **MANTER FOCO**: Apenas to-dos, sem documentação técnica

**Arquivo atual**: [to_do_20250718.md](./sessions/to_do_20250718.md)

### ⚠️ **IMPORTANTE - Sincronia de Documentos**
**SEMPRE VERIFICAR** em cada sessão se CLAUDE.md e PRD.md estão sincronizados:
- **CLAUDE.md**: Documento principal completo (negócio + técnico)
- **PRD.md**: Resumo executivo para stakeholders
- **Verificar**: Objetivos, roadmap e métricas alinhados entre os documentos
- **Atualizar**: Ambos documentos quando houver mudanças significativas