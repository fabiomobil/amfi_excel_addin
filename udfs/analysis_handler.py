# analysis_handler.py
"""
Handler para análises de concentração e risco
Sistema AmFi - Análise de Fundos de Investimento

Módulo otimizado para performance em carteiras grandes (1000+ ativos)
com foco em escalabilidade e manutenibilidade.
"""

import pandas as pd
import numpy as np
import re
from typing import List, Dict, Any, Optional, Union
import logging

# Configuração de logging
logger = logging.getLogger(__name__)

# Importações com fallback robusto
try:
    from cache_manager import load_xlsx_cached
except ImportError:
    logger.warning("cache_manager não encontrado - fallback para pandas direto")
    def load_xlsx_cached(file_path): 
        return pd.read_excel(file_path)

# ==================== CONSTANTES ====================

# Colunas obrigatórias para análises
REQUIRED_COLUMNS = {
    'valor': 'Valor presente (R$)',
    'pool': 'Pool',
    'sacado': 'Nome do Sacado', 
    'cedente': 'Nome do Cedente',
    'loan_id': 'loan_id'  # Opcional - pode não existir
}

# Tipos de análise suportados
VALID_ANALYSIS_TYPES = {'sacado', 'cedente', None}

# Cabeçalhos padrão dos resultados
STANDARD_HEADERS = ["Empresa", "Valor", "Percentual", "Espaço/Excesso", "Status"]
COMBINED_HEADERS = ["Cedente/Sacado", "Valor", "Percentual", "Espaço/Excesso", "Status"]


# ==================== FUNÇÃO PRINCIPAL ====================

def process_concentracao(arquivo_xlsx: str, pool: str, pl_total: float, 
                        tipo: Optional[str] = None, top: Optional[str] = None, 
                        limite: Optional[str] = None, ignore_list: Any = None) -> List[List[Any]]:
    """
    Processa análise de concentração com monitoramento de limites.
    
    Função principal otimizada para performance em carteiras grandes.
    Utiliza operações vetorizadas pandas e cache automático.
    
    Args:
        arquivo_xlsx: Caminho do arquivo XLSX
        pool: Nome do pool para filtrar
        pl_total: Valor total do PL para cálculo de percentuais (> 0)
        tipo: 'sacado', 'cedente' ou None (combinado)
        top: String 'top=X' ou número para limitar resultados
        limite: String 'individual=10,top3=30' para monitoramento
        ignore_list: String, range Excel ou lista de entidades
    
    Returns:
        Lista de listas formatada para Excel
        
    Raises:
        Retorna lista de erro formatada em caso de falha
    """
    try:
        # 1. Validação rápida de parâmetros críticos
        error = _validate_input_parameters(pl_total, tipo)
        if error:
            return error
        
        # 2. Carregamento otimizado com cache
        df = _load_and_validate_data(arquivo_xlsx, pool)
        if isinstance(df, list):  # É uma mensagem de erro
            return df
        
        # 3. Parsing de parâmetros de configuração
        top_limit = _parse_top_parameter(top)
        limite_config = _parse_limite_parameters(limite)
        
        # 4. Aplicação de filtros de exclusão
        df_filtered = _apply_ignore_filters(df, ignore_list, tipo)
        
        # 5. Execução da análise de concentração
        return _execute_concentration_analysis(
            df_filtered, tipo, pl_total, top_limit, limite_config
        )
        
    except Exception as e:
        logger.error(f"Erro crítico em process_concentracao: {e}", exc_info=True)
        return [["Erro", f"Falha na análise: {str(e)}", "", "", ""]]


# ==================== VALIDAÇÃO E CARREGAMENTO ====================

def _validate_input_parameters(pl_total: float, tipo: Optional[str]) -> Optional[List[List[str]]]:
    """Validação rápida de parâmetros de entrada."""
    if not isinstance(pl_total, (int, float)) or pl_total <= 0:
        return [["Erro", "PL deve ser um número maior que zero", "", "", ""]]
    
    if tipo is not None and tipo not in VALID_ANALYSIS_TYPES:
        valid_types = [t for t in VALID_ANALYSIS_TYPES if t is not None]
        return [["Erro", f"Tipo inválido. Use: {', '.join(valid_types)} ou deixe vazio", "", "", ""]]
    
    return None


