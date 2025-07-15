# AmFi - Sistema de Monitoramento de Portfólio

> **IMPORTANTE**: Sempre utilizar Claude Sonnet 4.0 para trabalhar neste projeto.

## Contexto do Projeto
Sistema de monitoramento automatizado para fundos de investimento estruturados no Brasil. Processa escrituras de debêntures (PDFs) em configurações JSON para executar monitoramento de compliance, análise de fluxo de caixa e verificação de liquidez.

## 🔄 Transformações de Dados Críticas

### **📝 Normalização de Colunas (IMPORTANTE para desenvolvimento)**

⚠️ **TODA SESSÃO NOVA DEVE SABER**: O sistema transforma automaticamente nomes de colunas:

```python
# Função: normalize_column_name() em data_converters.py
'Nome do Sacado' → 'nome_do_sacado'
'Nome do Cedente' → 'nome_do_cedente'  
'Valor presente (R$)' → 'valor_presente'
'Taxa de Juros a.m.' → 'taxa_de_juros_am'
'Data de Vencimento' → 'data_de_vencimento'
```

**Transformações aplicadas:**
- Converte para minúsculas
- Remove (R$), (RS) e variações
- Substitui espaços por underscore
- Remove acentos (ç→c, ã→a, é→e, etc.)
- Remove caracteres especiais ((), $, %, -, etc.)
- Remove underscores duplicados

**⚠️ IMPLICAÇÕES PARA CÓDIGO:**
- ✅ **USE**: `df['nome_do_sacado']` nos monitores
- ❌ **NÃO USE**: `df['Nome do Sacado']` (vai dar erro)
- ✅ **USE**: `df['valor_presente']` para valores monetários
- ❌ **NÃO USE**: `df['Valor presente']` (vai dar erro)

### **💰 Conversões Monetárias e Percentuais**

**Conversões automáticas aplicadas pelo data_loader:**
- **Monetários**: `R$ 1.234.567,89` → `1234567.89` (float)
- **Percentuais**: `25,50%` → `0.2550` (decimal)
- **Datas**: `01/01/2025` → `datetime` (formato brasileiro)

**Performance:**
- Datasets >1000 registros: Conversão vetorizada (50-100x mais rápida)
- Datasets menores: Conversão tradicional com .apply()

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
5. **Análise de Liquidez**: Cobertura de amortizações futuras

## Estrutura de Diretórios
```
/mnt/c/amfi/
├── legacy/                  # ⚠️ SISTEMA ANTIGO (xlwings) - NÃO USAR
│   ├── README.md           # Documentação do sistema legacy
│   ├── .gitignore          # Ignora conteúdo legacy no git
│   ├── udfs/               # UDFs Excel antigas (xlwings)
│   ├── amfi.xlam           # Add-in Excel antigo
│   └── Monitoramento.xlsm  # Workbook Excel antigo
├── monitor/                 # ✅ SISTEMA ATUAL (Python puro)
│   ├── base/               # Monitores padrão
│   ├── custom/             # Monitores específicos por pool
│   ├── utils/              # Utilitários compartilhados
│   └── orchestrator.py     # Interface principal do sistema
├── config/                  # ⚙️ CONFIGURAÇÕES ESTÁTICAS
│   ├── monitoring/         # Configurações de monitoramento
│   │   ├── test_pools.json # Pools para modo DEBUG
│   │   └── ignore_pools.json # Pools a ignorar
│   └── pools/              # Configurações de pools
│       ├── *.json          # JSONs ativos dos pools
│       └── legacy/         # JSONs antigos (histórico)
├── data/                    # 💾 DADOS DINÂMICOS APENAS
│   ├── input/              # Dados de entrada diários
│   │   ├── csv/            # CSVs diários (PL, SR, JR)
│   │   └── xlsx/           # Carteiras detalhadas (recebíveis)
│   └── output/             # Resultados processados
│       └── monitoring_results/ # Outputs de monitoramento por pool
├── assets/                  # 📄 RECURSOS ESTÁTICOS
│   ├── legal_docs/         # Escrituras originais em markdown
│   └── screenshots/        # Screenshots e evidências
├── docs/                    # 📚 DOCUMENTAÇÃO DO PROJETO
│   ├── processos/          # Checklists e processos operacionais
│   ├── sessions/           # APENAS to-dos por data (sem documentação técnica)
│   └── technical/          # Documentação técnica detalhada
├── scripts/                 # 🔧 SCRIPTS ADMINISTRATIVOS
│   └── run_data_loader.py  # Script para executar data_loader
└── tests/                   # 🧪 TESTES ORGANIZADOS
    ├── unit/               # Testes unitários
    ├── integration/        # Testes de integração (scripts específicos)
    ├── performance/        # Testes de performance
    └── fixtures/           # Dados de teste (vazio)
```

