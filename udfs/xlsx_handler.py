"""
Enhanced XLSX Handler - Targeted pool and status filtering
Sistema AmFi - Processamento otimizado de carteiras
"""

import pandas as pd
import logging
from typing import List, Optional, Any
from datetime import datetime
from cache_manager import load_xlsx_cached, auto_clear_daily_cache
from file_discovery import get_latest_xlsx, get_xlsx_by_date, extract_file_date

logger = logging.getLogger(__name__)

# Status column detection patterns
STATUS_COLUMN_PATTERNS = [
    'Status',
    'status', 
    'Status do Ativo',
    'Situação',
    'situacao',
    'Vencimento Status',
    'Due Status'
]

def _detect_status_column(df: pd.DataFrame) -> Optional[str]:
    """
    Detecta coluna de status no DataFrame
    
    Args:
        df: DataFrame do XLSX
        
    Returns:
        Nome da coluna de status ou None
    """
    for pattern in STATUS_COLUMN_PATTERNS:
        for col in df.columns:
            if pattern.lower() in col.lower():
                return col
    return None


def _get_unique_status_values(df: pd.DataFrame, status_col: str) -> List[str]:
    """
    Obter valores únicos de status
    
    Args:
        df: DataFrame
        status_col: Nome da coluna de status
        
    Returns:
        Lista de valores únicos de status
    """
    if status_col not in df.columns:
        return []
    
    return [str(val) for val in df[status_col].dropna().unique() if val != '']


def _filter_by_pool(df: pd.DataFrame, pool_name: str) -> pd.DataFrame:
    """
    Filtra DataFrame por pool específico
    
    Args:
        df: DataFrame completo
        pool_name: Nome do pool para filtrar
        
    Returns:
        DataFrame filtrado
    """
    if 'Pool' not in df.columns:
        raise ValueError("Coluna 'Pool' não encontrada no arquivo")
    
    # Filter by pool (case insensitive)
    pool_filter = df['Pool'].str.lower() == pool_name.lower()
    filtered_df = df[pool_filter].copy()
    
    if filtered_df.empty:
        available_pools = df['Pool'].dropna().unique()
        raise ValueError(f"Pool '{pool_name}' não encontrado. Pools disponíveis: {', '.join(available_pools)}")
    
    return filtered_df


def _filter_by_status(df: pd.DataFrame, status_value: str, status_col: str) -> pd.DataFrame:
    """
    Filtra DataFrame por status específico
    
    Args:
        df: DataFrame
        status_value: Valor do status para filtrar
        status_col: Nome da coluna de status
        
    Returns:
        DataFrame filtrado
    """
    if status_col not in df.columns:
        return df
    
    # Filter by status (case insensitive)
    status_filter = df[status_col].astype(str).str.lower() == status_value.lower()
    filtered_df = df[status_filter].copy()
    
    if filtered_df.empty:
        available_statuses = _get_unique_status_values(df, status_col)
        raise ValueError(f"Status '{status_value}' não encontrado. Status disponíveis: {', '.join(available_statuses)}")
    
    return filtered_df


def _select_columns_by_view(df: pd.DataFrame, visao: str) -> pd.DataFrame:
    """
    Seleciona colunas baseado no tipo de visão
    
    Args:
        df: DataFrame
        visao: 'exec' para colunas executivas, 'full' para todas
        
    Returns:
        DataFrame com colunas selecionadas
    """
    if visao.lower() == 'exec':
        # Colunas executivas essenciais
        exec_columns = [
            'Pool', 'Nome do Sacado', 'Nome do Cedente', 
            'Valor presente (R$)', 'Data de aquisição', 'Vencimento'
        ]
        
        # Adicionar coluna de status se detectada
        status_col = _detect_status_column(df)
        if status_col:
            exec_columns.append(status_col)
        
        # Filtrar apenas colunas que existem
        available_columns = [col for col in exec_columns if col in df.columns]
        return df[available_columns].copy()
    
    else:  # 'full'
        return df.copy()


def _add_file_date_column(df: pd.DataFrame, file_path: str) -> pd.DataFrame:
    """
    Adiciona coluna com data do arquivo como primeira coluna
    
    Args:
        df: DataFrame
        file_path: Caminho do arquivo
        
    Returns:
        DataFrame com coluna de data adicionada
    """
    file_date = extract_file_date(file_path)
    
    # Use the actual datetime object instead of string
    if file_date:
        date_value = file_date  # Keep as datetime for proper Excel formatting
    else:
        date_value = 'Unknown'
    
    # Adicionar como primeira coluna
    df_with_date = df.copy()
    df_with_date.insert(0, 'Data do Arquivo', date_value)
    
    return df_with_date


