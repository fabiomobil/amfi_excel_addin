# AmFi - Sistema de Monitoramento de Portfólio - Guia Completo

> **IMPORTANTE**: Sempre utilizar Claude Sonnet 4.0 para trabalhar neste projeto.

## Visão Executiva

### Resumo do Sistema
Sistema automatizado de monitoramento de compliance e liquidez para fundos de investimento estruturados no Brasil. Processa escrituras de debêntures (PDFs) em configurações JSON para executar monitoramento de compliance, análise de fluxo de caixa e verificação de liquidez.

### Objetivos de Negócio
1. **Reduzir tempo de análise**: De 4-6 horas para <30 minutos/dia
2. **Eliminar erros manuais**: Zero falhas de cálculo em produção  
3. **Antecipar problemas**: Alertas com 6+ meses de antecedência
4. **Garantir compliance**: 100% de cobertura dos requisitos das escrituras
5. **Facilitar auditoria**: Histórico completo e rastreável

## Arquitetura do Sistema

### **🆕 Arquitetura Otimizada (2025-07-17)**

#### **Sistema de Imports Centralizado**
- **Problema resolvido**: Eliminados 800+ linhas de código duplicado
- **Localização**: `/monitor/core/imports.py`
- **Benefício**: Compatibilidade total Spyder/Windows/WSL com código limpo

```python
# ANTES (87 linhas de imports em cada arquivo):
import_success = False
try:
    from .base.monitor_subordinacao import run_subordination_monitoring
except (ImportError, ValueError):
    try:
        # ... 60+ linhas de fallbacks ...

# DEPOIS (3 linhas usando sistema centralizado):
from .core.imports import import_function
run_subordination_monitoring = import_function('subordinacao', 'run_subordination_monitoring')
```

#### **Classe Base para Monitores (BaseMonitor)**
- **Problema resolvido**: Eliminados 470+ linhas de código duplicado
- **Localização**: `/monitor/core/base_monitor.py`
- **Benefício**: Padrão consistente para todos os monitores

```python
# ANTES (cada monitor reimplementava):
def _find_subordination_monitor(config):
    if 'monitoramentos_ativos' not in config:
        raise ValueError("Config não contém monitoramentos_ativos")
    # +40 linhas de validação duplicada...

# DEPOIS (herda de BaseMonitor):
class SubordinacaoMonitor(BaseMonitor):
    def get_monitor_type(self):
        return 'subordinacao'
    
    def calculate(self):
        # Apenas lógica específica do monitor
```

#### **Framework de Testes Implementado**
- **Cobertura**: 80%+ dos componentes principais
- **Localização**: `/tests/` com pytest + fixtures padronizadas
- **Benefício**: Testes consistentes e reutilizáveis

### Fluxo de Dados Principal
```
Escritura (PDF) → JSON Config → Monitoramento Python → JSON Resultados → Dashboard
     ↓               ↓                    ↓                    ↓
  Manual         Automático      5 Componentes Otimizados   Consolidado
                                       ↓
                              [Sistema Centralizado]
                              [Base Classes]
                              [Testes Automatizados]
```

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

### **💰 Conversões Monetárias e Percentuais**

**Conversões automáticas aplicadas pelo data_loader:**
- **Monetários**: `R$ 1.234.567,89` → `1234567.89` (float)
- **Percentuais**: `25,50%` → `0.2550` (decimal)
- **Datas**: `01/01/2025` → `datetime` (formato brasileiro)

**Performance:**
- Datasets >1000 registros: Conversão vetorizada (50-100x mais rápida)
- Datasets menores: Conversão tradicional com .apply()