## ⚠️ Sistema Legacy vs Sistema Atual

### **❌ Sistema Legacy (NÃO USAR)**
- **Local**: `/legacy/`
- **Tecnologia**: xlwings + Excel UDFs
- **Arquivos**: `udfs/`, `amfi.xlam`, `Monitoramento.xlsm`
- **Status**: **SUBSTITUÍDO** - Mantido apenas para referência histórica
- **Problemas**: Dependente do Excel, difícil manutenção, duplicação de código

### **✅ Sistema Atual (USAR ESTE)**
- **Local**: `/monitor/`
- **Tecnologia**: Python puro + JSON configs
- **Interface**: `run_monitoring()` - ÚNICA função oficial
- **Status**: **ATIVO** - Monitores subordinação + inadimplência + PDD implementados
- **Vantagens**: Independente do Excel, modular, testável, escalável

### **🔄 Migração de Funcionalidades**

| **Função Legacy** | **Sistema Atual** | **Status** |
|-------------------|-------------------|------------|
| `udfs/amfi.py` (UDFs Excel) | `monitor/orchestrator.py` | ✅ Substituído |
| `AmfiDashboard()` | `run_monitoring()` | ✅ Implementado |
| `AmfiXLSX()` | `data_loader.load_pool_data()` | ✅ Melhorado |
| `AmfiConcentracao()` | `monitor_concentracao.py` | 🔄 Em desenvolvimento |
| `AmfiCalcularIS()` | `monitor_subordinacao.py` | ✅ Implementado |
| Cache manual | Cache integrado no data_loader | ✅ Automatizado |

### **📝 Interface Principal: run_monitoring()**

**ÚNICA função oficial do sistema** - Funções legacy removidas em 2025-07-14.

```python
from monitor.orchestrator import run_monitoring

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
```

**Monitores Executados Automaticamente:**
- ✅ **Subordinação**: Índice de subordinação com limites (**IMPLEMENTADO**)
- ✅ **Inadimplência**: Janelas customizáveis (30d, 90d, etc.) (**IMPLEMENTADO**)
- ✅ **PDD**: Provisão para devedores duvidosos com lógica por cedente (**IMPLEMENTADO - 2025-07-14**)
- 🔄 **Concentração**: Sacados/cedentes (planejado)
- 🔄 **Vencimento médio**: Prazo médio ponderado (planejado)
- 🔄 **Elegibilidade**: Critérios de ativos (planejado)
```

## Estado Atual da Implementação

### ✅ Concluído no Sistema Atual (/monitor/)
- **Arquitetura modular** com monitores especializados
- **Data loader centralizado** com descoberta automática
- **Monitor de subordinação** com cálculo IS correto ✅ **IMPLEMENTADO**
- **Monitor de inadimplência** com enriquecimento progressivo, matriz detalhada de atrasos e aging configurável ✅ **IMPLEMENTADO - Atualizado 2025-07-15**
- **Monitor de PDD** com arquitetura inteligente e lógica por cedente ✅ **IMPLEMENTADO - 2025-07-14** ⚠️ **CCB não implementada**
- **Sistema de cache** integrado automaticamente
- **Orquestrador** com execução condicional de monitores (3 monitores integrados: subordinação, inadimplência, PDD)
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

### 🔄 Em Desenvolvimento
- **Monitor de concentração** (sacados/cedentes individuais)
- **Monitor de elegibilidade** (critérios gerais de ativos)
- **Monitores customizados específicos** (20+ identificados por pool)
- Dashboard de exceções
- Análise de fluxo de caixa
- Sistema de histórico de resultados

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
- `concentracao_sacados` - Concentração máxima por sacado individual 🔄 **PLANEJADO**
- `concentracao_cedentes` - Concentração máxima por cedente individual 🔄 **PLANEJADO**

**5. ELEGIBILIDADE (1 evento base)**
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

#### **📊 Estatísticas Reais (Atualização 2025-07-14)**
- **Eventos base padronizados**: 7 (template v2.2)
- **Eventos base implementados**: 5/7 (71% - Subordinação + Inadimplência + PDD)
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

## Problemas Técnicos a Resolver

### 1. Gestão de Particularidades (20% Customizado)
**Problema**: Cada escritura tem regras específicas além do padrão comum.
**Solução Proposta**: Sistema de plugins de monitoramento
```python
# monitors/base/ - Monitores padrão (80%)
# monitors/custom/pool_name/ - Monitores específicos (20%)
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
/mnt/c/amfi/
├── monitor/
│   ├── base/                          # Monitores padrão (7 eventos base)
│   │   ├── monitor_subordinacao.py    # 2 eventos ✅ IMPLEMENTADO
│   │   ├── monitor_concentracao.py    # 2 eventos base
│   │   ├── monitor_inadimplencia.py   # 2 eventos ✅ PRONTO (aguarda integração)
│   │   ├── monitor_elegibilidade.py   # 1 evento base
│   │   └── monitor_operacional.py     # Eventos legacy/customizados
│   ├── custom/                        # Monitores específicos por pool
│   │   ├── supersim_pool_1_recovery_rate.py    # 🔧 Taxa de recuperação SuperSim
│   │   ├── afa_pool_1_sacados_especificos.py   # 🔧 Limites especiais BMP, SOCINAL
│   │   ├── upvendas_pool_2_substituicao_pix.py # 🔧 Substituição PIX→URs UpVendas
│   │   └── {pool_id}_{funcionalidade}.py       # Padrão de nomenclatura
│   ├── utils/                         # Utilitários compartilhados
│   │   ├── data_loader.py             # ✅ Carregamento principal (9 etapas)
│   │   ├── file_loaders.py            # ✅ Carregamento CSV/XLSX
│   │   ├── data_handler.py            # ✅ Validações e metadados
│   │   ├── alerts.py                  # ✅ Sistema de alertas
│   │   └── file_discovery.py          # ✅ Descoberta de arquivos
│   ├── orchestrator.py                # ✅ Orquestração de monitores (parcial)
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
| **monitor_subordinacao.py** | ✅ FUNCIONAL | `run_subordination_monitoring()` | 2025-07-14 (integrado) |
| **monitor_inadimplencia.py** | ✅ FUNCIONAL | `run_delinquency_monitoring()` | 2025-07-14 (c/ enriquecimento) |
| **monitor_pdd.py** | ✅ FUNCIONAL | `run_pdd_monitoring()` | 2025-07-14 (arquitetura inteligente) |