def _convert_to_excel_format(df: pd.DataFrame) -> List[List]:
    """
    Converte DataFrame para formato Excel preservando tipos de dados
    
    Args:
        df: DataFrame processado
        
    Returns:
        Lista de listas para Excel
    """
    if df.empty:
        return [["Nenhum dado encontrado"]]
    
    # Primeiro, converter tipos de dados das colunas relevantes
    df_typed = _convert_column_types(df.copy())
    
    # Converter para lista de listas preservando tipos
    result = [df_typed.columns.tolist()]  # Headers
    
    for _, row in df_typed.iterrows():
        row_data = []
        for col_name, value in row.items():
            if pd.isna(value):
                row_data.append(None)  # Use None instead of empty string for Excel
            elif isinstance(value, pd.Timestamp):
                # Convert pandas Timestamp to Python datetime for Excel
                row_data.append(value.to_pydatetime())
            elif isinstance(value, (int, float)):
                # Keep numeric values as numbers
                row_data.append(value)
            else:
                # Convert to string only if necessary
                row_data.append(str(value))
        result.append(row_data)
    
    return result


def _convert_column_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converte tipos de dados das colunas para os tipos apropriados
    
    Args:
        df: DataFrame original
        
    Returns:
        DataFrame com tipos convertidos
    """
    df_converted = df.copy()
    
    # Define patterns for different column types
    date_columns = ['data de aquisição', 'vencimento', 'data do arquivo', 'dt. aquisicao']
    value_columns = ['valor presente (r$)', 'valor presente', 'valor']
    
    for col in df_converted.columns:
        col_lower = col.lower()
        
        # Convert date columns
        if any(pattern in col_lower for pattern in date_columns):
            df_converted[col] = pd.to_datetime(df_converted[col], errors='coerce')
        
        # Convert financial value columns
        elif any(pattern in col_lower for pattern in value_columns):
            # Clean and convert financial values
            df_converted[col] = df_converted[col].apply(_clean_financial_value)
    
    return df_converted


def _clean_financial_value(value):
    """
    Limpa e converte valores financeiros para números
    
    Args:
        value: Valor a ser convertido
        
    Returns:
        Valor numérico ou None se não for possível converter
    """
    if pd.isna(value) or value == '' or str(value).lower() in ['nan', 'none', 'null']:
        return None
    
    try:
        # Convert to string and clean
        clean_value = str(value).strip()
        
        # Remove financial symbols
        clean_value = clean_value.replace('R$', '').replace('$', '').replace('€', '').replace('£', '')
        clean_value = clean_value.replace('%', '').strip()
        
        if not clean_value:
            return None
        
        # Handle Brazilian number format
        if '.' in clean_value and ',' in clean_value:
            # Format: 1.234,56 -> 1234.56
            clean_value = clean_value.replace('.', '').replace(',', '.')
        elif ',' in clean_value and '.' not in clean_value:
            # Format: 1234,56 -> 1234.56
            clean_value = clean_value.replace(',', '.')
        
        # Convert to float
        return float(clean_value)
        
    except (ValueError, TypeError):
        return None


def _group_and_aggregate(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrupa dados por entidades e soma valores, preservando outras informações
    
    Args:
        df: DataFrame com dados individuais
        
    Returns:
        DataFrame agrupado com valores somados
    """
    if df.empty:
        return df
    
    try:
        # Criar cópia do DataFrame para manipulação
        df_work = df.copy()
        
        # Identificar colunas de agrupamento e valor
        grouping_cols = []
        value_cols = []
        date_cols = []
        
        for col in df_work.columns:
            col_lower = col.lower()
            
            # Colunas para agrupar (entidades e classificações)
            if any(term in col_lower for term in ['pool', 'nome do sacado', 'nome do cedente', 'status']):
                grouping_cols.append(col)
            
            # Colunas de valor para somar
            elif any(term in col_lower for term in ['valor presente', 'valor']):
                value_cols.append(col)
            
            # Colunas de data para agregar (min/max)
            elif any(term in col_lower for term in ['data de aquisição', 'vencimento']):
                date_cols.append(col)
        
        # Se não temos colunas de agrupamento ou valor, retornar original
        if not grouping_cols or not value_cols:
            return df
        
        # Handle None/NaN values in ALL columns before grouping
        for col in df_work.columns:
            if col in grouping_cols:
                # For grouping columns, replace None/NaN with empty string
                df_work[col] = df_work[col].fillna('').astype(str)
            elif col in value_cols:
                # For value columns, clean and convert to numeric
                df_work[col] = df_work[col].apply(_clean_financial_value)
            elif col in date_cols:
                # For date columns, keep as-is (pandas will handle NaT properly)
                pass
            else:
                # For other columns, convert to string
                df_work[col] = df_work[col].fillna('').astype(str)
        
        # Prepare aggregation dictionary
        agg_dict = {}
        
        # Sum value columns
        for col in value_cols:
            agg_dict[col] = 'sum'
        
        # Aggregate dates
        for col in date_cols:
            if 'aquisição' in col.lower() or 'aquisicao' in col.lower():
                agg_dict[col] = 'min'  # First acquisition
            elif 'vencimento' in col.lower():
                agg_dict[col] = 'max'  # Last maturity
            else:
                agg_dict[col] = 'first'
        
        # Keep other columns (take first value)
        other_cols = [col for col in df_work.columns if col not in grouping_cols + value_cols + date_cols]
        for col in other_cols:
            agg_dict[col] = 'first'
        
        # Perform grouping with dropna=False to include None/empty values
        grouped_df = df_work.groupby(grouping_cols, as_index=False, dropna=False).agg(agg_dict)
        
        # Maintain original column order
        original_order = [col for col in df_work.columns if col in grouped_df.columns]
        grouped_df = grouped_df[original_order]
        
        return grouped_df
        
    except Exception as e:
        # If grouping fails, return original data
        logger.error(f"Erro no agrupamento: {str(e)}")
        return df


