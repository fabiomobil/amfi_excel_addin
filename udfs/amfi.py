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

@xw.func
@xw.ret(expand='table')
def AmfiDashboard(caminho_arquivo: str, nomes_pool, visao: str = 'exec') -> List[List]:
    """Dashboard AMFI para consulta de oportunidades"""
    return AmfiDashboardLogic.execute(caminho_arquivo, nomes_pool, visao)

@xw.func
@xw.ret(expand='table')  
def ListPools(caminho_arquivo: str) -> List[List[str]]:
    """Lista pools disponíveis ordenados alfabeticamente"""
    return ListPoolsLogic.execute(caminho_arquivo)

@xw.func
@xw.ret(expand='table')
def AmFiReadJSON(caminho_arquivo: str, chave: str) -> List[List[str]]:
    """Lê arquivo JSON e busca chave específica"""
    return AmFiReadJSONLogic.execute(caminho_arquivo, chave)

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
    """Retorna estatísticas dos caches"""
    stats = get_cache_stats()
    return f"Cache: {stats['total_files']} arquivos (CSV: {stats['csv_files']}, JSON: {stats['json_files']}, XLSX: {stats['xlsx_files']})"

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