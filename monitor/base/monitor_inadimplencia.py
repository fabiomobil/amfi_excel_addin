"""
Monitor de Inadimplência
========================

Responsável por:
- Inadimplência por faixas de atraso (30, 60, 90+ dias)
- Análise de aging de recebíveis
- ENRIQUECIMENTO PROGRESSIVO de dados para outros monitores

ESTRATÉGIA DE ENRIQUECIMENTO DE DADOS:
=====================================

Este monitor implementa a estratégia de ENRIQUECIMENTO PROGRESSIVO:
- Recebe DataFrame XLSX por referência
- ADICIONA campos calculados para futuros monitores (PDD, Concentração, etc.)
- Evita recálculos desnecessários
- Campos adicionados: 'dias_atraso', 'grupo_de_risco'

Integração com Orquestrador:
----------------------------
```python
# Chamada via orchestrator.run_monitoring()
if _has_delinquency_monitoring(config):
    xlsx_enriched = run_delinquency_monitoring(csv_df, xlsx_df, config)
    # DataFrame agora contém campos calculados para próximos monitores
    
if _has_pdd_monitoring(config):
    # Monitor PDD usa dados já enriquecidos
    pdd_result = run_pdd_monitoring(xlsx_enriched, config)
```

Campos Adicionados ao DataFrame XLSX:
-------------------------------------
- 'dias_atraso': int - Dias de atraso calculados vs vencimento_original
- 'grupo_de_risco': str - Classificação AA-H baseada em atraso e config PDD

Benefícios do Enriquecimento:
-----------------------------
✅ Performance: Cálculos feitos uma vez, usados sempre
✅ Consistência: Única fonte de verdade para cada cálculo
✅ Extensibilidade: Novos monitores reutilizam campos existentes
✅ Auditoria: Dados enriquecidos persistem na memória

Cálculo de Inadimplência:
------------------------
% inadimplência = (Σ valor_presente dos títulos atrasados) / PL do pool

Onde:
- Numerador: Soma dos valores presentes onde status = 'atrasada' 
             e dias_atraso >= janela configurada (calculado aqui)
- Denominador: PL do pool (do CSV - coluna 'PL')

Fontes de Dados:
---------------
1. CSV (Dados consolidados):
   - PL: Patrimônio Líquido do pool (denominador)
   - nome: Identificação do pool

2. XLSX (Carteira detalhada - SERÁ ENRIQUECIDA):
   - status: Identifica títulos atrasados ('atrasada')
   - vencimento_original: Data base para cálculo de atraso
   - valor_presente: Valor do título para somatório
   - sacado/cedente: Para análises complementares
   + dias_atraso: ADICIONADO por este monitor
   + grupo_de_risco: ADICIONADO por este monitor

3. JSON (Configuração):
   - Janelas de análise (30, 90 dias, etc.)
   - Limites por janela
   - Grupos de PDD (para classificação de risco)
"""

import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np