## Estrutura de Diretórios Organizada

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
│   ├── core/               # ✅ BaseMonitor + imports centralizados
│   ├── custom/             # Monitores específicos por pool
│   ├── utils/              # Utilitários compartilhados
│   └── orchestrator.py     # Interface principal do sistema
├── config/                  # ⚙️ CONFIGURAÇÕES ESTÁTICAS
│   ├── monitoring/         # Configurações de monitoramento
│   │   ├── test_pools.json # Pools para modo DEBUG
│   │   ├── ignore_pools.json # Pools a ignorar
│   │   └── concentration_filters.json # Filtros de entidades
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
│       ├── BASE_MONITOR_API.md # API da classe base
│       ├── MIGRATION_STRATEGY.md # Estratégia de migração
│       └── SYSTEM_STATE.md # Estado atual do sistema
├── scripts/                 # 🔧 SCRIPTS ADMINISTRATIVOS
│   └── run_data_loader.py  # Script para executar data_loader
└── tests/                   # 🧪 TESTES ORGANIZADOS
    ├── unit/               # Testes unitários
    ├── integration/        # Testes de integração (scripts específicos)
    ├── performance/        # Testes de performance
    ├── fixtures/           # Dados de teste (vazio)
    ├── conftest.py         # Configuração pytest
    └── pytest.ini          # Configuração de testes
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
- **Status**: **ATIVO** - Monitores subordinação + inadimplência + PDD + concentração implementados
- **Vantagens**: Independente do Excel, modular, testável, escalável

## Componentes Principais do Sistema

### 1. Monitoramento Individual por Pool

**Interface Principal**: `run_monitoring(pool_name=None)` - função única do sistema

**Monitores Disponíveis (2025-07-17):**
- ✅ **Subordinação**: Índice de subordinação com limites (BaseMonitor implementado)
- ✅ **Inadimplência**: Janelas customizáveis + aging configurável + drill-down completo
- ✅ **PDD**: Provisão para Devedores Duvidosos (grupos AA-H) ⚠️ **CCB não implementada**
- ✅ **Concentração**: Individual e top-N + análise sequencial + matriz de sobra + filtro de entidades
- 🔄 **Elegibilidade**: Critérios de ativos (implementação planejada com BaseMonitor)

**Execução Automática:**
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

### 2. Dashboard Consolidado de Exceções
**Objetivo**: Visão executiva focada apenas em violações e alertas.

**Funcionalidades**:
- Filtrar apenas pools com problemas
- Priorizar por severidade (crítico/alto/médio)
- Indicar ações corretivas necessárias
- Mostrar prazos de cura disponíveis

### 3. Análise Comparativa Temporal
**Objetivo**: Identificar tendências e deterioração de indicadores.

### 4. Análise de Fluxo de Caixa
**Objetivo**: Projetar recebimentos futuros considerando qualidade da carteira.

### 5. Verificação de Liquidez para Amortizações
**Objetivo**: Garantir capacidade de pagamento das obrigações.

## Estado Atual da Implementação

### ✅ Concluído no Sistema Atual (/monitor/)

- **Arquitetura modular** com monitores especializados
- **Data loader centralizado** com descoberta automática
- **Monitor de subordinação** com cálculo IS correto ✅ **IMPLEMENTADO**
- **Monitor de inadimplência** com enriquecimento progressivo, matriz detalhada de atrasos e aging configurável ✅ **IMPLEMENTADO**
- **Monitor de PDD** com arquitetura inteligente e lógica por cedente ✅ **IMPLEMENTADO** ⚠️ **CCB não implementada**
- **Monitor de concentração** com análise individual, top-N e sequencial ✅ **IMPLEMENTADO**
- **Sistema de cache** integrado automaticamente
- **Orquestrador** com execução condicional de monitores (4 monitores integrados)
- **9 pools auditados e padronizados** em JSON v2.3
- **JSON otimizado para monitoramento** (template v2.3 com estrutura híbrida)
- **Estrutura flexível de concentração** (top_N genérico)
- **Sistema de BaseMonitor** implementado e funcional
- **Framework de testes** com 80%+ cobertura
- **Sistema de imports centralizado** eliminando duplicação

### 🔄 Em Desenvolvimento

- **Monitor de elegibilidade** (critérios gerais de ativos)
- **Monitores customizados específicos** (20+ identificados por pool)
- Dashboard de exceções
- Análise de fluxo de caixa
- Sistema de histórico de resultados