### Fluxo de Execução Integrado (Testado e Funcionando):

```
run_monitoring(pool_name=None) [INTERFACE ÚNICA]
    ↓
data_loader.load_pool_data() [CENTRALIZADOR]
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

Futuros Monitores podem usar:
├── Concentração: usar grupo_de_risco para análise
├── Elegibilidade: usar dias_atraso para filtros
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
  - `monitor_subordinacao.py` ✅ implementado
  - `monitor_inadimplencia.py` ✅ pronto (aguarda integração)

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
from monitor.orchestrator import run_monitoring

# Processar todos os pools (modo normal ou debug)
resultado = run_monitoring()

# Processar pool específico
resultado = run_monitoring("LeCapital Pool #1")
```

#### **Fluxo Interno do Orquestrador:**

```python
def run_monitoring(pool_name: str = None) -> Dict:
    # 1. data_loader centraliza tudo (descoberta + configuração + carregamento)
    dados = data_loader.load_pool_data()
    
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
            
        # Futuros monitores usarão dados já enriquecidos
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

O monitor de inadimplência está **funcionalmente completo** e pronto para integração.

#### **Estratégia de Enriquecimento:**
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
            resultado_conc = pool_result['resultados'].get('concentracao', {})  # Futuro
            resultado_inad = pool_result['resultados'].get('inadimplencia', {})
            
            # Consolidar resultados
            relatorio_pool = {
                "pool": pool_name,
                "data": datetime.now().isoformat(),
                "subordinacao": resultado_sub,
                "concentracao": resultado_conc,
                "inadimplencia": resultado_inad
            }
            
            gerar_relatorio_pool(relatorio_pool)
            
        except Exception as e:
            log_alerta({
                "tipo": "erro_critico",
                "pool": pool_name,
                "erro": str(e)
            })
```

#### **Status de Implementação (Atualização 2025-07-14):**

- ✅ **monitor_subordinacao.py**: 100% funcional e testado
- ✅ **monitor_inadimplencia.py**: 100% funcional com enriquecimento
- ✅ **monitor_pdd.py**: 100% funcional com arquitetura inteligente
- ✅ **Orquestrador**: 100% implementado com 3 monitores integrados
- ✅ **Sistema de enriquecimento**: Operacional (dias_atraso, grupo_de_risco)
- ✅ **Arquitetura de dependências**: PDD usa dados já enriquecidos
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
- [x] **Integração data_loader + orchestrator**: Fluxo centralizado com 3 monitores

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

**Localização**: `/mnt/c/amfi/monitor/base/monitor_pdd.py` (docstring atualizado com esta limitação)

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

