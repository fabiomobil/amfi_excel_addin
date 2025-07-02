"""
AmFi - UDFs principais para Excel
Arquivo principal visto pelo xlwings
"""
import xlwings as xw
from typing import List
from csv_handler import AmfiDashboardLogic, ListPoolsLogic
from json_handler import AmFiReadJSONLogic
from cache_manager import (
    clear_all_cache, clear_csv_cache, clear_json_cache, 
    clear_xlsx_cache, get_cache_stats
)
from xlsx_handler import EnhancedAmfiXLSXLogic
from analysis_handler import process_concentracao
from calculus import CalculusLogic
from file_discovery import get_latest_csv_path, get_latest_xlsx_path, check_data_status
from data_validator import generate_validation_report
from udf_cache import cache_udf_result, clear_udf_cache, format_cache_stats

@cache_udf_result(ttl_seconds=60)  # Cache por 60 segundos
@xw.func
@xw.ret(expand='table')
def AmfiDashboard(caminho_arquivo: str, nomes_pool=None, visao: str = 'exec', ignore_list=None) -> List[List]:
    """
    Dashboard AMFI para consulta de oportunidades
    
    Args:
        caminho_arquivo: Caminho do arquivo CSV
        nomes_pool: Pool(s) a serem exibidos (string ou range)
                   Se vazio ou None, retorna TODOS os pools disponíveis
        visao: 'exec' para visão executiva, 'full' para visão completa
        ignore_list: Pool(s) a serem ignorados (string, range Excel ou lista)
                    Suporta: "Pool A", "Pool A|Pool B", range Excel
    
    Exemplos Excel:
        =AmfiDashboard(A1)                    # Todos os pools, visão exec
        =AmfiDashboard(A1, "Pool A")          # Apenas Pool A
        =AmfiDashboard(A1, , "full")          # Todos os pools, visão completa
        =AmfiDashboard(A1, , , "Pool X")      # Todos exceto Pool X
    """
    return AmfiDashboardLogic.execute(caminho_arquivo, nomes_pool, visao, ignore_list)

@xw.func
@xw.ret(expand='table')  
def ListPools(caminho_arquivo: str, ignore_list=None) -> List[List[str]]:
    """
    Lista pools disponíveis ordenados alfabeticamente
    
    Args:
        caminho_arquivo: Caminho do arquivo CSV
        ignore_list: Pool(s) a serem ignorados (string, range Excel ou lista)
                    Suporta: "Pool A", "Pool A|Pool B", range Excel
    """
    return ListPoolsLogic.execute(caminho_arquivo, ignore_list)

@xw.func
@xw.ret(expand='table')
def AmFiReadJSON(caminho_arquivo: str, chave: str) -> List[List[str]]:
    """Lê arquivo JSON e busca chave específica"""
    return AmFiReadJSONLogic.execute(caminho_arquivo, chave)

@cache_udf_result(ttl_seconds=60)  # Cache por 60 segundos
@xw.func
@xw.ret(expand='table')
def AmfiXLSX(pool_name, status_=None, date_=None, visao=None):
    """Consulta dados de ativos/empréstimos filtrados por pool e status"""
    # Set defaults to match expected behavior
    if status_ is None:
        status_ = ""
    if date_ is None:
        date_ = ""
    if visao is None:
        visao = "exec"
    return EnhancedAmfiXLSXLogic.execute(pool_name, status_, date_, visao)


@cache_udf_result(ttl_seconds=120)  # Cache por 2 minutos - análise mais pesada
@xw.func
@xw.ret(expand='table')
def AmfiConcentracao(arquivo_xlsx, pool, pl_total, tipo=None, top=None, limite=None, ignore_list=None):
    """Análise de concentração de sacados, cedentes ou combinado com monitoramento de limites"""
    try:
        return process_concentracao(arquivo_xlsx, pool, pl_total, tipo, top, limite, ignore_list)
    except Exception as e:
        return [["Erro", str(e), "", "", ""]]
    
    
@xw.func
def ClearCache(tipo: str = 'all') -> str:
    """Limpa cache de arquivos carregados"""
    tipo = tipo.lower().strip()
    
    if tipo == 'csv':
        count = clear_csv_cache()
        return f"Cache CSV limpo. {count} arquivos removidos."
    elif tipo == 'json':
        count = clear_json_cache()
        return f"Cache JSON limpo. {count} arquivos removidos."
    elif tipo == 'xlsx':
        count = clear_xlsx_cache()
        return f"Cache XLSX limpo. {count} arquivos removidos."
    else:  # 'all' ou qualquer outro valor
        return clear_all_cache()

@xw.func
def CacheStats() -> str:
    """Retorna estatísticas dos caches de arquivos"""
    stats = get_cache_stats()
    return f"Cache: {stats['total_files']} arquivos (CSV: {stats['csv_files']}, JSON: {stats['json_files']}, XLSX: {stats['xlsx_files']})"

@xw.func
def UDFCacheStats() -> str:
    """Retorna estatísticas do cache de resultados UDF"""
    return format_cache_stats()

@xw.func
def ClearUDFCache(function_name: str = "") -> str:
    """
    Limpa o cache de resultados UDF
    
    Args:
        function_name: Nome da função para limpar (vazio = limpar tudo)
                      Ex: "AmfiDashboard", "AmfiConcentracao"
    """
    if function_name:
        return clear_udf_cache(function_name)
    else:
        return clear_udf_cache(None)

@xw.func
def AmfiCalcularIS(pl: float, jr: float) -> float:
    """Calcula o Índice de Subordinação (IS)"""
    return CalculusLogic.calculate_is(pl, jr)