def _load_and_validate_data(arquivo_xlsx: str, pool: str) -> Union[pd.DataFrame, List[List[str]]]:
    """
    Carrega dados com cache e validação completa.
    
    Retorna DataFrame válido ou lista de erro formatada.
    """
    try:
        # Carregamento com cache automático
        df = load_xlsx_cached(arquivo_xlsx)
        
        if df is None or df.empty:
            return [["Erro", f"Arquivo '{arquivo_xlsx}' não encontrado ou vazio", "", "", ""]]
        
        # Validação de estrutura obrigatória
        missing_cols = [
            col for col_key, col in REQUIRED_COLUMNS.items() 
            if col_key != 'loan_id' and col not in df.columns
        ]
        
        if missing_cols:
            return [["Erro", f"Colunas obrigatórias ausentes: {', '.join(missing_cols)}", "", "", ""]]
        
        # Filtro por pool com otimização
        if pool and pool.strip():
            pool_mask = df[REQUIRED_COLUMNS['pool']].astype(str).str.lower() == pool.lower()
            df_pool = df[pool_mask].copy()
            
            if df_pool.empty:
                return [["Erro", f"Pool '{pool}' não encontrado no arquivo", "", "", ""]]
            
            return df_pool
        
        return df
        
    except FileNotFoundError:
        return [["Erro", f"Arquivo não encontrado: {arquivo_xlsx}", "", "", ""]]
    except Exception as e:
        logger.error(f"Erro ao carregar dados: {e}")
        return [["Erro", f"Falha ao processar arquivo: {str(e)}", "", "", ""]]


# ==================== FILTROS DE EXCLUSÃO ====================

def _apply_ignore_filters(df: pd.DataFrame, ignore_list: Any, tipo: Optional[str]) -> pd.DataFrame:
    """
    Aplica filtros de exclusão com performance otimizada.
    
    Utiliza operações vetorizadas para máxima eficiência.
    """
    if not ignore_list:
        return df
    
    try:
        entities_to_ignore = _parse_ignore_list(ignore_list)
        if not entities_to_ignore:
            return df
        
        # Determinar coluna alvo baseada no tipo de análise
        target_column = _get_target_column_for_ignore(tipo)
        
        if target_column not in df.columns:
            logger.warning(f"Coluna '{target_column}' não encontrada - ignorando filtro")
            return df
        
        # Filtro otimizado com case-insensitive matching
        entities_lower = [entity.lower() for entity in entities_to_ignore]
        mask = ~df[target_column].astype(str).str.lower().isin(entities_lower)
        
        df_filtered = df[mask].copy()
        
        removed_count = len(df) - len(df_filtered)
        if removed_count > 0:
            logger.info(f"Filtro ignore aplicado: {removed_count} registros removidos")
        
        return df_filtered
        
    except Exception as e:
        logger.warning(f"Erro ao aplicar filtros de exclusão: {e}")
        return df  # Retorna original em caso de erro


def _get_target_column_for_ignore(tipo: Optional[str]) -> str:
    """Determina coluna alvo para ignore_list baseada no tipo."""
    if tipo == "sacado":
        return REQUIRED_COLUMNS['sacado']
    else:  # 'cedente' ou None (padrão: cedente)
        return REQUIRED_COLUMNS['cedente']


def _parse_ignore_list(ignore_list: Any) -> List[str]:
    """
    Parser robusto para ignore_list com suporte a múltiplos formatos.
    
    Suporta strings, ranges Excel e listas Python.
    """
    if not ignore_list:
        return []
    
    entities = set()  # Set para eliminação automática de duplicatas
    
    try:
        if isinstance(ignore_list, str):
            # String simples ou separada por pipe
            entities.update(item.strip() for item in ignore_list.split("|") if item.strip())
        
        elif hasattr(ignore_list, '__iter__'):
            # Range Excel ou lista Python
            for item in ignore_list:
                if item is not None:
                    item_str = str(item).strip()
                    if item_str:
                        # Suporte a pipe dentro de células individuais
                        entities.update(sub.strip() for sub in item_str.split("|") if sub.strip())
        else:
            # Valor único
            item_str = str(ignore_list).strip()
            if item_str:
                entities.add(item_str)
                
    except Exception as e:
        logger.warning(f"Erro ao processar ignore_list: {e}")
    
    return list(entities)