### 📋 Próximos Passos (Atualização 2025-07-14)
1. ✅ **Criar pasta config/monitoring/** com ignore_pools.json e test_pools.json
2. ✅ **Implementar data_loader.py** com fluxo refinado de 9 etapas - COMPLETO
3. ✅ **Implementar monitor_subordinacao.py** - COMPLETO
4. ✅ **Implementar orquestrador de subordinação** - COMPLETO
5. ✅ **Definir arquitetura de enriquecimento progressivo** - COMPLETO
6. ✅ **Implementar run_monitoring()** - Interface única implementada e testada
7. ✅ **Integrar monitor_inadimplencia.py** com enriquecimento de DataFrame - COMPLETO
8. ✅ **Implementar funções auxiliares** (`_has_*_monitoring()` para cada monitor) - COMPLETO
9. ✅ **Implementar monitor_pdd.py** com arquitetura inteligente - COMPLETO
10. **Implementar monitor_concentracao.py** (2 eventos base)
11. **Implementar monitor_elegibilidade.py** (1 evento base)
12. **Criar supersim_pool_1_recovery_rate.py** (🔧 Custom SuperSim)
13. **Criar afa_pool_1_sacados_especificos.py** (🔧 Custom AFA)
14. **Criar upvendas_pool_2_substituicao_pix.py** (🔧 Custom UpVendas)

### 📊 Métricas de Progresso
- **Pools mapeados**: 7 (lecapital, afa, supersim, credmei, formento, upvendas, a55)
- **Pools com JSON otimizado**: 7/7 (100% - template v2.2 aplicado)
- **Auditoria de dados**: 7/7 pools (100% verificados contra escrituras originais)
- **Integridade de dados**: 100% - Zero dados inventados ou incorretos
- **Estrutura organizada**: ✅ `/base/`, `/custom/`, `/utils/`
- **Monitores base**: 5/5 (esqueletos criados e organizados)
- **Monitores custom**: 0/20+ identificados (recovery_rate, sacados_especificos, veto_aquisicoes, etc.)
- **Utilitários**: 5/5 ✅ (todos refatorados e funcionais)
  - data_loader.py: ✅ Orquestrador principal
  - file_loaders.py: ✅ Carregamento CSV/XLSX
  - data_handler.py: ✅ Validações e metadados
  - alerts.py: ✅ Sistema de alertas
  - file_discovery.py: ✅ Descoberta de arquivos
- **Sistema de descoberta**: 0/4 (pool_discovery, monitoring_engine, config_loader, alert_manager)
- **Fluxo de carregamento**: ✅ COMPLETO - 9 etapas + filtros + ignore list + validações
- **Compatibilidade Spyder**: ✅ COMPLETO - Sistema de imports com fallback
- **Arquivos de configuração**: ✅ 2/2 (ignore_pools.json, test_pools.json)
- **Template atualizado**: v2.2 com 5 seções lógicas e instruções detalhadas
- **Eventos base mapeados**: 7/7 (template v2.2)
- **Eventos base implementados**: 5/7 (subordinação + inadimplência + PDD ✅)
- **Eventos customizados identificados**: 20+ (específicos por pool)
- **Monitores base implementados**: 3/5 (subordinação ✅, inadimplência ✅, PDD ✅)
- **Monitores customizados implementados**: 0/20+
- **Orquestradores implementados**: 1/1 (3 monitores integrados)
- **Estratégia de enriquecimento**: 100% operacional (dias_atraso, grupo_de_risco)
- **Arquitetura inteligente**: PDD implementado com dependência otimizada

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
cd /mnt/c/amfi

# Execute o data_loader
from monitor.utils.data_loader import load_pool_data
resultado = load_pool_data()

# Para debug específico de pools
from monitor.utils.data_loader import load_pool_data
resultado = load_pool_data(data="07/07/2025")  # Data específica
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

## Contato e Sessões
- Última atualização: 2025-07-14
- Sessão atual: Implementação do monitor PDD com arquitetura inteligente
- Próxima revisão: Monitor de concentração (sacados/cedentes)

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

**Arquivo atual**: [to_do_20250713.md](./sessions/to_do_20250713.md)

### ⚠️ **IMPORTANTE - Sincronia de Documentos**
**SEMPRE VERIFICAR** em cada sessão se CLAUDE.md e PRD.md estão sincronizados:
- **CLAUDE.md**: Documento principal completo (negócio + técnico)
- **PRD.md**: Resumo executivo para stakeholders
- **Verificar**: Objetivos, roadmap e métricas alinhados entre os documentos
- **Atualizar**: Ambos documentos quando houver mudanças significativas