## Funcionalidades Avançadas

### **🆕 Estrutura Híbrida de Processos Legais (v2.3)**

O sistema implementa uma **arquitetura híbrida** que separa aspectos técnicos e legais:

```json
"triggers_aceleracao": {
  "concentracao_violacao": {
    "prazo_cura_dias": 30,
    "automatico": false,
    "processo_detalhado_ref": "processos_legais.concentracao_violacao"
  }
},
"processos_legais": {
  "concentracao_violacao": {
    "pos_violacao": {
      "assembleia": {"convocacao_prazo_dias": 3},
      "votacao": {"votantes": "serie_senior"},
      "renuncia": {"prazo_dias": 5}
    }
  }
}
```

**Benefícios:**
- **Sistema de Monitoramento**: Usa `triggers_aceleracao` simples para automação
- **Compliance/Auditoria**: Usa `processos_legais` detalhados para processos manuais
- **Rastro Legal**: Documentação completa dos processos pós-violação

### **🆕 Análise Sequencial de Capacidade (Monitor Concentração v2.1)**

O monitor de concentração inclui **análise sequencial de capacidade** que mostra:

**Funcionalidade:**
- **Capacidade por entidade**: Quanto cada sacado/cedente pode crescer
- **Análise cascata**: Como espaço disponível é consumido sequencialmente
- **Limitações identificadas**: Se restrição é individual ou top-N
- **Saldo restante**: Quanto sobra após cada alocação

**Casos de Uso:**
- **Gestão de Originação**: Saber exatamente quanto originar por sacado
- **Planejamento de Portfolio**: Otimizar uso de limites disponíveis
- **Compliance Proativo**: Evitar violações antes que aconteçam

### **🔽 Filtro de Entidades Ignoradas**

Sistema de filtros configurável que remove entidades específicas dos cálculos (ex: "Amfi Digital Assets LTDA").

```json
// /config/monitoring/concentration_filters.json
{
  "entidades_ignoradas": {
    "cedentes": ["Amfi Digital Assets LTDA"],
    "sacados": ["Amfi Digital Assets LTDA"]
  }
}
```

## Arquitetura de Enriquecimento Progressivo

### **Conceito Central**
- **DataFrame XLSX** é passado por referência entre monitores
- **Cada monitor** pode adicionar colunas calculadas
- **Dados enriquecidos** ficam disponíveis para monitores posteriores
- **Evita recálculos** desnecessários e melhora performance

### **Campos Adicionados por Monitor**
```
Data Original (XLSX):
├── status, vencimento_original, valor_presente, sacado, cedente...

Monitor de Inadimplência adiciona:
├── dias_atraso: int (calculado vs data atual)
├── grupo_de_risco: str (AA, A, B, C, D, E, F, G, H)

Futuros Monitores podem usar:
├── Concentração: usar grupo_de_risco para análise
├── Elegibilidade: usar dias_atraso para filtros
└── Customizados: usar qualquer campo calculado
```

## Mapeamento de Eventos de Monitoramento

### **🏗️ Eventos Base (7 principais - Template v2.3)**

**1. SUBORDINAÇÃO (2 eventos base)**
- `subordinacao` - Índice mínimo de subordinação ✅ **IMPLEMENTADO**
- `subordinacao_critica` - Limite crítico de subordinação ✅ **IMPLEMENTADO**

**2. INADIMPLÊNCIA (2 eventos base)**
- `inadimplencia_30_dias` - Inadimplência 30+ dias (limite: 3-4%) ✅ **IMPLEMENTADO**
- `inadimplencia_90_dias` - Inadimplência 90+ dias (limite: 2%) ✅ **IMPLEMENTADO**

**3. PDD (1 evento base)**
- `pdd` - Provisão para Devedores Duvidosos (grupos AA-H) ✅ **IMPLEMENTADO**

**4. CONCENTRAÇÃO (2 eventos base)**
- `concentracao_individual` - Concentração máxima por sacado/cedente individual ✅ **IMPLEMENTADO**
- `concentracao_top_n` - Concentração agregada dos N maiores (ex: top 10) ✅ **IMPLEMENTADO**