# ==================== PARSERS DE PARÂMETROS ====================

def _parse_top_parameter(top: Optional[str]) -> Optional[int]:
    """Parser flexível para parâmetro top."""
    if not top:
        return None
    
    try:
        if isinstance(top, str):
            if top.startswith("top="):
                return int(top.split("=")[1])
            return int(top)
        return int(top)
    except (ValueError, IndexError, TypeError):
        logger.warning(f"Parâmetro top inválido ignorado: {top}")
        return None


def _parse_limite_parameters(limite: Optional[str]) -> Dict[str, float]:
    """Parser para configuração de limites."""
    if not limite:
        return {}
    
    params = {}
    
    try:
        for part in limite.split(","):
            if "=" in part:
                key, value = part.strip().split("=", 1)
                params[key.strip()] = float(value.strip())
    except (ValueError, IndexError) as e:
        logger.warning(f"Erro ao processar parâmetros de limite '{limite}': {e}")
    
    return params


# ==================== ORQUESTRAÇÃO DE ANÁLISE ====================

def _execute_concentration_analysis(df: pd.DataFrame, tipo: Optional[str], 
                                   pl_total: float, top_limit: Optional[int], 
                                   limite_config: Dict[str, float]) -> List[List[Any]]:
    """Orquestra execução da análise baseada no tipo."""
    if tipo in ['sacado', 'cedente']:
        return _analyze_single_entity_concentration(
            df, tipo, pl_total, top_limit, limite_config
        )
    else:
        return _analyze_combined_concentration(
            df, pl_total, top_limit, limite_config
        )


def _analyze_single_entity_concentration(df: pd.DataFrame, tipo: str, 
                                       pl_total: float, top_limit: Optional[int],
                                       limite_config: Dict[str, float]) -> List[List[Any]]:
    """
    Análise de concentração para entidade única (sacado ou cedente).
    
    Otimizada com operações vetorizadas pandas.
    """
    group_column = REQUIRED_COLUMNS[tipo]
    
    # Agregação otimizada
    concentration = _perform_aggregation(df, group_column)
    
    # Cálculos vetorizados
    concentration = _calculate_percentages_and_sort(concentration, pl_total)
    
    # Aplicar limitação por top
    if top_limit and top_limit > 0:
        concentration = concentration.head(top_limit)
    
    # Análise de limites
    concentration = _apply_limit_analysis(concentration, limite_config, pl_total)
    
    # Construção do resultado
    result = [STANDARD_HEADERS.copy()]
    result.extend(_build_entity_rows(concentration, group_column))
    
    # Linha de total se necessário
    if top_limit and top_limit > 0:
        total_row = _build_total_summary_row(concentration, limite_config, pl_total, top_limit)
        result.append(total_row)
    
    return result


def _analyze_combined_concentration(df: pd.DataFrame, pl_total: float,
                                  top_limit: Optional[int], 
                                  limite_config: Dict[str, float]) -> List[List[Any]]:
    """Análise de concentração combinada cedente/sacado."""
    # Criar chave combinada
    df_work = df.copy()
    combined_key = 'Cedente_Sacado'
    df_work[combined_key] = (
        df_work[REQUIRED_COLUMNS['cedente']] + " / " + df_work[REQUIRED_COLUMNS['sacado']]
    )
    
    # Agregação
    concentration = _perform_aggregation(df_work, combined_key)
    
    # Cálculos
    concentration = _calculate_percentages_and_sort(concentration, pl_total)
    
    # Limitação
    if top_limit and top_limit > 0:
        concentration = concentration.head(top_limit)
    
    # Análise de limites
    concentration = _apply_limit_analysis(concentration, limite_config, pl_total)
    
    # Resultado
    result = [COMBINED_HEADERS.copy()]
    result.extend(_build_entity_rows(concentration, combined_key))
    
    if top_limit and top_limit > 0:
        total_row = _build_total_summary_row(concentration, limite_config, pl_total, top_limit)
        result.append(total_row)
    
    return result


# ==================== OPERAÇÕES DE AGREGAÇÃO ====================

