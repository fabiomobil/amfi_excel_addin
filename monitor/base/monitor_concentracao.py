"""
Monitor de Concentração - Base
==============================

Monitor base para concentração de ativos por sacado e cedente.
Implementa apenas funcionalidades essenciais do sistema de monitoramento AmFi.

## 🎯 FUNCIONALIDADES SUPORTADAS

### 1. Concentração Individual
Monitora concentração por entidade específica (sacado ou cedente):
- Identifica maior concentração individual
- Calcula percentual vs. patrimônio líquido do pool
- Valida contra limites configurados na escritura

### 2. Concentração Top-N
Monitora concentração agregada dos N maiores (ex: top 10):
- Soma dos N maiores sacados/cedentes
- Calcula percentual agregado vs. PL do pool
- Valida contra limites configurados na escritura

### 3. 🆕 Análise Sequencial de Capacidade
Calcula capacidade incremental considerando ordem de prioridade:
- Mostra quanto cada sacado/cedente pode crescer individualmente
- Considera limitações de teto individual E top-N simultaneamente
- Análise cascata: mostra saldo restante após cada alocação
- Identifica qual restrição é mais limitante por posição

### 4. 🆕 Matriz de Sobra Tabular
Visualização clara da capacidade disponível em formato tabela:
- Tabela ASCII formatada para fácil visualização
- Mostra capacidade individual vs efetiva por entidade
- Indica saldo restante após cada alocação sequencial
- Identifica limitações (individual vs top-N) por posição

## 🏗️ ARQUITETURA SIMPLIFICADA

**Design Pattern**: Tudo consolidado em um único arquivo para simplicidade
**Funcionalidades customizadas**: Grupo econômico, CNPJ 8 dígitos → /monitor/custom/
**Compatibilidade**: Mantém interface compatível com código existente

## 📋 CONFIGURAÇÃO JSON

```json
{
  "id": "concentracao",
  "tipo": "concentracao",
  "ativo": true,
  "frequencia": "diaria",
  "prioridade": "alta",
  "limites": [
    {
      "tipo": "individual",
      "entidade": "sacado",
      "limite": 0.35
    },
    {
      "tipo": "top_n",
      "entidade": "cedente",
      "n": 10,
      "limite": 0.70
    }
  ],
  "campos_necessarios": ["sacado", "cedente", "valor_presente"],
  "funcao_calculo": "calc_concentracao"
}
```

## 🔧 INTERFACE PRINCIPAL

```python
# Uso típico
resultado = run_concentration_monitoring(
    pool_data_csv=pool_csv,      # DataFrame com PL do pool
    carteira_xlsx=carteira_df,   # DataFrame com carteira detalhada
    config=pool_config           # Configuração JSON do pool
)

# Estrutura de retorno
{
    "sucesso": True,
    "pool_id": "AFA Pool #1",
    "pl_pool": 8500000.0,
    "status_geral": "enquadrado",
    "configuracao": {
        "ativo": True,
        "numero_limites": 4,
        "complexidade": "alta"
    },
    "resumo": {
        "total_limites_analisados": 4,
        "limites_enquadrados": 4,
        "limites_violados": 0
    },
    "resultados_por_limite": [
        {
            "limite_id": "limite_1",
            "tipo": "individual",
            "entidade": "sacado",
            "limite_configurado": 27.0,
            "status": "enquadrado",
            "maior_concentracao": {
                "entidade": "Empresa ABC",
                "valor_absoluto": 1200000.0,
                "percentual_pl": 14.1,
                "quantidade_titulos": 45
            },
            "margem_limite": 12.9,
            "total_entidades": 28
        }
    ],
    "analises_capacidade": {
        "sacado": {
            "tipo_analise": "sequencial",
            "entidade_tipo": "sacado",
            "resumo": {
                "pl_pool": 8500000.0,
                "limite_individual_pct": 27.0,
                "limite_top_n_pct": 100.0,
                "top_n_size": 10,
                "exposicao_top_n_atual": 85.0,
                "espaco_total_disponivel": 15.0
            },
            "analise_sequencial": [
                {
                    "posicao": 1,
                    "entidade": "Empresa ABC",
                    "exposicao_atual": 1200000.0,
                    "percentual_atual": 14.1,
                    "capacidade_individual": 1095000.0,
                    "capacidade_efetiva": 1095000.0,
                    "saldo_antes": 1275000.0,
                    "saldo_apos": 180000.0,
                    "limitada_por": "individual",
                    "explicacao": "Limitado por teto individual. Restaria 180000.0 no Top-N"
                }
            ]
        },
        "matriz_sobra_tabular": {
            "tabela_ascii": "
MATRIZ DE SOBRA - ANÁLISE SEQUENCIAL
PL: 8,500,000 | Individual: 27.0% | Top-10: 100.0%
Espaço disponível: 1,275,000

┌──────────────┬────────┬──────────┬─────────────┬─────────────┬───────────────┐
│Entidade      │Atual   │Cap.Indiv │Cap.Efetiva  │Saldo Antes  │Limitado Por   │
├──────────────┼────────┼──────────┼─────────────┼─────────────┼───────────────┤
│Empresa ABC   │1200000 │+1095000  │+1095000     │1275000      │individual     │
│Empresa XYZ   │800000  │+1495000  │+180000      │180000       │top_n          │
│Empresa DEF   │600000  │+1695000  │+0           │0            │esgotado       │
└──────────────┴────────┴──────────┴─────────────┴─────────────┴───────────────┘
            ",
            "resumo": {
                "total_crescimento_possivel": 1275000.0,
                "entidades_com_capacidade": 2,
                "utilizacao_espaco_disponivel": 100.0
            }
        }
    }
}
```

## 📊 DADOS NECESSÁRIOS

### CSV do Pool (pool_data_csv)
```
pool,pl,sr,jr
AFA Pool #1,8500000,6000000,2500000
```

### XLSX da Carteira (carteira_xlsx)
```
pool,nome_do_sacado,nome_do_cedente,valor_presente
AFA Pool #1,Empresa A,Cedente 1,150000
AFA Pool #1,Empresa B,Cedente 2,280000
```

## 🎨 EXEMPLOS DE USO

### Exemplo 1: Pool com Concentração Individual
```python
import pandas as pd
from monitor_concentracao import run_concentration_monitoring

# Dados do pool
pool_csv = pd.DataFrame({
    'pool': ['LeCapital Pool #1'],
    'pl': [15000000]
})

# Carteira
carteira_df = pd.DataFrame({
    'pool': ['LeCapital Pool #1'] * 3,
    'nome_do_sacado': ['Empresa A', 'Empresa B', 'Empresa C'],
    'nome_do_cedente': ['Cedente 1', 'Cedente 1', 'Cedente 2'],
    'valor_presente': [500000, 300000, 200000]
})

# Configuração
config = {
    "pool_id": "LeCapital Pool #1",
    "monitoramentos_ativos": [
        {
            "tipo": "concentracao",
            "ativo": True,
            "limites": [
                {
                    "tipo": "individual",
                    "entidade": "sacado",
                    "limite": 0.35
                }
            ]
        }
    ]
}

# Executar
resultado = run_concentration_monitoring(pool_csv, carteira_df, config)
print(f"Status: {resultado['status_geral']}")
# Output: "Status: enquadrado"
```

### Exemplo 2: Pool com Top-N
```python
# Configuração Top-10
config = {
    "pool_id": "AFA Pool #1",
    "monitoramentos_ativos": [
        {
            "tipo": "concentracao",
            "ativo": True,
            "limites": [
                {
                    "tipo": "top_n",
                    "entidade": "sacado",
                    "n": 10,
                    "limite": 1.00
                }
            ]
        }
    ]
}

resultado = run_concentration_monitoring(pool_csv, carteira_df, config)
top_10_result = resultado['resultados_por_limite'][0]
print(f"Top-10 sacados: {top_10_result['concentracao_top_n']['percentual_pl']:.1f}%")
```

### Exemplo 3: Análise Sequencial de Capacidade
```python
# Configuração com Individual + Top-N
config = {
    "pool_id": "Union Pool #5",
    "monitoramentos_ativos": [
        {
            "tipo": "concentracao",
            "ativo": True,
            "limites": [
                {
                    "tipo": "individual",
                    "entidade": "sacado",
                    "limite": 0.25  # 25% individual
                },
                {
                    "tipo": "top_n",
                    "entidade": "sacado", 
                    "n": 3,
                    "limite": 0.50  # 50% top-3
                }
            ]
        }
    ]
}

resultado = run_concentration_monitoring(pool_csv, carteira_df, config)

# Acessar análise sequencial
if "analises_capacidade" in resultado:
    analise_sacado = resultado["analises_capacidade"]["sacado"]
    print(f"Espaço disponível: {analise_sacado['resumo']['espaco_total_disponivel']:.1f}")
    
    for item in analise_sacado["analise_sequencial"]:
        print(f"Posição {item['posicao']}: {item['entidade']} - "
              f"Pode crescer {item['capacidade_efetiva']:.1f}, "
              f"sobram {item['saldo_apos']:.1f}")

# Acessar matriz de sobra tabular
if "matriz_sobra_tabular" in analise_sacado:
    print(analise_sacado["matriz_sobra_tabular"]["tabela_ascii"])
    
    resumo_matriz = analise_sacado["matriz_sobra_tabular"]["resumo"]
    print(f"📊 RESUMO DA MATRIZ:")
    print(f"   Total crescimento possível: {resumo_matriz['total_crescimento_possivel']:,.0f}")
    print(f"   Entidades com capacidade: {resumo_matriz['entidades_com_capacidade']}")
    print(f"   Utilização do espaço: {resumo_matriz['utilizacao_espaco_disponivel']:.1f}%")
```

## ⚠️ TRATAMENTO DE ERROS

### Erros Comuns
- **Pool não encontrado**: Carteira vazia para o pool
- **Coluna ausente**: nome_do_sacado/nome_do_cedente não existe
- **PL inválido**: Patrimônio líquido <= 0
- **Configuração inválida**: Limite fora do range 0-1

### Códigos de Status
- `"enquadrado"`: Todos os limites respeitados
- `"violado"`: Pelo menos um limite violado
- `"sem_limites"`: Sem limites configurados
- `"erro"`: Erro na execução

## 🔗 INTEGRAÇÃO COM ORQUESTRADOR

Este monitor é executado automaticamente pelo orquestrador quando:
1. Pool tem `"tipo": "concentracao"` ativo na configuração
2. Dados CSV e XLSX estão disponíveis
3. Campos necessários existem na carteira

## 📈 PERFORMANCE

- **Otimizado para datasets grandes**: Usa pandas.groupby() eficiente
- **Memória controlada**: Processa apenas dados do pool específico
- **Cálculos simples**: Agregações diretas sem algoritmos complexos

## 🧪 TESTES

Execute testes automatizados:
```bash
python3 test_monitor_concentracao.py
python3 test_orchestrator_concentration.py
```

## 🎯 EXTENSIBILIDADE

Para funcionalidades customizadas:
1. Criar arquivo em `/monitor/custom/`
2. Implementar lógica específica do pool
3. Registrar em `monitores_customizados` no JSON

Exemplo: Grupo econômico, CNPJ 8 dígitos, listas específicas.

---

**Versão**: 2.2 (Simplificada + Análise Sequencial + Matriz de Sobra)  
**Data**: 2025-07-15  
**Autor**: Claude (Building Block 6 - Consolidado + Capacidade Sequencial + Matriz Tabular)  
**Compatibilidade**: Python 3.8+, pandas 1.3+  
**Funcionalidades**: Individual, Top-N, Análise Sequencial, Matriz de Sobra Tabular
"""

