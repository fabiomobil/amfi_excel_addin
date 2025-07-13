# Sistema de Monitoramento AmFi

Arquitetura modular de monitoramento de compliance para fundos de investimento estruturados.

## 🏗️ Arquitetura do Sistema

### Estrutura Hierárquica
```
/monitor/
├── base/                    # Monitores padrão (80% comum)
│   ├── monitor_subordinacao.py      ✅ IMPLEMENTADO
│   ├── monitor_concentracao.py      📋 Planejado
│   ├── monitor_inadimplencia.py     📋 Planejado (inclui PDD)
│   ├── monitor_elegibilidade.py     📋 Planejado
│   └── monitor_operacional.py       📋 Planejado
├── custom/                  # Monitores específicos (20% customizado)
│   ├── supersim_pool_1_recovery_rate.py    🔧 Custom
│   ├── afa_pool_1_sacados_especificos.py  🔧 Custom
│   └── upvendas_pool_2_substituicao_pix.py 🔧 Custom
├── utils/                   # Utilitários compartilhados
│   ├── data_loader.py       ✅ COMPLETO - Orquestrador principal
│   ├── file_loaders.py      ✅ COMPLETO - Carregamento CSV/XLSX
│   ├── data_handler.py      ✅ COMPLETO - Validações e metadados
│   ├── alerts.py            ✅ COMPLETO - Sistema de alertas
│   └── file_discovery.py    ✅ COMPLETO - Descoberta de arquivos
├── pool_discovery.py        📋 Planejado - Descoberta automática de pools
├── monitoring_engine.py     📋 Planejado - Orquestração geral
├── config_loader.py         📋 Planejado - Carregamento dinâmico
└── alert_manager.py         📋 Planejado - Gestão de alertas
```

## 🔍 Sistema de Descoberta Automática

### Como Funciona o Matching JSON → Código

O sistema lê os JSONs em `/data/escrituras/` e faz descoberta automática dos monitores baseado em **convenções de nomenclatura**:

#### 1. Monitores Base (Padrão)
**JSON**: `monitoramentos_ativos` → `tipo`
**Código**: `monitor/base/monitor_{tipo}.py`

**Exemplos**:
```json
{"tipo": "subordinacao"} → monitor/base/monitor_subordinacao.py
{"tipo": "concentracao"} → monitor/base/monitor_concentracao.py  
{"tipo": "inadimplencia"} → monitor/base/monitor_inadimplencia.py (inclui PDD)
{"tipo": "provisao"} → monitor/base/monitor_inadimplencia.py (consolidado)
{"tipo": "elegibilidade"} → monitor/base/monitor_elegibilidade.py
```

#### 2. Monitores Customizados (Específicos)
**JSON**: `monitores_customizados` → `arquivos_necessarios`
**Código**: `monitor/custom/{arquivo}.py`

**Exemplos**:
```json
"arquivos_necessarios": [
  "SuperSim Pool #1_recovery_rate.py"
] → monitor/custom/supersim_pool_1_recovery_rate.py

"arquivos_necessarios": [
  "AFA Pool #1_sacados_especificos.py"  
] → monitor/custom/afa_pool_1_sacados_especificos.py
```

### 3. Função de Cálculo
**JSON**: `funcao_calculo`
**Código**: Nome da função dentro do arquivo Python

**Exemplo**:
```json
{
  "tipo": "subordinacao",
  "funcao_calculo": "calc_subordinacao"
}
```
→ Chama `calc_subordinacao()` em `monitor_subordinacao.py`

## 🔧 Interface Padrão dos Monitores

### Monitores Base
Todos seguem a mesma interface:

```python
def run_{tipo}_monitoring(df: pd.DataFrame, config: dict) -> dict:
    """
    Interface principal para orquestrador
    
    Args:
        df: DataFrame com dados do pool
        config: JSON de configuração do pool
        
    Returns:
        dict: Resultado padronizado com sucesso/erro
    """
    
def validate_data(df: pd.DataFrame, config: dict) -> bool:
    """Validação de entrada"""
    
def calculate_{tipo}(df: pd.DataFrame, config: dict) -> float:
    """Cálculo principal do monitor"""
    
def generate_result(valor: float, limites: dict) -> dict:
    """Geração do resultado padronizado"""
```

