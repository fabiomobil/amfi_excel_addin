"""
Data Validator - Validação de qualidade de dados
Sistema AmFi - Verificação de integridade e consistência
"""

import pandas as pd
import logging
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Colunas obrigatórias por tipo de arquivo
REQUIRED_CSV_COLUMNS = [
    'Nome', 'PL', 'SR', 'JR', 'Carteira', 'I.S.', 
    'Status do Pool', 'Tipo de Produto'
]

REQUIRED_XLSX_COLUMNS = [
    'Pool', 'Nome do Sacado', 'Nome do Cedente', 
    'Valor presente (R$)', 'Data de aquisição'
]

# Thresholds de validação
VALIDATION_THRESHOLDS = {
    'min_pools': 5,  # Mínimo de pools esperados
    'min_assets': 100,  # Mínimo de ativos na carteira
    'max_empty_values_percent': 10,  # % máximo de valores vazios
    'max_pl_change_percent': 50,  # Mudança máxima de PL entre dias
}


def validate_csv_structure(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Valida estrutura do arquivo CSV
    
    Args:
        df: DataFrame do CSV
        
    Returns:
        Dicionário com resultados da validação
    """
    results = {
        'valid': True,
        'missing_columns': [],
        'warnings': [],
        'errors': []
    }
    
    # Verificar colunas obrigatórias
    missing = [col for col in REQUIRED_CSV_COLUMNS if col not in df.columns]
    if missing:
        results['valid'] = False
        results['missing_columns'] = missing
        results['errors'].append(f"Colunas obrigatórias ausentes: {', '.join(missing)}")
    
    # Verificar quantidade de pools
    if len(df) < VALIDATION_THRESHOLDS['min_pools']:
        results['warnings'].append(
            f"Poucos pools encontrados: {len(df)} (esperado: >{VALIDATION_THRESHOLDS['min_pools']})"
        )
    
    # Verificar valores vazios
    for col in ['Nome', 'PL', 'Status do Pool']:
        if col in df.columns:
            empty_count = df[col].isna().sum()
            empty_percent = (empty_count / len(df)) * 100
            if empty_percent > VALIDATION_THRESHOLDS['max_empty_values_percent']:
                results['warnings'].append(
                    f"Coluna '{col}' com {empty_percent:.1f}% valores vazios"
                )
    
    # Verificar tipos de dados
    if 'PL' in df.columns:
        try:
            # Tentar converter PL para numérico
            df['PL'].apply(lambda x: float(str(x).replace('R$', '').replace('.', '').replace(',', '.')))
        except:
            results['errors'].append("Coluna PL contém valores não numéricos")
            results['valid'] = False
    
    return results


def validate_xlsx_structure(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Valida estrutura do arquivo XLSX
    
    Args:
        df: DataFrame do XLSX
        
    Returns:
        Dicionário com resultados da validação
    """
    results = {
        'valid': True,
        'missing_columns': [],
        'warnings': [],
        'errors': []
    }
    
    # Verificar colunas obrigatórias
    missing = [col for col in REQUIRED_XLSX_COLUMNS if col not in df.columns]
    if missing:
        results['valid'] = False
        results['missing_columns'] = missing
        results['errors'].append(f"Colunas obrigatórias ausentes: {', '.join(missing)}")
    
    # Verificar quantidade de ativos
    if len(df) < VALIDATION_THRESHOLDS['min_assets']:
        results['warnings'].append(
            f"Poucos ativos encontrados: {len(df)} (esperado: >{VALIDATION_THRESHOLDS['min_assets']})"
        )
    
    # Verificar valores vazios em colunas críticas
    critical_columns = ['Pool', 'Valor presente (R$)']
    for col in critical_columns:
        if col in df.columns:
            empty_count = df[col].isna().sum()
            if empty_count > 0:
                results['errors'].append(f"Coluna crítica '{col}' tem {empty_count} valores vazios")
                results['valid'] = False
    
    return results


def validate_data_consistency(csv_df: pd.DataFrame, xlsx_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Valida consistência entre CSV e XLSX
    
    Args:
        csv_df: DataFrame do CSV
        xlsx_df: DataFrame do XLSX
        
    Returns:
        Dicionário com resultados da validação
    """
    results = {
        'valid': True,
        'warnings': [],
        'errors': [],
        'pool_mismatches': []
    }
    
    # Extrair pools únicos de cada arquivo
    csv_pools = set(csv_df['Nome'].dropna().unique()) if 'Nome' in csv_df.columns else set()
    xlsx_pools = set(xlsx_df['Pool'].dropna().unique()) if 'Pool' in xlsx_df.columns else set()
    
    # Verificar pools no CSV sem dados no XLSX
    csv_only = csv_pools - xlsx_pools
    if csv_only:
        results['warnings'].append(f"Pools no CSV sem dados no XLSX: {', '.join(csv_only)}")
        results['pool_mismatches'].extend(list(csv_only))
    
    # Verificar pools no XLSX sem registro no CSV
    xlsx_only = xlsx_pools - csv_pools
    if xlsx_only:
        results['warnings'].append(f"Pools no XLSX sem registro no CSV: {', '.join(xlsx_only)}")
        results['pool_mismatches'].extend(list(xlsx_only))
    
    # Validar totais por pool (se possível)
    common_pools = csv_pools & xlsx_pools
    for pool in common_pools:
        try:
            # Somar valores do XLSX para o pool
            if 'Valor presente (R$)' in xlsx_df.columns:
                xlsx_total = xlsx_df[xlsx_df['Pool'] == pool]['Valor presente (R$)'].sum()
                
                # Buscar valor da carteira no CSV
                if 'Carteira' in csv_df.columns:
                    csv_row = csv_df[csv_df['Nome'] == pool]
                    if not csv_row.empty and pd.notna(csv_row.iloc[0]['Carteira']):
                        csv_carteira = float(str(csv_row.iloc[0]['Carteira'])
                                           .replace('R$', '')
                                           .replace('.', '')
                                           .replace(',', '.'))
                        
                        # Verificar discrepância significativa (>5%)
                        if abs(xlsx_total - csv_carteira) / csv_carteira > 0.05:
                            results['warnings'].append(
                                f"Pool '{pool}': discrepância entre CSV (R$ {csv_carteira:,.2f}) "
                                f"e XLSX (R$ {xlsx_total:,.2f})"
                            )
        except Exception as e:
            logger.warning(f"Erro ao validar totais do pool {pool}: {str(e)}")
    
    return results


def compare_with_previous_day(
    current_csv: pd.DataFrame, 
    previous_csv: Optional[pd.DataFrame]
) -> Dict[str, Any]:
    """
    Compara dados atuais com dia anterior
    
    Args:
        current_csv: DataFrame atual
        previous_csv: DataFrame do dia anterior (opcional)
        
    Returns:
        Dicionário com mudanças detectadas
    """
    results = {
        'new_pools': [],
        'removed_pools': [],
        'significant_changes': [],
        'warnings': []
    }
    
    if previous_csv is None or previous_csv.empty:
        results['warnings'].append("Sem dados do dia anterior para comparação")
        return results
    
    # Comparar pools
    current_pools = set(current_csv['Nome'].dropna().unique()) if 'Nome' in current_csv.columns else set()
    previous_pools = set(previous_csv['Nome'].dropna().unique()) if 'Nome' in previous_csv.columns else set()
    
    results['new_pools'] = list(current_pools - previous_pools)
    results['removed_pools'] = list(previous_pools - current_pools)
    
    # Verificar mudanças significativas de PL
    common_pools = current_pools & previous_pools
    for pool in common_pools:
        try:
            current_pl = _extract_pl_value(current_csv[current_csv['Nome'] == pool].iloc[0]['PL'])
            previous_pl = _extract_pl_value(previous_csv[previous_csv['Nome'] == pool].iloc[0]['PL'])
            
            if previous_pl > 0:
                change_percent = abs(current_pl - previous_pl) / previous_pl * 100
                if change_percent > VALIDATION_THRESHOLDS['max_pl_change_percent']:
                    results['significant_changes'].append({
                        'pool': pool,
                        'previous_pl': previous_pl,
                        'current_pl': current_pl,
                        'change_percent': change_percent
                    })
        except:
            pass
    
    return results


def _extract_pl_value(pl_str: Any) -> float:
    """Extrai valor numérico de string PL"""
    if pd.isna(pl_str):
        return 0.0
    try:
        return float(str(pl_str).replace('R$', '').replace('.', '').replace(',', '.'))
    except:
        return 0.0


def generate_validation_report(
    csv_path: str, 
    xlsx_path: str,
    previous_csv_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Gera relatório completo de validação
    
    Args:
        csv_path: Caminho do CSV atual
        xlsx_path: Caminho do XLSX atual
        previous_csv_path: Caminho do CSV anterior (opcional)
        
    Returns:
        Relatório completo de validação
    """
    report = {
        'timestamp': datetime.now().isoformat(),
        'files': {
            'csv': csv_path,
            'xlsx': xlsx_path
        },
        'validations': {},
        'overall_status': 'VALID',
        'summary': []
    }
    
    try:
        # Carregar arquivos
        from cache_manager import load_csv_cached, load_xlsx_cached
        csv_df = load_csv_cached(csv_path)
        xlsx_df = load_xlsx_cached(xlsx_path)
        
        # Validar estruturas
        csv_validation = validate_csv_structure(csv_df)
        xlsx_validation = validate_xlsx_structure(xlsx_df)
        
        report['validations']['csv_structure'] = csv_validation
        report['validations']['xlsx_structure'] = xlsx_validation
        
        # Validar consistência
        consistency = validate_data_consistency(csv_df, xlsx_df)
        report['validations']['consistency'] = consistency
        
        # Comparar com dia anterior se disponível
        if previous_csv_path:
            try:
                previous_df = load_csv_cached(previous_csv_path)
                comparison = compare_with_previous_day(csv_df, previous_df)
                report['validations']['daily_comparison'] = comparison
            except:
                report['validations']['daily_comparison'] = {
                    'warnings': ['Não foi possível carregar dados do dia anterior']
                }
        
        # Determinar status geral
        all_errors = []
        all_warnings = []
        
        for validation in report['validations'].values():
            if 'errors' in validation:
                all_errors.extend(validation['errors'])
            if 'warnings' in validation:
                all_warnings.extend(validation['warnings'])
        
        if all_errors:
            report['overall_status'] = 'INVALID'
            report['summary'] = all_errors
        elif all_warnings:
            report['overall_status'] = 'WARNING'
            report['summary'] = all_warnings
        else:
            report['overall_status'] = 'VALID'
            report['summary'] = ['Todos os dados validados com sucesso']
        
    except Exception as e:
        report['overall_status'] = 'ERROR'
        report['summary'] = [f"Erro na validação: {str(e)}"]
    
    return report