import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from pathlib import Path
import os
import json


class ConcentrationType(Enum):
    """Tipos de concentração suportados pelo monitor base."""
    INDIVIDUAL = "individual"
    TOP_N = "top_n"


class ConcentrationEntity(Enum):
    """Entidades monitoradas para concentração."""
    SACADO = "sacado"
    CEDENTE = "cedente"


@dataclass
class ConcentrationLimit:
    """Estrutura para um limite de concentração."""
    tipo: ConcentrationType
    entidade: ConcentrationEntity
    limite: float
    n: Optional[int] = None  # Para top_n
    
    def __post_init__(self):
        """Validações pós-inicialização."""
        if self.tipo == ConcentrationType.TOP_N and self.n is None:
            raise ValueError("Top-N concentration requires 'n' parameter")
        
        if self.limite < 0 or self.limite > 1:
            raise ValueError(f"Limite deve estar entre 0 e 1, recebido: {self.limite}")


def _load_concentration_filters() -> Dict[str, Any]:
    """
    Carrega configuração de filtros para concentração.
    
    Returns:
        Dict com configuração de entidades ignoradas
    """
    try:
        # Caminho para configuração de filtros
        filters_path = Path(__file__).parent.parent.parent / "config" / "monitoring" / "concentration_filters.json"
        
        if filters_path.exists():
            with open(filters_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Configuração padrão caso arquivo não exista
            return {
                "entidades_ignoradas": {
                    "cedentes": ["Amfi Digital Assets LTDA"],
                    "sacados": ["Amfi Digital Assets LTDA"]
                },
                "configuracoes_adicionais": {
                    "case_sensitive": False,
                    "normalize_names": True,
                    "partial_match": False
                }
            }
    except Exception as e:
        print(f"⚠️ Erro ao carregar filtros de concentração: {e}")
        # Retorna configuração padrão mínima
        return {
            "entidades_ignoradas": {
                "cedentes": ["Amfi Digital Assets LTDA"],
                "sacados": ["Amfi Digital Assets LTDA"]
            },
            "configuracoes_adicionais": {
                "case_sensitive": False,
                "normalize_names": True,
                "partial_match": False
            }
        }


def _should_ignore_entity(entity_name: str, entity_type: str, filters_config: Dict[str, Any]) -> bool:
    """
    Verifica se uma entidade deve ser ignorada nos cálculos de concentração.
    
    Args:
        entity_name: Nome da entidade (cedente/sacado)
        entity_type: Tipo da entidade ('cedente' ou 'sacado')
        filters_config: Configuração de filtros
        
    Returns:
        True se deve ignorar, False caso contrário
    """
    try:
        entidades_ignoradas = filters_config.get("entidades_ignoradas", {})
        lista_ignoradas = entidades_ignoradas.get(f"{entity_type}s", [])
        
        if not lista_ignoradas:
            return False
        
        # Configurações de comparação
        config_adicional = filters_config.get("configuracoes_adicionais", {})
        case_sensitive = config_adicional.get("case_sensitive", False)
        normalize_names = config_adicional.get("normalize_names", True)
        partial_match = config_adicional.get("partial_match", False)
        
        # Normalizar nome se configurado
        entity_check = entity_name
        if normalize_names:
            entity_check = entity_name.strip()
        
        # Verificar cada entidade na lista
        for ignored_entity in lista_ignoradas:
            ignored_check = ignored_entity
            if normalize_names:
                ignored_check = ignored_entity.strip()
            
            # Comparação case sensitive/insensitive
            if case_sensitive:
                if partial_match:
                    if ignored_check in entity_check:
                        return True
                else:
                    if ignored_check == entity_check:
                        return True
            else:
                entity_lower = entity_check.lower()
                ignored_lower = ignored_check.lower()
                
                if partial_match:
                    if ignored_lower in entity_lower:
                        return True
                else:
                    if ignored_lower == entity_lower:
                        return True
        
        return False
        
    except Exception as e:
        print(f"⚠️ Erro ao verificar entidade ignorada: {e}")
        # Em caso de erro, não ignora para segurança
        return False


def _filter_concentration_data(df: pd.DataFrame, entity_type: str, filters_config: Dict[str, Any]) -> pd.DataFrame:
    """
    Filtra DataFrame removendo entidades que devem ser ignoradas.
    
    Args:
        df: DataFrame com dados de concentração
        entity_type: Tipo da entidade ('cedente' ou 'sacado')  
        filters_config: Configuração de filtros
        
    Returns:
        DataFrame filtrado
    """
    try:
        # Determinar coluna baseada no tipo de entidade
        if entity_type == "cedente":
            entity_column = "nome_do_cedente"
        elif entity_type == "sacado":
            entity_column = "nome_do_sacado"
        else:
            return df
        
        # Verificar se coluna existe
        if entity_column not in df.columns:
            return df
        
        # Filtrar dados
        mask = df[entity_column].apply(
            lambda x: not _should_ignore_entity(str(x), entity_type, filters_config)
        )
        
        filtered_df = df[mask].copy()
        
        # Log se alguma entidade foi filtrada
        original_count = len(df)
        filtered_count = len(filtered_df)
        
        if original_count != filtered_count:
            removed_count = original_count - filtered_count
            print(f"🔽 Concentração {entity_type}: {removed_count} registros filtrados (entidades ignoradas)")
        
        return filtered_df
        
    except Exception as e:
        print(f"⚠️ Erro ao filtrar dados de concentração: {e}")
        # Em caso de erro, retorna dados originais
        return df


def _has_concentration_monitoring(config: Dict[str, Any]) -> bool:
    """Verifica se monitor de concentração está ativo."""
    try:
        monitores = config.get('monitoramentos_ativos', [])
        for monitor in monitores:
            if monitor.get('tipo') == 'concentracao' and monitor.get('ativo', False):
                return True
        return False
    except:
        return False


def _parse_concentration_config(config: Dict[str, Any]) -> List[ConcentrationLimit]:
    """
    Parseia configuração de concentração do JSON do pool.
    
    Args:
        config: Configuração completa do pool
        
    Returns:
        Lista de limites de concentração
    """
    limites = []
    
    # Buscar monitor de concentração
    monitores = config.get('monitoramentos_ativos', [])
    monitor_concentracao = None
    
    for monitor in monitores:
        if monitor.get('tipo') == 'concentracao' and monitor.get('ativo', False):
            monitor_concentracao = monitor
            break
    
    if not monitor_concentracao:
        return limites
    
    # Parsear limites
    for limite_config in monitor_concentracao.get('limites', []):
        try:
            # Tipo de concentração
            tipo_str = limite_config.get('tipo', '').lower()
            if tipo_str == 'individual':
                tipo = ConcentrationType.INDIVIDUAL
            elif tipo_str == 'top_n':
                tipo = ConcentrationType.TOP_N
            else:
                continue  # Ignorar tipos não suportados
            
            # Entidade
            entidade_str = limite_config.get('entidade', '').lower()
            if entidade_str == 'sacado':
                entidade = ConcentrationEntity.SACADO
            elif entidade_str == 'cedente':
                entidade = ConcentrationEntity.CEDENTE
            else:
                continue  # Ignorar entidades não suportadas
            
            # Limite
            limite_valor = limite_config.get('limite', 0.0)
            
            # Parâmetros opcionais
            n = limite_config.get('n')
            
            limite = ConcentrationLimit(
                tipo=tipo,
                entidade=entidade,
                limite=limite_valor,
                n=n
            )
            
            limites.append(limite)
            
        except Exception as e:
            print(f"Erro ao parsear limite de concentração: {e}")
            continue
    
    return limites


def _calculate_individual_concentration(carteira_df: pd.DataFrame, 
                                        limite: ConcentrationLimit, 
                                        pl_pool: float) -> Dict[str, Any]:
    """
    Calcula concentração individual por entidade.
    
    Args:
        carteira_df: DataFrame com carteira do pool
        limite: Configuração do limite individual
        pl_pool: Patrimônio líquido do pool
        
    Returns:
        Dict com resultado da concentração individual
    """
    # Validar entrada
    if carteira_df.empty:
        return {
            "tipo": "individual",
            "entidade": limite.entidade.value,
            "limite_configurado": limite.limite * 100,
            "pl_pool": 0.0,
            "maior_concentracao": {
                "entidade": "N/A",
                "valor_absoluto": 0.0,
                "percentual_pl": 0.0,
                "quantidade_titulos": 0
            },
            "status": "erro",
            "erro": "Carteira vazia"
        }
    
    # Carregar configuração de filtros
    filters_config = _load_concentration_filters()
    
    # Filtrar dados removendo entidades ignoradas
    filtered_df = _filter_concentration_data(carteira_df, limite.entidade.value, filters_config)
    
    # Verificar se ainda há dados após filtro
    if filtered_df.empty:
        return {
            "tipo": "individual",
            "entidade": limite.entidade.value,
            "limite_configurado": limite.limite * 100,
            "pl_pool": pl_pool,
            "maior_concentracao": {
                "entidade": "N/A",
                "valor_absoluto": 0.0,
                "percentual_pl": 0.0,
                "quantidade_titulos": 0
            },
            "status": "sem_dados",
            "observacao": "Todas as entidades foram filtradas (entidades ignoradas)"
        }
    
    # Mapear entidade para coluna
    if limite.entidade == ConcentrationEntity.SACADO:
        entidade_col = 'nome_do_sacado'
    else:  # CEDENTE
        entidade_col = 'nome_do_cedente'
    
    # Verificar se coluna existe
    if entidade_col not in filtered_df.columns:
        return {
            "tipo": "individual",
            "entidade": limite.entidade.value,
            "limite_configurado": limite.limite * 100,
            "pl_pool": pl_pool,
            "maior_concentracao": {
                "entidade": "N/A",
                "valor_absoluto": 0.0,
                "percentual_pl": 0.0,
                "quantidade_titulos": 0
            },
            "status": "erro",
            "erro": f"Coluna '{entidade_col}' não encontrada na carteira"
        }
    
    # Calcular concentração por entidade
    concentracao_df = filtered_df.groupby(entidade_col).agg({
        'valor_presente': ['sum', 'count']
    }).reset_index()
    
    # Achatar colunas
    concentracao_df.columns = ['entidade', 'valor_total', 'quantidade_titulos']
    concentracao_df = concentracao_df.sort_values('valor_total', ascending=False)
    
    # Calcular percentuais vs PL
    concentracao_df['percentual_pl'] = (concentracao_df['valor_total'] / pl_pool) * 100
    
    # Identificar maior concentração
    maior_concentracao = concentracao_df.iloc[0]
    
    # Verificar violação
    limite_percent = limite.limite * 100
    violacao = maior_concentracao['percentual_pl'] > limite_percent
    
    return {
        "tipo": "individual",
        "entidade": limite.entidade.value,
        "limite_configurado": limite_percent,
        "pl_pool": pl_pool,
        "maior_concentracao": {
            "entidade": maior_concentracao['entidade'],
            "valor_absoluto": float(maior_concentracao['valor_total']),
            "percentual_pl": float(maior_concentracao['percentual_pl']),
            "quantidade_titulos": int(maior_concentracao['quantidade_titulos'])
        },
        "status": "violado" if violacao else "enquadrado",
        "margem_limite": limite_percent - maior_concentracao['percentual_pl'],
        "total_entidades": len(concentracao_df)
    }


def _calculate_top_n_concentration(carteira_df: pd.DataFrame, 
                                   limite: ConcentrationLimit, 
                                   pl_pool: float) -> Dict[str, Any]:
    """
    Calcula concentração top-N por entidade.
    
    Args:
        carteira_df: DataFrame com carteira do pool
        limite: Configuração do limite top-N
        pl_pool: Patrimônio líquido do pool
        
    Returns:
        Dict com resultado da concentração top-N
    """
    # Validar entrada
    if carteira_df.empty:
        return {
            "tipo": "top_n",
            "entidade": limite.entidade.value,
            "n": limite.n,
            "limite_configurado": limite.limite * 100,
            "pl_pool": 0.0,
            "concentracao_top_n": {
                "percentual_pl": 0.0,
                "valor_absoluto": 0.0,
                "quantidade_entidades": 0
            },
            "status": "erro",
            "erro": "Carteira vazia"
        }
    
    # Carregar configuração de filtros
    filters_config = _load_concentration_filters()
    
    # Filtrar dados removendo entidades ignoradas
    filtered_df = _filter_concentration_data(carteira_df, limite.entidade.value, filters_config)
    
    # Verificar se ainda há dados após filtro
    if filtered_df.empty:
        return {
            "tipo": "top_n",
            "entidade": limite.entidade.value,
            "n": limite.n,
            "limite_configurado": limite.limite * 100,
            "pl_pool": pl_pool,
            "concentracao_top_n": {
                "percentual_pl": 0.0,
                "valor_absoluto": 0.0,
                "quantidade_entidades": 0
            },
            "status": "sem_dados",
            "observacao": "Todas as entidades foram filtradas (entidades ignoradas)"
        }
    
    # Mapear entidade para coluna
    if limite.entidade == ConcentrationEntity.SACADO:
        entidade_col = 'nome_do_sacado'
    else:  # CEDENTE
        entidade_col = 'nome_do_cedente'
    
    # Verificar se coluna existe
    if entidade_col not in filtered_df.columns:
        return {
            "tipo": "top_n",
            "entidade": limite.entidade.value,
            "n": limite.n,
            "limite_configurado": limite.limite * 100,
            "pl_pool": pl_pool,
            "concentracao_top_n": {
                "percentual_pl": 0.0,
                "valor_absoluto": 0.0,
                "quantidade_entidades": 0
            },
            "status": "erro",
            "erro": f"Coluna '{entidade_col}' não encontrada na carteira"
        }
    
    # Calcular concentração por entidade
    concentracao_df = filtered_df.groupby(entidade_col).agg({
        'valor_presente': ['sum', 'count']
    }).reset_index()
    
    # Achatar colunas
    concentracao_df.columns = ['entidade', 'valor_total', 'quantidade_titulos']
    concentracao_df = concentracao_df.sort_values('valor_total', ascending=False)
    
    # Pegar top-N
    top_n_df = concentracao_df.head(limite.n)
    
    # Calcular concentração total do top-N
    valor_total_top_n = top_n_df['valor_total'].sum()
    percentual_top_n = (valor_total_top_n / pl_pool) * 100
    
    # Verificar violação
    limite_percent = limite.limite * 100
    violacao = percentual_top_n > limite_percent
    
    return {
        "tipo": "top_n",
        "entidade": limite.entidade.value,
        "n": limite.n,
        "limite_configurado": limite_percent,
        "pl_pool": pl_pool,
        "concentracao_top_n": {
            "percentual_pl": float(percentual_top_n),
            "valor_absoluto": float(valor_total_top_n),
            "quantidade_entidades": len(top_n_df)
        },
        "status": "violado" if violacao else "enquadrado",
        "margem_limite": limite_percent - percentual_top_n,
        "total_entidades": len(concentracao_df)
    }


def _gerar_explicacao_sequencial(capacidade_efetiva: float, limitada_por: str, 
                                capacidade_individual: float, saldo_disponivel: float) -> str:
    """Gera explicação clara da limitação sequencial."""
    
    if limitada_por == "esgotado":
        return "Espaço Top-N já esgotado por posições anteriores"
    elif limitada_por == "individual":
        return f"Limitado por teto individual. Restaria {saldo_disponivel - capacidade_efetiva:.1f} no Top-N"
    elif limitada_por == "top_n":
        return f"Usa todo saldo Top-N restante. Individual permitiria {capacidade_individual:.1f}"
    else:
        return "Análise não disponível"


def _gerar_matriz_sobra_tabular(analise_sequencial: List[Dict], resumo_analise: Dict) -> Dict[str, Any]:
    """
    Gera matriz de sobra tabular para visualização clara da capacidade incremental.
    
    Args:
        analise_sequencial: Lista com análise sequencial por posição
        resumo_analise: Dict com resumo da análise (PL, limites, etc.)
        
    Returns:
        Dict com matriz tabular formatada e dados estruturados
    """
    
    # Cabeçalho da matriz
    cabecalho_info = {
        "pl_pool": resumo_analise["pl_pool"],
        "limite_individual": resumo_analise.get("limite_individual_pct"),
        "limite_top_n": resumo_analise["limite_top_n_pct"],
        "top_n_size": resumo_analise["top_n_size"],
        "espaco_disponivel": resumo_analise["espaco_total_disponivel"]
    }
    
    # Gerar linhas da tabela
    linhas_tabela = []
    for item in analise_sequencial:
        linha = {
            "posicao": item["posicao"],
            "entidade": item["entidade"],
            "exposicao_atual": item["exposicao_atual"],
            "percentual_atual": item["percentual_atual"],
            "capacidade_individual": item.get("capacidade_individual", 0) or 0,
            "capacidade_efetiva": item["capacidade_efetiva"],
            "saldo_antes": item["saldo_antes"],
            "saldo_apos": item["saldo_apos"],
            "limitada_por": item["limitada_por"],
            "pode_crescer": f"+{item['capacidade_efetiva']:.0f}",
            "sobra_proximo": f"{item['saldo_apos']:.0f}"
        }
        linhas_tabela.append(linha)
    
    # Gerar tabela ASCII formatada
    tabela_ascii = _formatar_tabela_ascii(linhas_tabela, cabecalho_info)
    
    # Gerar resumo da matriz
    total_crescimento_possivel = sum(item["capacidade_efetiva"] for item in analise_sequencial)
    entidades_com_capacidade = len([item for item in analise_sequencial if item["capacidade_efetiva"] > 0])
    
    resumo_matriz = {
        "total_crescimento_possivel": total_crescimento_possivel,
        "entidades_com_capacidade": entidades_com_capacidade,
        "total_entidades_analisadas": len(analise_sequencial),
        "utilizacao_espaco_disponivel": (total_crescimento_possivel / resumo_analise["espaco_total_disponivel"]) * 100 if resumo_analise["espaco_total_disponivel"] > 0 else 0
    }
    
    return {
        "cabecalho": cabecalho_info,
        "linhas": linhas_tabela,
        "tabela_ascii": tabela_ascii,
        "resumo": resumo_matriz
    }


def _formatar_tabela_ascii(linhas: List[Dict], cabecalho: Dict) -> str:
    """
    Formata matriz de sobra em tabela ASCII legível.
    
    Args:
        linhas: Lista com dados das linhas
        cabecalho: Dict com informações do cabeçalho
        
    Returns:
        String com tabela ASCII formatada
    """
    
    # Cabeçalho informativo
    header_info = f"""
MATRIZ DE SOBRA - ANÁLISE SEQUENCIAL
PL: {cabecalho['pl_pool']:,.0f} | Individual: {cabecalho.get('limite_individual', 'N/A')}% | Top-{cabecalho['top_n_size']}: {cabecalho['limite_top_n']}%
Espaço disponível: {cabecalho['espaco_disponivel']:,.0f}
"""
    
    # Larguras das colunas
    col_entidade = max(len(linha["entidade"]) for linha in linhas) + 2
    col_entidade = max(col_entidade, 12)  # Mínimo 12 chars
    
    # Cabeçalho da tabela
    separador = "┌" + "─" * col_entidade + "┬" + "─" * 8 + "┬" + "─" * 10 + "┬" + "─" * 13 + "┬" + "─" * 13 + "┬" + "─" * 15 + "┐"
    cabecalho_tabela = f"│{'Entidade':<{col_entidade}}│{'Atual':<8}│{'Cap.Indiv':<10}│{'Cap.Efetiva':<13}│{'Saldo Antes':<13}│{'Limitado Por':<15}│"
    separador_meio = "├" + "─" * col_entidade + "┼" + "─" * 8 + "┼" + "─" * 10 + "┼" + "─" * 13 + "┼" + "─" * 13 + "┼" + "─" * 15 + "┤"
    
    # Linhas de dados
    linhas_dados = []
    for linha in linhas:
        entidade = linha["entidade"][:col_entidade-2]  # Truncar se muito longo
        atual = f"{linha['exposicao_atual']:.0f}"
        cap_indiv = f"+{linha['capacidade_individual']:.0f}" if linha['capacidade_individual'] and linha['capacidade_individual'] > 0 else "0"
        cap_efetiva = f"+{linha['capacidade_efetiva']:.0f}"
        saldo_antes = f"{linha['saldo_antes']:.0f}"
        limitada_por = linha["limitada_por"][:13]  # Truncar se muito longo
        
        linha_formatada = f"│{entidade:<{col_entidade}}│{atual:<8}│{cap_indiv:<10}│{cap_efetiva:<13}│{saldo_antes:<13}│{limitada_por:<15}│"
        linhas_dados.append(linha_formatada)
    
    # Rodapé da tabela
    separador_fim = "└" + "─" * col_entidade + "┴" + "─" * 8 + "┴" + "─" * 10 + "┴" + "─" * 13 + "┴" + "─" * 13 + "┴" + "─" * 15 + "┘"
    
    # Montar tabela completa
    tabela_completa = "\n".join([
        header_info,
        separador,
        cabecalho_tabela,
        separador_meio,
        *linhas_dados,
        separador_fim
    ])
    
    return tabela_completa


def _calculate_sequential_capacity(concentracao_df: pd.DataFrame,
                                   limites: List[ConcentrationLimit], 
                                   pl_pool: float,
                                   entidade_tipo: str = "sacado") -> Dict[str, Any]:
    """
    Calcula capacidade sequencial/cascata considerando ordem de prioridade.
    
    Simula como o espaço disponível vai sendo consumido sequencialmente,
    mostrando saldo restante após cada alocação.
    
    Args:
        concentracao_df: DataFrame com concentração por entidade (já ordenado)
        limites: Lista de limites de concentração
        pl_pool: Patrimônio líquido do pool
        entidade_tipo: "sacado" ou "cedente"
        
    Returns:
        Dict com análise sequencial de capacidade
    """
    
    # Identificar limites relevantes para esta entidade
    limite_individual = None
    limite_top_n = None
    
    for limite in limites:
        if limite.entidade.value == entidade_tipo:
            if limite.tipo == ConcentrationType.INDIVIDUAL:
                limite_individual = limite
            elif limite.tipo == ConcentrationType.TOP_N:
                limite_top_n = limite
    
    if not limite_top_n:
        # Se não tem top-N, não faz sentido análise sequencial
        return {
            "tipo_analise": "sem_top_n",
            "mensagem": f"Análise sequencial não aplicável - sem limite Top-N para {entidade_tipo}"
        }
    
    # Calcular espaço disponível no top-N
    top_n_df = concentracao_df.head(limite_top_n.n)
    top_n_atual = top_n_df['valor_total'].sum()
    limite_top_n_valor = limite_top_n.limite * pl_pool
    espaco_total_disponivel = limite_top_n_valor - top_n_atual
    
    # Análise sequencial
    analise_sequencial = []
    saldo_restante = espaco_total_disponivel
    
    for i, (_, row) in enumerate(top_n_df.iterrows()):
        entidade = row['entidade']
        exposicao_atual = row['valor_total']
        percentual_atual = (exposicao_atual / pl_pool) * 100
        
        # Capacidade individual disponível
        if limite_individual:
            limite_individual_valor = limite_individual.limite * pl_pool
            capacidade_individual = limite_individual_valor - exposicao_atual
        else:
            capacidade_individual = float('inf')
        
        # Capacidade efetiva = min(individual, saldo_restante)
        capacidade_efetiva = min(
            max(0, capacidade_individual) if capacidade_individual != float('inf') else saldo_restante,
            max(0, saldo_restante)
        )
        
        # Determinar limitação
        if saldo_restante <= 0:
            limitada_por = "esgotado"
        elif capacidade_individual != float('inf') and capacidade_individual <= saldo_restante:
            limitada_por = "individual"
        else:
            limitada_por = "top_n"
        
        # Atualizar saldo restante
        saldo_apos_uso = saldo_restante - capacidade_efetiva
        
        analise_sequencial.append({
            "posicao": i + 1,
            "entidade": entidade,
            "exposicao_atual": float(exposicao_atual),
            "percentual_atual": float(percentual_atual),
            "capacidade_individual": float(max(0, capacidade_individual)) if capacidade_individual != float('inf') else None,
            "capacidade_efetiva": float(capacidade_efetiva),
            "saldo_antes": float(saldo_restante),
            "saldo_apos": float(max(0, saldo_apos_uso)),
            "limitada_por": limitada_por,
            "explicacao": _gerar_explicacao_sequencial(
                capacidade_efetiva, 
                limitada_por, 
                capacidade_individual if capacidade_individual != float('inf') else 0, 
                saldo_restante
            )
        })
        
        # Atualizar saldo para próxima iteração
        saldo_restante = max(0, saldo_apos_uso)
    
    # Gerar matriz de sobra tabular
    matriz_sobra = _gerar_matriz_sobra_tabular(analise_sequencial, resumo_analise={
        "pl_pool": float(pl_pool),
        "limite_individual_pct": float(limite_individual.limite * 100) if limite_individual else None,
        "limite_top_n_pct": float(limite_top_n.limite * 100),
        "top_n_size": limite_top_n.n,
        "espaco_total_disponivel": float(espaco_total_disponivel)
    })

    return {
        "tipo_analise": "sequencial",
        "entidade_tipo": entidade_tipo,
        "resumo": {
            "pl_pool": float(pl_pool),
            "limite_individual_pct": float(limite_individual.limite * 100) if limite_individual else None,
            "limite_top_n_pct": float(limite_top_n.limite * 100),
            "top_n_size": limite_top_n.n,
            "exposicao_top_n_atual": float(top_n_atual),
            "percentual_top_n_atual": float((top_n_atual / pl_pool) * 100),
            "espaco_total_disponivel": float(espaco_total_disponivel),
            "espaco_utilizado_na_analise": float(espaco_total_disponivel - saldo_restante)
        },
        "analise_sequencial": analise_sequencial,
        "matriz_sobra_tabular": matriz_sobra
    }


def run_concentration_monitoring(pool_data_csv: pd.DataFrame,
                                 carteira_xlsx: pd.DataFrame,
                                 config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Interface principal do monitor de concentração.
    
    Args:
        pool_data_csv: DataFrame com dados do pool (PL, etc.)
        carteira_xlsx: DataFrame com carteira detalhada
        config: Configuração do pool (JSON)
        
    Returns:
        Dict com resultados do monitoramento
    """
    try:
        # Informações básicas
        pool_id = config.get('pool_id', 'desconhecido')
        
        # Verificar se monitoramento está ativo
        if not _has_concentration_monitoring(config):
            return {
                "sucesso": True,
                "pool_id": pool_id,
                "status_geral": "sem_limites",
                "configuracao": {
                    "ativo": False,
                    "numero_limites": 0,
                    "complexidade": "sem_limites"
                },
                "resumo": {
                    "total_limites_analisados": 0,
                    "limites_enquadrados": 0,
                    "limites_violados": 0
                },
                "resultados_por_limite": [],
                "timestamp": datetime.now().isoformat()
            }
        
        # Obter PL do pool
        if pool_data_csv.empty:
            raise ValueError("Dados do pool não encontrados")
        
        pl_pool = pool_data_csv['pl'].iloc[0]
        if pd.isna(pl_pool) or pl_pool <= 0:
            raise ValueError(f"PL do pool inválido: {pl_pool}")
        
        # Filtrar carteira para o pool
        nome_pool = pool_data_csv['pool'].iloc[0] if 'pool' in pool_data_csv.columns else pool_id
        carteira_pool = carteira_xlsx[carteira_xlsx['pool'] == nome_pool]
        
        if carteira_pool.empty:
            raise ValueError(f"Carteira do pool '{nome_pool}' não encontrada")
        
        # Parsear configuração
        limites = _parse_concentration_config(config)
        
        if not limites:
            return {
                "sucesso": True,
                "pool_id": pool_id,
                "status_geral": "sem_limites",
                "configuracao": {
                    "ativo": True,
                    "numero_limites": 0,
                    "complexidade": "sem_limites"
                },
                "resumo": {
                    "total_limites_analisados": 0,
                    "limites_enquadrados": 0,
                    "limites_violados": 0
                },
                "resultados_por_limite": [],
                "timestamp": datetime.now().isoformat()
            }
        
        # Calcular concentração para cada limite
        resultados_limites = []
        limites_enquadrados = 0
        limites_violados = 0
        
        for i, limite in enumerate(limites):
            limite_id = f"limite_{i+1}"
            
            try:
                if limite.tipo == ConcentrationType.INDIVIDUAL:
                    resultado = _calculate_individual_concentration(carteira_pool, limite, pl_pool)
                elif limite.tipo == ConcentrationType.TOP_N:
                    resultado = _calculate_top_n_concentration(carteira_pool, limite, pl_pool)
                else:
                    resultado = {
                        "tipo": limite.tipo.value,
                        "entidade": limite.entidade.value,
                        "status": "erro",
                        "erro": f"Tipo de concentração não suportado: {limite.tipo.value}"
                    }
                
                # Adicionar ID do limite
                resultado["limite_id"] = limite_id
                
                # Contar status
                if resultado["status"] == "enquadrado":
                    limites_enquadrados += 1
                elif resultado["status"] == "violado":
                    limites_violados += 1
                
                resultados_limites.append(resultado)
                
            except Exception as e:
                resultado_erro = {
                    "limite_id": limite_id,
                    "tipo": limite.tipo.value,
                    "entidade": limite.entidade.value,
                    "status": "erro",
                    "erro": str(e)
                }
                resultados_limites.append(resultado_erro)
        
        # Determinar status geral
        if limites_violados > 0:
            status_geral = "violado"
        elif limites_enquadrados > 0:
            status_geral = "enquadrado"
        else:
            status_geral = "erro"
        
        # Determinar complexidade
        num_limites = len(limites)
        if num_limites == 0:
            complexidade = "sem_limites"
        elif num_limites == 1:
            complexidade = "simples"
        elif num_limites == 2:
            complexidade = "media"
        else:
            complexidade = "alta"
        
        # Adicionar análise sequencial de capacidade (se aplicável)
        analises_capacidade = {}
        
        try:
            # Preparar dados de concentração para análise sequencial
            for entidade_tipo in ['sacado', 'cedente']:
                # Verificar se há limites para esta entidade
                tem_limites_entidade = any(
                    limite.entidade.value == entidade_tipo 
                    for limite in limites
                )
                
                if tem_limites_entidade:
                    # Mapear entidade para coluna
                    if entidade_tipo == 'sacado':
                        entidade_col = 'nome_do_sacado'
                    else:
                        entidade_col = 'nome_do_cedente'
                    
                    # Verificar se coluna existe na carteira
                    if entidade_col in carteira_pool.columns:
                        # 🔧 CORREÇÃO: Aplicar filtro antes de processar dados
                        filters_config = _load_concentration_filters()
                        filtered_carteira = _filter_concentration_data(carteira_pool, entidade_tipo, filters_config)
                        
                        # Calcular concentração por entidade com dados filtrados
                        concentracao_df = filtered_carteira.groupby(entidade_col).agg({
                            'valor_presente': ['sum', 'count']
                        }).reset_index()
                        
                        # Achatar colunas
                        concentracao_df.columns = ['entidade', 'valor_total', 'quantidade_titulos']
                        concentracao_df = concentracao_df.sort_values('valor_total', ascending=False)
                        
                        # Calcular análise sequencial
                        analise_sequencial = _calculate_sequential_capacity(
                            concentracao_df, limites, pl_pool, entidade_tipo
                        )
                        
                        if analise_sequencial.get("tipo_analise") == "sequencial":
                            analises_capacidade[entidade_tipo] = analise_sequencial
        
        except Exception as e:
            # Se análise sequencial falhar, continua sem ela
            analises_capacidade["erro_analise_capacidade"] = str(e)
        
        resultado_final = {
            "sucesso": True,
            "pool_id": pool_id,
            "pl_pool": pl_pool,
            "status_geral": status_geral,
            "configuracao": {
                "ativo": True,
                "numero_limites": num_limites,
                "complexidade": complexidade
            },
            "resumo": {
                "total_limites_analisados": num_limites,
                "limites_enquadrados": limites_enquadrados,
                "limites_violados": limites_violados
            },
            "resultados_por_limite": resultados_limites,
            "timestamp": datetime.now().isoformat()
        }
        
        # Adicionar análises de capacidade se disponíveis
        if analises_capacidade:
            resultado_final["analises_capacidade"] = analises_capacidade
        
        return resultado_final
        
    except Exception as e:
        return {
            "sucesso": False,
            "pool_id": config.get('pool_id', 'desconhecido'),
            "erro": str(e),
            "timestamp": datetime.now().isoformat()
        }


# Funções auxiliares para compatibilidade com código existente
def create_concentration_config(config: Dict[str, Any]):
    """Compatibilidade com código existente."""
    return _parse_concentration_config(config)


def calculate_concentration_for_limit(carteira_df: pd.DataFrame, limite, pl_pool: float):
    """Compatibilidade com código existente."""
    if limite.tipo == ConcentrationType.INDIVIDUAL:
        return _calculate_individual_concentration(carteira_df, limite, pl_pool)
    elif limite.tipo == ConcentrationType.TOP_N:
        return _calculate_top_n_concentration(carteira_df, limite, pl_pool)
    else:
        return {"status": "erro", "erro": f"Tipo não suportado: {limite.tipo}"}


if __name__ == "__main__":
    print("Monitor de Concentração - Base")
    print("Suporte para concentração individual e top-N")
    print("Funcionalidades customizadas devem usar /monitor/custom/")