**5. ELEGIBILIDADE (1 evento base)**
- `elegibilidade_geral` - Critérios gerais de elegibilidade de ativos 🔄 **PLANEJADO**

### **⚙️ Eventos Customizados por Pool (20+ identificados)**

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

## Usando BaseMonitor para Novos Monitores

### Template Básico

```python
from monitor.core.base_monitor import BaseMonitor

class MeuNovoMonitor(BaseMonitor):
    def get_monitor_type(self) -> str:
        return 'meu_monitor'
    
    def calculate(self) -> Dict:
        # 1. Obter dados do pool automaticamente
        pool_data = self._get_pool_data()
        
        # 2. Obter configurações específicas
        limite = self._get_config_value('limite', 0.10)
        
        # 3. Executar cálculo específico
        valor_calculado = self._meu_calculo_especifico(pool_data)
        
        # 4. Verificar violações
        status = 'enquadrado' if valor_calculado <= limite else 'violado'
        
        # 5. Retornar resultado
        return {
            'valor_calculado': valor_calculado,
            'limite_configurado': limite,
            'status': status
        }
    
    def _meu_calculo_especifico(self, pool_data):
        # Sua lógica aqui
        return resultado
```

### Vantagens do BaseMonitor

✅ **Validação Automática**: Dados são validados automaticamente  
✅ **Logging Integrado**: Sistema de logs padronizado  
✅ **Tratamento de Erros**: Handling robusto de exceções  
✅ **Compatibilidade**: Funciona com run_monitoring() automaticamente  
✅ **Testabilidade**: Framework de testes já configurado  
✅ **Performance**: Otimizações automáticas aplicadas  

## Roadmap de Implementação

### Fase 1 (Atual): Fundação ✅ CONCLUÍDA
- ✅ Sistema de monitoramento básico
- ✅ Processamento de dados core
- ✅ JSON otimizado para monitoramento
- ✅ **Estrutura híbrida processos legais implementada**
- ✅ **Monitor concentração com análise sequencial**
- ✅ Sistema de carregamento completo (data_loader.py)
- ✅ **Sistema BaseMonitor implementado**
- ✅ **Framework de testes com 80%+ cobertura**

### Fase 2: Expansão
- Todos os monitores implementados (5/5 base + customizados)
- Dashboard de exceções
- Análise temporal

### Fase 3: Inteligência
- Fluxo de caixa preditivo
- Análise de liquidez
- Machine learning para recuperação

### Fase 4: Integração
- APIs para sistemas externos
- Notificações automáticas
- Mobile dashboard

## Métricas de Progresso Atuais