def _find_delinquency_monitors(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Busca todos os monitores de inadimplência no JSON de configuração.
    
    Args:
        config: Configuração do pool (JSON)
        
    Returns:
        Lista com configurações dos monitores de inadimplência
    """
    if 'monitoramentos_ativos' not in config:
        raise ValueError("Configuração não contém 'monitoramentos_ativos'")
        
    monitores = []
    for monitor in config['monitoramentos_ativos']:
        if monitor.get('tipo') == 'inadimplencia' and monitor.get('ativo', False):
            monitores.append(monitor)
    
    return monitores


def _find_pdd_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Busca configuração de PDD no JSON.
    
    Args:
        config: Configuração do pool (JSON)
        
    Returns:
        Dict com grupos de risco e provisões
    """
    if 'provisoes_pdd' not in config:
        return {}
    
    return config['provisoes_pdd'].get('grupos_risco', {})


def validate_data(csv_df: pd.DataFrame, xlsx_df: pd.DataFrame, config: Dict[str, Any]) -> bool:
    """
    Valida se os dados de entrada estão adequados para monitoramento de inadimplência.
    
    Args:
        csv_df: DataFrame com dados consolidados do pool
        xlsx_df: DataFrame com carteira detalhada
        config: Configuração do pool (JSON)
        
    Returns:
        bool: True se dados são válidos
        
    Raises:
        ValueError: Se dados essenciais estão ausentes
    """
    # Verificar se há dados
    if csv_df.empty:
        raise ValueError("DataFrame CSV está vazio")
    
    if xlsx_df.empty:
        raise ValueError("DataFrame XLSX está vazio")
    
    # Verificar se há monitores de delinquency ativos
    monitores = _find_delinquency_monitors(config)
    if not monitores:
        raise ValueError("Nenhum monitor de inadimplência ativo encontrado")
    
    # Verificar colunas obrigatórias no CSV
    colunas_csv_obrigatorias = ['pl']
    colunas_csv_lower = [col.lower() for col in csv_df.columns]
    for col in colunas_csv_obrigatorias:
        if col not in colunas_csv_lower:
            raise ValueError(f"Coluna obrigatória '{col}' ausente no CSV")
    
    # Verificar colunas obrigatórias no XLSX
    colunas_xlsx_obrigatorias = ['status', 'vencimento_original', 'valor_presente']
    for col in colunas_xlsx_obrigatorias:
        if col not in xlsx_df.columns:
            raise ValueError(f"Coluna obrigatória '{col}' ausente no XLSX")
    
    # Verificar se PL é válido (maior que zero)
    pl_col = 'pl' if 'pl' in csv_df.columns else 'PL'
    pl_value = csv_df[pl_col].iloc[0]
    
    if pd.isna(pl_value) or pl_value <= 0:
        raise ValueError(f"PL inválido: {pl_value}. Deve ser maior que zero.")
    
    # Verificar se valores_presente são numéricos
    if not pd.api.types.is_numeric_dtype(xlsx_df['valor_presente']):
        raise ValueError("Coluna 'valor_presente' não é numérica")
    
    # Verificar se há pelo menos um monitor com limites configurados
    for monitor in monitores:
        limites = monitor.get('limites', {})
        if 'prazo_dias' not in limites or 'limite' not in limites:
            raise ValueError(f"Monitor {monitor.get('id')} sem configuração completa de limites")
    
    return True


def calculate_days_overdue(xlsx_df: pd.DataFrame, reference_date: Optional[datetime] = None) -> pd.DataFrame:
    """
    Calcula dias de atraso para cada título baseado em vencimento_original.
    
    Args:
        xlsx_df: DataFrame com carteira
        reference_date: Data de referência (None = hoje)
        
    Returns:
        DataFrame com coluna 'dias_atraso' adicionada
    """
    df = xlsx_df.copy()
    
    # Data de referência
    if reference_date is None:
        reference_date = datetime.now()
    
    # Converter vencimento_original para datetime se necessário
    if not pd.api.types.is_datetime64_any_dtype(df['vencimento_original']):
        df['vencimento_original'] = pd.to_datetime(df['vencimento_original'], errors='coerce')
    
    # Calcular dias de atraso
    df['dias_atraso'] = (reference_date - df['vencimento_original']).dt.days
    
    # Apenas valores positivos (negativos = ainda não venceu)
    df['dias_atraso'] = df['dias_atraso'].clip(lower=0)
    
    return df


def calculate_delinquency_by_window(
    xlsx_df: pd.DataFrame, 
    csv_df: pd.DataFrame, 
    window_days: int,
    limite: float
) -> Dict[str, Any]:
    """
    Calcula inadimplência para qualquer janela de dias especificada.
    Função genérica que pode ser usada para 30, 60, 90 ou qualquer número de dias.
    
    Args:
        xlsx_df: DataFrame com carteira detalhada (deve ter 'dias_atraso' calculado)
        csv_df: DataFrame com dados do pool
        window_days: Janela de análise (30, 60, 90, etc.)
        limite: Limite configurado para esta janela (em decimal, ex: 0.04 para 4%)
        
    Returns:
        Dict com percentual, valor e status de compliance
    """
    # Obter PL do pool (usar primeira linha)
    pl_col = 'pl' if 'pl' in csv_df.columns else 'PL'
    pl_pool = csv_df[pl_col].iloc[0]
    
    # Filtrar apenas títulos atrasados
    titulos_atrasados = xlsx_df[xlsx_df['status'] == 'atrasada'].copy()
    
    # Se não há títulos atrasados, retornar zero
    if titulos_atrasados.empty:
        return {
            "percentual": 0.0,
            "valor_absoluto": 0.0,
            "pl_base": float(pl_pool),
            "limite": limite * 100,
            "status": "enquadrado",
            "quantidade_titulos": 0
        }
    
    # Filtrar por janela (>= window_days)
    titulos_janela = titulos_atrasados[titulos_atrasados['dias_atraso'] >= window_days]
    
    # Calcular valores
    valor_total_atraso = titulos_janela['valor_presente'].sum()
    quantidade_titulos = len(titulos_janela)
    
    # Calcular percentual
    percentual_delinquency = (valor_total_atraso / pl_pool) * 100
    
    # Determinar status
    status = "enquadrado" if percentual_delinquency <= (limite * 100) else "violado"
    
    # Calcular margem
    margem = (limite * 100) - percentual_delinquency
    
    return {
        "percentual": round(percentual_delinquency, 2),
        "valor_absoluto": round(float(valor_total_atraso), 2),
        "pl_base": round(float(pl_pool), 2),
        "limite": round(limite * 100, 2),
        "status": status,
        "margem": round(margem, 2),
        "quantidade_titulos": quantidade_titulos
    }


# Função calculate_pdd() movida para monitor_pdd.py
# Mantida apenas classificação de grupo_de_risco para enriquecimento


def generate_aging_analysis(xlsx_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Gera análise de aging da carteira completa.
    
    Args:
        xlsx_df: DataFrame com carteira (deve ter 'dias_atraso' calculado)
        
    Returns:
        Dict com distribuição por faixas de atraso
    """
    # Definir faixas de aging
    faixas = [
        (0, 0, "adimplente"),
        (1, 30, "1-30"),
        (31, 60, "31-60"),
        (61, 90, "61-90"),
        (91, float('inf'), "90+")
    ]
    
    total_carteira = xlsx_df['valor_presente'].sum()
    analise = {}
    
    for min_dias, max_dias, label in faixas:
        if label == "adimplente":
            # Títulos não atrasados
            mask = (xlsx_df['status'] != 'atrasada') | (xlsx_df['dias_atraso'] == 0)
        else:
            # Títulos atrasados na faixa
            mask = (xlsx_df['status'] == 'atrasada') & \
                   (xlsx_df['dias_atraso'] >= min_dias) & \
                   (xlsx_df['dias_atraso'] <= max_dias)
        
        titulos_faixa = xlsx_df[mask]
        valor_faixa = titulos_faixa['valor_presente'].sum()
        
        analise[label] = {
            "quantidade": len(titulos_faixa),
            "valor": round(float(valor_faixa), 2),
            "percentual": round((valor_faixa / total_carteira * 100) if total_carteira > 0 else 0, 2)
        }
    
    return {
        "faixas": analise,
        "total_carteira": round(float(total_carteira), 2)
    }


def run_delinquency_monitoring(
    pool_data_csv: pd.DataFrame,
    carteira_xlsx: pd.DataFrame,
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Interface principal para o orquestrador com ENRIQUECIMENTO PROGRESSIVO.
    
    NOVA FUNCIONALIDADE (2025-07-13): 
    - Modifica o DataFrame carteira_xlsx IN-PLACE (enriquecimento progressivo)
    - Adiciona campos: 'dias_atraso', 'grupo_de_risco'
    - Permite que futuros monitores usem campos já calculados
    
    Args:
        pool_data_csv: DataFrame com dados consolidados do pool (deve conter PL)
        carteira_xlsx: DataFrame com carteira detalhada de recebíveis (SERÁ MODIFICADO)
        config: Configuração do pool (JSON)
        
    Returns:
        Dict com resultados de todos os monitores de inadimplência
        
    Note:
        carteira_xlsx é modificado in-place com novos campos calculados
    """
    try:
        # Validar dados de entrada
        validate_data(pool_data_csv, carteira_xlsx, config)
        
        # ENRIQUECIMENTO PROGRESSIVO 1: Adicionar dias_atraso ao DataFrame GLOBAL
        if 'dias_atraso' not in carteira_xlsx.columns:
            # Calcular dias de atraso para TODA a carteira (não apenas este pool)
            carteira_xlsx_enriched = calculate_days_overdue(carteira_xlsx)
            
            # Adicionar coluna ao DataFrame original IN-PLACE
            carteira_xlsx['dias_atraso'] = carteira_xlsx_enriched['dias_atraso']
            
            print(f"✅ ENRIQUECIMENTO: Campo 'dias_atraso' adicionado ao XLSX global")
        
        # ENRIQUECIMENTO PROGRESSIVO 2: Adicionar grupo_de_risco ao DataFrame GLOBAL
        if 'grupo_de_risco' not in carteira_xlsx.columns:
            # Obter configuração PDD para classificação
            pdd_grupos = _find_pdd_config(config)
            
            if pdd_grupos:
                # Função para classificar cada título em um grupo de risco
                def classificar_grupo_risco(dias):
                    for grupo, params in sorted(pdd_grupos.items()):
                        if dias <= params['atraso_max_dias']:
                            return grupo
                    return 'H'  # Grupo mais alto por default
                
                # Aplicar classificação para TODA a carteira
                carteira_xlsx['grupo_de_risco'] = carteira_xlsx['dias_atraso'].apply(classificar_grupo_risco)
                
                print(f"✅ ENRIQUECIMENTO: Campo 'grupo_de_risco' adicionado ao XLSX global")
            else:
                print(f"⚠️ Configuração PDD não encontrada - grupo_de_risco não adicionado")
        
        # Filtrar apenas dados do pool atual para cálculos de monitoramento
        pool_xlsx = carteira_xlsx[carteira_xlsx['pool'] == config.get('pool_id', '')]
        
        if pool_xlsx.empty:
            # Tentar com pool_name se pool_id não funcionar
            pool_name = config.get('pool_name', config.get('pool_id', ''))
            pool_xlsx = carteira_xlsx[carteira_xlsx['pool'] == pool_name]
        
        # Resultado base
        resultado = {
            "sucesso": True,
            "monitor": "inadimplencia",
            "pool_id": config.get('pool_id', 'desconhecido'),
            "data_analise": datetime.now().isoformat(),
            "pl_pool": float(pool_data_csv['pl'].iloc[0] if 'pl' in pool_data_csv.columns else pool_data_csv['PL'].iloc[0]),
            "enriquecimento": {
                "dias_atraso_adicionado": 'dias_atraso' in carteira_xlsx.columns,
                "grupo_de_risco_adicionado": 'grupo_de_risco' in carteira_xlsx.columns,
                "registros_pool": len(pool_xlsx),
                "registros_total_xlsx": len(carteira_xlsx)
            }
        }
        
        # Processar cada janela configurada (usando dados do pool específico)
        monitores = _find_delinquency_monitors(config)
        for monitor in monitores:
            window = monitor['limites']['prazo_dias']
            limite = monitor['limites']['limite']
            key = f"inadimplencia_{window}d"
            
            resultado[key] = calculate_delinquency_by_window(
                pool_xlsx,  # Usar dados filtrados por pool
                pool_data_csv,
                window,
                limite
            )
        
        # Análise de PDD movida para monitor_pdd.py (execução separada)
        
        # Adicionar análise de aging (usando dados do pool específico)
        resultado['aging_analysis'] = generate_aging_analysis(pool_xlsx)
        
        return resultado
        
    except Exception as e:
        return {
            "sucesso": False,
            "monitor": "inadimplencia",
            "erro": str(e),
            "tipo_erro": type(e).__name__
        }


if __name__ == "__main__":
    # Exemplo de uso para testes
    print("Monitor de Inadimplência carregado com sucesso")
    print("Use run_delinquency_monitoring() como interface principal")