### Monitores Customizados
Interface flexível conforme necessidade específica do pool.

## 📊 Status de Implementação

### ✅ Completado
- **monitor_subordinacao.py**: 100% implementado e testado
- **Sistema de utilitários**: 5/5 arquivos funcionais
- **data_loader.py**: Orquestrador principal completo
- **Interface padrão**: Definida e documentada

### 🔄 Em Desenvolvimento  
- **Classes de erro específicas**: Enum de severidade + retry automático
- **Sistema de tratamento de erros**: Categorização CRÍTICO/ALTO/BAIXO

### 📋 Próximos Monitores
1. **monitor_concentracao.py** - Concentração individual e top N
2. **monitor_inadimplencia.py** - Inadimplência + PDD por grupos de risco
3. **monitor_elegibilidade.py** - Critérios de elegibilidade
4. **monitor_operacional.py** - Reservas e triggers

### 🔧 Monitores Customizados Identificados (20+)
- **SuperSim**: Recovery rate mensal (95%)
- **AFA**: Sacados específicos (BMP, SOCINAL)
- **UpVendas**: Substituição PIX→URs, despesas extras
- **Credmei**: Recompra obrigatória
- **Formento**: Vencimentos específicos
- **LeCapital**: (sem customizações - 100% padrão)
- **a55**: Limites diferenciados

## 🚀 Fluxo de Execução

### 1. Descoberta Automática
```python
# data_loader.py descobre pools ativos
pools = descobrir_pools_em_csv_xlsx()

# Para cada pool, carrega JSON correspondente
for pool in pools:
    config = carregar_json_pool(pool)
    monitores = extrair_monitores_ativos(config)
```

### 2. Execução de Monitores
```python
# Para cada monitor ativo no JSON
for monitor in config['monitoramentos_ativos']:
    if monitor['ativo']:
        # Descoberta automática do arquivo
        arquivo = f"monitor_{monitor['tipo']}.py"
        funcao = monitor['funcao_calculo']
        
        # Execução
        resultado = executar_monitor(arquivo, funcao, dados, config)
```

### 3. Consolidação de Resultados
```python
# Consolida todos os resultados do pool
relatorio_pool = {
    "pool_id": pool_name,
    "data": hoje,
    "monitores": resultados_individuais,
    "resumo": estatisticas_gerais
}
```

## 🎯 Convenções de Desenvolvimento

### Nomenclatura de Arquivos
- **Base**: `monitor_{tipo}.py` (ex: `monitor_subordinacao.py`)
- **Custom**: `{pool_id}_{funcionalidade}.py` (ex: `supersim_pool_1_recovery_rate.py`)

### Nomenclatura de Funções
- **Principal**: `run_{tipo}_monitoring()` (interface do orquestrador)
- **Cálculo**: `calc_{tipo}()` ou `calculate_{tipo}()` 
- **Validação**: `validate_data()`
- **Resultado**: `generate_result()`

### Tratamento de Erros
```python
# Retorno padrão de sucesso
{"sucesso": true, "monitor": "subordinacao", "resultado": {...}}

# Retorno padrão de erro  
{"sucesso": false, "monitor": "subordinacao", "erro": "Descrição"}
```

## 🔗 Integração com Orquestrador

### Orquestrador Principal (Futuro)
`monitoring_engine.py` será responsável por:
- Descobrir pools ativos automaticamente
- Carregar configurações JSON correspondentes
- Executar monitores base + customizados em paralelo
- Consolidar resultados e gerar relatórios
- Gerenciar alertas e notificações

### Sistema de Alertas
`alert_manager.py` processará resultados e gerará:
- Alertas por severidade (CRÍTICO/ALTO/MÉDIO/BAIXO)
- Notificações automáticas
- Histórico de eventos
- Dashboard de exceções

---
**Última atualização**: 2025-07-12 | **Status**: 1/6 monitores base implementados