@xw.func
def AmfiCalcularJR(pl: float, is_percentual: float) -> float:
    """Calcula JR baseado no PL e IS desejado"""
    return CalculusLogic.calculate_jr(pl, is_percentual)

@xw.func
@xw.ret(expand='table')
def AmfiCalcularAdicionalIS(pl_inicial: float, is_atual: float, is_desejado: float):
    """Calcula quanto adicionar ao JR para atingir IS desejado"""
    try:
        resultado = CalculusLogic.calculate_adicional_is(pl_inicial, is_atual, is_desejado)
        
        return [
            ["Descrição", "Valor"],
            ["PL Inicial", resultado['pl_inicial']],
            ["JR Inicial", resultado['jr_inicial']],
            ["SR Inicial", resultado['sr_inicial']], 
            ["IS Inicial (%)", resultado['is_inicial_percentual']],
            ["", ""],
            ["Adicional Necessário", resultado['adicional_x']],
            ["", ""],
            ["JR Final", resultado['jr_final']],
            ["PL Final", resultado['pl_final']], 
            ["SR Final", resultado['sr_final']],
            ["IS Final (%)", resultado['is_final_percentual']]
        ]
    except Exception as e:
        return [["Erro", str(e)]]

@xw.func
def AmfiLatestCSV() -> str:
    """Retorna caminho do arquivo CSV mais recente"""
    return get_latest_csv_path()

@xw.func
def AmfiLatestXLSX() -> str:
    """Retorna caminho do arquivo XLSX mais recente"""
    return get_latest_xlsx_path()

@xw.func
def AmfiDataStatus() -> str:
    """Verifica status e idade dos arquivos de dados"""
    return check_data_status()

# @xw.func
# @xw.ret(expand='table')
# def AmfiGetPools(date="") -> List[List]:
#     """Lista pools disponíveis no arquivo XLSX"""
#     date_param = date if date and date.strip() else None
#     return EnhancedAmfiXLSXLogic.get_available_pools(date_param)

# @xw.func
# @xw.ret(expand='table')
# def AmfiGetStatuses(pool_name: str, date="") -> List[List]:
#     """Lista status disponíveis para um pool específico"""
#     date_param = date if date and date.strip() else None
#     return EnhancedAmfiXLSXLogic.get_available_statuses(pool_name, date_param)

@xw.func
@xw.ret(expand='table')
def AmfiDebugPools(caminho_arquivo: str, nomes_pool=None, ignore_list=None) -> List[List]:
    """
    Debug function to understand pool filtering issues
    """
    try:
        from csv_handler import load_csv_cached, _normalize_pools, _parse_ignore_list
        import pandas as pd
        
        # Load data
        df = load_csv_cached(caminho_arquivo)
        
        # Get all pools from file
        all_pools_in_file = df['Nome'].dropna().unique().tolist()
        
        # Parse inputs
        pools_lista = _normalize_pools(nomes_pool)
        pools_to_ignore = _parse_ignore_list(ignore_list)
        
        # Build debug result
        result = [
            ["Debug Info", "Value"],
            ["All pools in file", str(len(all_pools_in_file))],
            ["", ""],
            ["Requested pools count", str(len(pools_lista))],
            ["Ignore list count", str(len(pools_to_ignore))],
            ["", ""],
            ["ALL POOLS IN FILE:", ""],
        ]
        
        for i, pool in enumerate(all_pools_in_file):
            result.append([f"Pool {i+1}", f"'{pool}' (len={len(pool)})"])
        
        result.append(["", ""])
        result.append(["REQUESTED POOLS:", ""])
        for i, pool in enumerate(pools_lista):
            result.append([f"Req {i+1}", f"'{pool}' (len={len(pool)})"])
        
        result.append(["", ""])
        result.append(["IGNORE LIST:", ""])
        for i, pool in enumerate(pools_to_ignore):
            result.append([f"Ignore {i+1}", f"'{pool}' (len={len(pool)})"])
        
        return result
        
    except Exception as e:
        return [["Erro", str(e)]]

@cache_udf_result(ttl_seconds=300)  # Cache por 5 minutos - validação pesada
@xw.func
@xw.ret(expand='table')
def AmfiValidateData() -> List[List]:
    """Valida dados dos arquivos mais recentes"""
    try:
        csv_path = get_latest_csv_path()
        xlsx_path = get_latest_xlsx_path()
        
        # Verificar se arquivos foram encontrados
        if "No CSV file found" in csv_path or "No XLSX file found" in xlsx_path:
            return [["Status", "ERRO"], ["Mensagem", "Arquivos de dados não encontrados"]]
        
        # Gerar relatório
        report = generate_validation_report(csv_path, xlsx_path)
        
        # Formatar para Excel
        result = [
            ["Validação de Dados", ""],
            ["Timestamp", report['timestamp']],
            ["Status Geral", report['overall_status']],
            ["", ""],
            ["Resumo", ""]
        ]
        
        for msg in report['summary']:
            result.append(["", msg])
        
        # Adicionar detalhes se houver warnings ou erros
        if report['overall_status'] != 'VALID':
            result.append(["", ""])
            result.append(["Detalhes", ""])
            
            for validation_type, validation_data in report['validations'].items():
                if 'errors' in validation_data and validation_data['errors']:
                    result.append([validation_type, "ERROS:"])
                    for error in validation_data['errors']:
                        result.append(["", error])
                
                if 'warnings' in validation_data and validation_data['warnings']:
                    result.append([validation_type, "AVISOS:"])
                    for warning in validation_data['warnings']:
                        result.append(["", warning])
        
        return result
        
    except Exception as e:
        return [["Erro", str(e)]]