def _perform_aggregation(df: pd.DataFrame, group_column: str) -> pd.DataFrame:
    """Executa agregação otimizada por coluna de agrupamento."""
    agg_dict = {REQUIRED_COLUMNS['valor']: 'sum'}
    
    # Adicionar contagem de loans se coluna existir
    if REQUIRED_COLUMNS['loan_id'] in df.columns:
        agg_dict[REQUIRED_COLUMNS['loan_id']] = 'count'
    
    concentration = df.groupby(group_column).agg(agg_dict).reset_index()
    
    # Calcular contagem se loan_id não existe
    if REQUIRED_COLUMNS['loan_id'] not in df.columns:
        concentration['loan_count'] = df.groupby(group_column).size().values
    else:
        concentration['loan_count'] = concentration[REQUIRED_COLUMNS['loan_id']]
    
    return concentration


def _calculate_percentages_and_sort(df: pd.DataFrame, pl_total: float) -> pd.DataFrame:
    """Calcula percentuais e ordena por valor decrescente."""
    # Cálculo vetorizado de percentuais
    df['Percentual'] = df[REQUIRED_COLUMNS['valor']] / pl_total
    
    # Ordenação otimizada
    return df.sort_values(REQUIRED_COLUMNS['valor'], ascending=False)


# ==================== ANÁLISE DE LIMITES ====================

def _apply_limit_analysis(df: pd.DataFrame, limite_config: Dict[str, float], 
                         pl_total: float) -> pd.DataFrame:
    """
    Aplica análise de limites com cálculos vetorizados.
    """
    df = df.copy()
    
    # Inicialização
    df['Espaco_Excesso'] = 0.0
    df['Status'] = "enquadrado"
    
    # Aplicar limite individual se configurado
    if 'individual' in limite_config:
        individual_limit_pct = limite_config['individual'] / 100
        individual_limit_value = pl_total * individual_limit_pct
        
        # Cálculos vetorizados
        df['Espaco_Excesso'] = individual_limit_value - df[REQUIRED_COLUMNS['valor']]
        df.loc[df[REQUIRED_COLUMNS['valor']] > individual_limit_value, 'Status'] = "violado"
    
    return df


# ==================== CONSTRUÇÃO DE RESULTADOS ====================

def _build_entity_rows(df: pd.DataFrame, entity_column: str) -> List[List[Any]]:
    """Constrói linhas de entidades para o resultado final."""
    rows = []
    for _, row in df.iterrows():
        entity_row = [
            row[entity_column],
            row[REQUIRED_COLUMNS['valor']],
            row['Percentual'],
            row['Espaco_Excesso'],
            row['Status']
        ]
        rows.append(entity_row)
    return rows


def _build_total_summary_row(df: pd.DataFrame, limite_config: Dict[str, float], 
                           pl_total: float, top_num: int) -> List[Any]:
    """Constrói linha de resumo total."""
    total_value = df[REQUIRED_COLUMNS['valor']].sum()
    total_percentage = total_value / pl_total
    
    # Análise de status individual
    has_individual_violations = (df['Status'] == "violado").any()
    individual_status = "individual violado" if has_individual_violations else "individual enquadrado"
    
    # Análise de status agregado
    aggregate_status = "top enquadrado"
    aggregate_excess = 0.0
    
    # Verificar limite agregado específico
    top_limit_key = f"top{top_num}"
    if top_limit_key in limite_config:
        aggregate_limit_pct = limite_config[top_limit_key] / 100
        aggregate_limit_value = pl_total * aggregate_limit_pct
        
        aggregate_excess = aggregate_limit_value - total_value
        
        if total_value > aggregate_limit_value:
            aggregate_status = "top violado"
    
    # Combinação de status
    final_status = _combine_status_messages(individual_status, aggregate_status)
    
    return ["Total", total_value, total_percentage, aggregate_excess, final_status]


def _combine_status_messages(individual_status: str, aggregate_status: str) -> str:
    """Combina mensagens de status individual e agregado."""
    individual_violated = "violado" in individual_status
    aggregate_violated = "violado" in aggregate_status
    
    if individual_violated and aggregate_violated:
        return "ambos violados"
    elif individual_violated:
        return f"top enquadrado, {individual_status}"
    elif aggregate_violated:
        return f"{aggregate_status}, individual enquadrado"
    else:
        return "ambos enquadrados"