# AmFi - Sistema de Monitoramento de Portfólio

> **IMPORTANTE**: Sempre utilizar Claude Sonnet 4.0 para trabalhar neste projeto.

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
5. **Análise de Liquidez**: Cobertura de amortizações futuras

## Estrutura de Diretórios
```
/mnt/c/amfi/
├── docs/                    # Documentação do projeto
│   ├── processos/           # Checklists e processos operacionais
│   ├── sessions/            # APENAS to-dos por data (sem documentação técnica)
│   └── technical/           # Documentação técnica detalhada
├── tests/                   # Testes organizados
│   ├── unit/               # Testes unitários
│   ├── integration/        # Testes de integração
│   ├── performance/        # Testes de performance
│   └── fixtures/           # Dados de teste
├── scripts/                # Scripts utilitários e debug
├── monitor/                # Sistema de monitoramento
│   ├── base/               # Monitores padrão
│   ├── custom/             # Monitores específicos
│   └── utils/              # Utilitários compartilhados
├── udfs/                   # Código Python principal (UDFs Excel)
├── data/
│   ├── csv/                # Dados diários dos pools (PL, SR, JR)
│   ├── xlsx/               # Carteiras detalhadas (recebíveis)
│   ├── escrituras/         # JSONs de configuração dos pools
│   ├── escrituras_md/      # Escrituras originais em markdown
│   └── templates/          # Templates para criação de novos JSONs
└── Monitoramento.xlsm      # Interface Excel
```

## Estado Atual da Implementação

### ✅ Concluído
- Estrutura base de UDFs Excel
- Handlers para CSV/XLSX/JSON
- Sistema de cache
- Funções de cálculo financeiro (IS, JR)
- **7 pools auditados e padronizados** em JSON v2.2
- **JSON otimizado para monitoramento** (template v2.2 organizado em 5 seções)
- **Estrutura flexível de concentração** (top_N genérico)
- **Consolidação de limites** dispersos em `limites_monitoramento`
- **Mapeamento de eventos de monitoramento** organizados por categoria (7 base + customizados)
- **Auditoria sistemática completa**: 100% de dados verificados contra escrituras originais
- **Padronização de formatos**: Percentuais em decimal, cronogramas corrigidos
- **Template como fonte única de verdade**: Reorganizado em 5 seções lógicas

### 🔄 Em Desenvolvimento
- **Sistema de monitoramento modular** (5 arquivos por natureza)
- **Monitores customizados específicos** (20+ identificados)
- Dashboard de exceções
- Análise de fluxo de caixa
- Sistema de descoberta automática de pools (data_loader funcional)

### 📋 Mapeamento Real de Eventos de Monitoramento

#### **🏗️ Eventos Base (7 principais - Template v2.2)**
Padronizados e implementados em todos os pools via `monitoramentos_ativos`:

**1. SUBORDINAÇÃO (2 eventos base)**
- `subordinacao` - Índice mínimo de subordinação ✅ **IMPLEMENTADO**
- `subordinacao_critica` - Limite crítico de subordinação ✅ **IMPLEMENTADO**

**2. CONCENTRAÇÃO (2 eventos base)**
- `concentracao_sacados` - Concentração máxima por sacado individual
- `concentracao_cedentes` - Concentração máxima por cedente individual

**3. INADIMPLÊNCIA (2 eventos base)**
- `inadimplencia_30_dias` - Inadimplência 30+ dias (limite: 3-4%)
- `inadimplencia_90_dias` - Inadimplência 90+ dias (limite: 2%)

**4. ELEGIBILIDADE (1 evento base)**
- `elegibilidade_geral` - Critérios gerais de elegibilidade de ativos

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

#### **📊 Estatísticas Reais**
- **Eventos base padronizados**: 7 (template v2.2)
- **Eventos customizados identificados**: 20+ (JSONs legacy)
- **Total de combinações únicas**: 25+ eventos distintos
- **Pools com eventos customizados**: 100% (todos têm particularidades)
- Análise de liquidez vs amortizações
- Comparativo temporal automático
- Sistema de alertas
- Testes automatizados

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
    │   ├── ignore_pools.json          # Pools ignorados
    │   └── test_pools.json            # Cenários de teste
    ├── csv/                           # Dados gerais dos pools
    ├── xlsx/                          # Dados detalhadas das carteiras
    ├── escrituras/                    # Configurações específicas por pool
    │   └── legacy/                    # JSONs no formato antigo (arquivados)
    └── templates/                     # Templates para novos pools
        └── pool_monitoring_template.json