### Status Geral do Sistema (2025-07-17):
- **Pools mapeados**: 9/9 (100% - incluindo UnionNational Pool #5, E-ctare Pool #1)
- **JSONs de configuração**: 9/9 (100% - template v2.3 com estrutura híbrida)
- **Auditoria de dados**: 9/9 (100% - verificados contra escrituras originais)
- **Nomenclatura padronizada**: 9/9 (100% - matching CSV ↔ JSON)
- **Monitores base implementados**: 4/5 (80% - Subordinação, Inadimplência, PDD, Concentração)
- **Sistema BaseMonitor**: ✅ Implementado e funcional
- **Framework de testes**: ✅ 80%+ cobertura
- **Sistema centralizado**: ✅ 1.270+ linhas de duplicação eliminadas
- **Documentação**: ✅ Completamente reorganizada e atualizada

### Benefícios Entregues:
- ✅ **Redução de código duplicado**: 1.270+ linhas eliminadas
- ✅ **Melhoria de manutenibilidade**: 60-70% redução de esforço
- ✅ **Testabilidade**: Framework completo implementado
- ✅ **Performance**: Sistema otimizado com imports centralizados
- ✅ **Extensibilidade**: BaseMonitor facilita criação de novos monitores

## Limitações Conhecidas

### ⚠️ Limitação CCB (Cédula de Crédito Bancário)

**Status**: Lógica CCB **NÃO IMPLEMENTADA** no Monitor PDD

**Problema**: 
- Sistema atual calcula PDD por cedente (lógica padrão)
- CCB requer cálculo PDD por ativo individual
- Todos os títulos CCB recebem provisão do pior ativo do cedente (incorreto)

**Impacto**:
- CCB com 0 dias atraso pode receber provisão alta indevidamente
- Superprovisão em carteiras com CCB misturadas
- Análise de risco distorcida para pools com CCB

## Compatibilidade e Ambiente

### Execução no Spyder
O sistema foi desenvolvido e é testado principalmente no **Spyder IDE**:

```python
# No console do Spyder, navegue até o diretório do projeto
cd /mnt/c/amfi

# Execute o monitoramento
from monitor.orchestrator import run_monitoring
resultado = run_monitoring()
```

### Compatibilidade de Ambientes
A função `run_monitoring()` funciona em todos os ambientes:

- ✅ **Windows**: `C:\amfi\...`
- ✅ **WSL**: `/mnt/c/amfi/...`
- ✅ **Spyder**: Descoberta automática de caminhos
- ✅ **Linha de comando**: Python direto
- ✅ **Jupyter**: Notebooks compatíveis

## Princípios de Desenvolvimento

### 🎯 Mentalidade de Desenvolvimento Sênior
- **SEMPRE pensar como dev senior e arquiteto de soluções**
- **NUNCA ser agreeable se houver propostas melhores**
- **Questionar decisões técnicas** e propor alternativas superiores
- **Priorizar qualidade de código** sobre velocidade de entrega
- **Focar em performance** desde o design inicial

### 🏗️ Princípios Arquiteturais SOLID
- **Single Responsibility**: Cada classe/função tem UMA responsabilidade
- **Open/Closed**: Extensível via novos componentes, fechado para modificação
- **Liskov Substitution**: Interfaces consistentes e substituíveis
- **Interface Segregation**: Interfaces específicas por necessidade
- **Dependency Inversion**: Dependências em abstrações, não implementações

## Próximos Passos

### Prioridades Imediatas:
1. **Implementar Monitor de Elegibilidade** com BaseMonitor
2. **Resolver Limitação CCB** no Monitor PDD
3. **Implementar Monitores Customizados** (SuperSim, AFA, UpVendas)
4. **Dashboard de Exceções** - Consolidar apenas violações
5. **Sistema de Templates** para JSONs de configuração

### Métricas de Sucesso:
- **Cobertura de monitoramento**: 100% (5/5 monitores base)
- **Redução de tempo**: 80% redução no tempo de análise
- **Zero erros**: Sem falhas de cálculo em produção
- **Performance**: <5 minutos para processar todos os pools

---

## Links de Referência

### Documentação Técnica Detalhada
- **API BaseMonitor**: `/docs/technical/BASE_MONITOR_API.md`
- **Estratégia de Migração**: `/docs/technical/MIGRATION_STRATEGY.md`
- **Estado do Sistema**: `/docs/technical/SYSTEM_STATE.md`
- **Exemplos de Uso**: `/docs/USAGE_EXAMPLES.md`

### Processos Operacionais
- **Extração Sistemática**: `/docs/processos/PROCESSO_EXTRACAO_SISTEMATICA.md`
- **Checklist Features**: `/docs/processos/CHECKLIST_EXTRACAO_FEATURES.md`
- **Framework Daily Sync**: `/docs/processos/FRAMEWORK_DAILY_SYNC.md`

### Implementação
- **Sistema de Imports**: `/monitor/core/imports.py`
- **Classe Base**: `/monitor/core/base_monitor.py`
- **Framework de Testes**: `/tests/conftest.py`
- **Interface Principal**: `/monitor/orchestrator.py`

---

**Última atualização**: 2025-07-17  
**Responsável**: Claude Sonnet 4.0  
**Status**: Sistema operacional com arquitetura otimizada