def _apply_default_ordering(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica ordenação padrão ao DataFrame
    
    Ordem:
    1. Status (com 'atrasada' primeiro)
    2. Vencimento
    3. Valor presente
    4. Nome do Cedente
    5. Nome do Sacado
    
    Args:
        df: DataFrame para ordenar
        
    Returns:
        DataFrame ordenado
    """
    if df.empty:
        return df
    
    try:
        df_sorted = df.copy()
        
        # Find column names (case-insensitive match)
        status_col = None
        vencimento_col = None
        valor_col = None
        cedente_col = None
        sacado_col = None
        
        for col in df_sorted.columns:
            col_lower = col.lower()
            
            if status_col is None and 'status' in col_lower:
                status_col = col
            elif vencimento_col is None and 'vencimento' in col_lower:
                vencimento_col = col
            elif valor_col is None and 'valor presente' in col_lower:
                valor_col = col
            elif cedente_col is None and 'nome do cedente' in col_lower:
                cedente_col = col
            elif sacado_col is None and 'nome do sacado' in col_lower:
                sacado_col = col
        
        # Build sorting columns list
        sort_columns = []
        ascending_flags = []
        
        # Handle status column with custom sorting for 'atrasada' first
        if status_col:
            # Create a custom sort key for status
            df_sorted['_status_sort_key'] = df_sorted[status_col].apply(
                lambda x: 0 if str(x).lower() == 'atrasada' else 1
            )
            sort_columns.append('_status_sort_key')
            ascending_flags.append(True)
            
            # Then sort by actual status value
            sort_columns.append(status_col)
            ascending_flags.append(True)
        
        # Add other columns in order
        if vencimento_col:
            sort_columns.append(vencimento_col)
            ascending_flags.append(True)  # Earlier dates first
            
        if valor_col:
            sort_columns.append(valor_col)
            ascending_flags.append(False)  # Higher values first
            
        if cedente_col:
            sort_columns.append(cedente_col)
            ascending_flags.append(True)  # Alphabetical
            
        if sacado_col:
            sort_columns.append(sacado_col)
            ascending_flags.append(True)  # Alphabetical
        
        # Apply sorting if we have any columns to sort by
        if sort_columns:
            df_sorted = df_sorted.sort_values(
                by=sort_columns,
                ascending=ascending_flags,
                na_position='last'
            )
            
            # Remove temporary sort column if it was added
            if '_status_sort_key' in df_sorted.columns:
                df_sorted = df_sorted.drop('_status_sort_key', axis=1)
        
        return df_sorted
        
    except Exception as e:
        # If sorting fails, return original data
        logger.error(f"Erro na ordenação: {str(e)}")
        return df


class EnhancedAmfiXLSXLogic:
    """
    Lógica aprimorada para processamento de XLSX com filtros específicos
    """
    
    @staticmethod
    def execute(pool_name: str, status: Optional[str] = None, 
                date: Optional[str] = None, visao: str = 'exec', group_by: bool = False) -> List[List]:
        """
        Executa processamento aprimorado de XLSX
        
        Args:
            pool_name: Nome do pool (obrigatório)
            status: Status para filtrar (opcional)
            date: Data específica YYYY-MM-DD (opcional, usa mais recente se não fornecido)
            visao: 'exec' ou 'full'
            group_by: True para agrupar e somar por entidades (opcional)
            
        Returns:
            Lista de listas formatada para Excel
        """
        try:
            # Auto-clear cache if new day
            auto_clear_daily_cache()
            
            # 1. Determinar arquivo a ser usado
            if date:
                file_path = get_xlsx_by_date(date)
                if not file_path:
                    return [["Erro", f"Arquivo XLSX não encontrado para data: {date}"]]
            else:
                file_path = get_latest_xlsx()
                if not file_path:
                    return [["Erro", "Nenhum arquivo XLSX encontrado"]]
            
            # 2. Carregar dados com cache
            df = load_xlsx_cached(file_path)
            
            if df.empty:
                return [["Erro", "Arquivo XLSX está vazio"]]
            
            # 3. Filtrar por pool
            df_filtered = _filter_by_pool(df, pool_name)
            
            # 4. Detectar coluna de status
            status_col = _detect_status_column(df_filtered)
            
            # 5. Filtrar por status se fornecido
            if status and status_col:
                df_filtered = _filter_by_status(df_filtered, status, status_col)
            elif status and not status_col:
                return [["Aviso", f"Status '{status}' solicitado mas coluna de status não encontrada"]]
            
            # 6. Selecionar colunas baseado na visão
            df_final = _select_columns_by_view(df_filtered, visao)
            
            # 7. Adicionar data do arquivo como primeira coluna
            df_with_date = _add_file_date_column(df_final, file_path)
            
            # 7.5. Agrupar dados se solicitado
            if group_by:
                df_with_date = _group_and_aggregate(df_with_date)
            
            # 7.6. Aplicar ordenação padrão
            df_ordered = _apply_default_ordering(df_with_date)
            
            # 8. Converter para formato Excel
            result = _convert_to_excel_format(df_ordered)
            
            # Log de informações
            logger.info(f"Processado XLSX: {pool_name}, status={status}, "
                       f"registros={len(df_ordered)}, arquivo={file_path}")
            
            return result
            
        except ValueError as e:
            return [["Erro de Validação", str(e)]]
        except Exception as e:
            logger.error(f"Erro no processamento XLSX: {str(e)}")
            return [["Erro", f"Erro no processamento: {str(e)}"]]
    
    @staticmethod
    def get_available_pools(date: Optional[str] = None) -> List[List]:
        """
        Retorna lista de pools disponíveis
        
        Args:
            date: Data específica (opcional)
            
        Returns:
            Lista de pools únicos
        """
        try:
            # Determinar arquivo
            if date:
                file_path = get_xlsx_by_date(date)
            else:
                file_path = get_latest_xlsx()
                
            if not file_path:
                return [["Erro", "Arquivo XLSX não encontrado"]]
            
            # Carregar dados
            df = load_xlsx_cached(file_path)
            
            if 'Pool' not in df.columns:
                return [["Erro", "Coluna 'Pool' não encontrada"]]
            
            # Obter pools únicos
            pools = sorted(df['Pool'].dropna().unique())
            
            # Formatar para Excel
            result = [["Pool"]]
            for pool in pools:
                result.append([str(pool)])
            
            return result
            
        except Exception as e:
            return [["Erro", str(e)]]
    
    @staticmethod
    def get_available_statuses(pool_name: str, date: Optional[str] = None) -> List[List]:
        """
        Retorna status disponíveis para um pool
        
        Args:
            pool_name: Nome do pool
            date: Data específica (opcional)
            
        Returns:
            Lista de status únicos
        """
        try:
            # Determinar arquivo
            if date:
                file_path = get_xlsx_by_date(date)
            else:
                file_path = get_latest_xlsx()
                
            if not file_path:
                return [["Erro", "Arquivo XLSX não encontrado"]]
            
            # Carregar e filtrar dados
            df = load_xlsx_cached(file_path)
            df_pool = _filter_by_pool(df, pool_name)
            
            # Detectar coluna de status
            status_col = _detect_status_column(df_pool)
            if not status_col:
                return [["Aviso", "Coluna de status não encontrada"]]
            
            # Obter status únicos
            statuses = _get_unique_status_values(df_pool, status_col)
            
            # Formatar para Excel
            result = [["Status"]]
            for status in sorted(statuses):
                result.append([str(status)])
            
            return result
            
        except Exception as e:
            return [["Erro", str(e)]]