```

### Estado dos Arquivos Principais (Última Verificação: 2025-07-13)

#### **Estrutura de Dados Real (Variável Diariamente)**
- **CSV Dashboard**: ~45 registros de pools, colunas `nome/sr/jr/pl`
- **XLSX Portfolio**: ~79k registros de recebíveis, 36+ pools, coluna identificadora `pool`
- **Enriquecimento**: Processo temporário durante execução (+2 colunas calculadas)

#### **Arquivos Funcionais Confirmados**
| Arquivo | Status | Interface | Última Verificação |
|---------|--------|-----------|-------------------|
| **data_loader.py** | ✅ FUNCIONAL | `load_pool_data()` | 2025-07-13 (79k registros em 10s) |
| **orchestrator.py** | ✅ FUNCIONAL | `run_monitoring()` | 2025-07-13 (100% taxa sucesso) |
| **monitor_subordinacao.py** | ✅ FUNCIONAL | `run_subordination_monitoring()` | 2025-07-13 (integrado) |
| **monitor_inadimplencia.py** | ✅ FUNCIONAL | `run_delinquency_monitoring()` | 2025-07-13 (c/ enriquecimento) |

### Fluxo de Execução Integrado (Testado e Funcionando):

```
orchestrator.run_monitoring(pool_name=None)
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
            # Subordinação
            resultado_sub = orchestrate_subordination_monitoring(pool_name)
            
            # Concentração  
            resultado_conc = orchestrate_concentration_monitoring(pool_name)
            
            # Inadimplência
            resultado_inad = orchestrate_default_monitoring(pool_name)
            
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

#### **Status de Implementação:**

- ✅ **monitor_subordinacao.py**: 100% funcional e testado
- ✅ **Testes unitários**: 100% aprovados (4 testes por pool)
- ✅ **Documentação**: Interface e contratos definidos
- ✅ **Orquestrador**: 100% implementado e funcional
- ✅ **Estratégia de erros**: Definida e documentada
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
- [x] **Pasta data/config/**: Criada com ignore_pools.json e test_pools.json
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
- [x] **Monitor de inadimplência**: Funcionalmente completo, aguarda integração
- [x] **Arquitetura de enriquecimento**: Estratégia de dados progressivos definida
- [x] **Padrões de nomenclatura**: `_find_*_monitor()`, `_has_*_monitoring()`, `run_*_monitoring()`
- [x] **Integração data_loader + orchestrator**: Fluxo centralizado definido

### 🔄 Em Desenvolvimento
- [ ] **Classes de erro específicas**: Implementar enum de severidade e classes customizadas
- [ ] **Sistema de retry**: Backoff exponencial para erros temporários
- [ ] Sistema de descoberta automática de pools (`pool_discovery.py`)
- [ ] Engine de orquestração (`monitoring_engine.py`)
- [ ] Carregador de configurações (`config_loader.py`)
- [ ] Gerenciador de alertas (`alert_manager.py`)
- [ ] Implementação das funções nos utilitários
- [ ] Implementação das funções nos monitores base

### 📋 Próximos Passos
1. ✅ **Criar pasta data/config/** com ignore_pools.json e test_pools.json
2. ✅ **Implementar data_loader.py** com fluxo refinado de 9 etapas - COMPLETO
3. ✅ **Implementar monitor_subordinacao.py** - COMPLETO
4. ✅ **Implementar orquestrador de subordinação** - COMPLETO
5. ✅ **Definir arquitetura de enriquecimento progressivo** - COMPLETO
6. **Implementar orchestrator.run_monitoring()** - Nova função master integrada
7. **Integrar monitor_inadimplencia.py** com enriquecimento de DataFrame
8. **Implementar funções auxiliares** (`_has_*_monitoring()` para cada monitor)
9. **Implementar monitor_concentracao.py** (2 eventos base)
10. **Implementar monitor_elegibilidade.py** (1 evento base)
11. **Criar supersim_pool_1_recovery_rate.py** (🔧 Custom SuperSim)
12. **Criar afa_pool_1_sacados_especificos.py** (🔧 Custom AFA)
13. **Criar upvendas_pool_2_substituicao_pix.py** (🔧 Custom UpVendas)
14. **Sistema de PDD** (v2.0 - Provisão para Devedores Duvidosos)

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
- **Eventos base implementados**: 4/7 (subordinação + inadimplência prontos)
- **Eventos customizados identificados**: 20+ (específicos por pool)
- **Monitores base implementados**: 2/5 (subordinação ✅, inadimplência ✅ pronto)
- **Monitores customizados implementados**: 0/20+
- **Orquestradores implementados**: 1/1 (arquitetura integrada definida)
- **Estratégia de enriquecimento**: 100% definida (dias_atraso, grupo_de_risco)

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
- Última atualização: 2025-07-12
- Sessão atual: Definição de estratégia de tratamento de erros no orquestrador
- Próxima revisão: Implementação de classes de erro específicas e sistema de retry

### 📁 **Filosofia do docs/sessions/**

**PROPÓSITO EXCLUSIVO**: Lista de tarefas organizadas por data de sessão

**CONTEÚDO PERMITIDO**:
- ✅ To-dos priorizados com checkboxes [ ]
- ✅ Status de progresso (x/y tarefas concluídas)
- ✅ Próxima tarefa prioritária a executar
- ✅ Ordem de implementação recomendada

**CONTEÚDO ESTRITAMENTE PROIBIDO**:
- ❌ Descobertas técnicas → docs/SYSTEM_STATE.md
- ❌ Definições de arquitetura → docs/CLAUDE.md  
- ❌ Checklists e processos → docs/processos/
- ❌ Documentação detalhada → docs/technical/
- ❌ Métricas de performance → docs/SYSTEM_STATE.md
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