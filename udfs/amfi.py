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
    """
    Lê arquivo JSON e busca chave específica
    
    Args:
        caminho_arquivo: Caminho completo do arquivo JSON OU nome do pool
        chave: Nome da chave para buscar no JSON
    """
    import os
    
    # Se não tem extensão .json e não é um caminho completo, assume que é nome de pool
    if not caminho_arquivo.endswith('.json') and not os.path.isabs(caminho_arquivo):
        # Converter nome do pool para caminho do arquivo
        pool_name_clean = caminho_arquivo.strip().lower().replace(" ", "_").replace("#", "")
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        caminho_arquivo = os.path.join(base_path, 'data', 'escrituras', f"{pool_name_clean}.json")
    
    return AmFiReadJSONLogic.execute(caminho_arquivo, chave)

@cache_udf_result(ttl_seconds=60)  # Cache por 60 segundos
@xw.func
@xw.ret(expand='table')
def AmfiXLSX(pool_name, status_=None, date_=None, visao=None, group_by=None):
    """
    Consulta dados de ativos/empréstimos filtrados por pool e status
    
    Args:
        pool_name: Nome do pool (obrigatório)
        status_: Status para filtrar (opcional)
        date_: Data específica YYYY-MM-DD (opcional)
        visao: 'exec' para colunas executivas, 'full' para todas
        group_by: True para agrupar e somar por entidades, False ou vazio para dados individuais
    """
    # Set defaults to match expected behavior
    if status_ is None:
        status_ = ""
    if date_ is None:
        date_ = ""
    if visao is None:
        visao = "exec"
    if group_by is None:
        group_by = False
    
    # Convert group_by to boolean if it's a string or number
    if isinstance(group_by, str):
        group_by = group_by.lower() in ['true', '1', 'yes', 'sim']
    elif isinstance(group_by, (int, float)):
        group_by = bool(group_by)
    
    return EnhancedAmfiXLSXLogic.execute(pool_name, status_, date_, visao, group_by)


@cache_udf_result(ttl_seconds=120)  # Cache por 2 minutos - análise mais pesada
@xw.func
@xw.ret(expand='table')
def AmfiConcentracao(arquivo_xlsx, pool, pl_total, tipo=None, top=None, limite=None, ignore_list=None):
    """Análise de concentração de sacados, cedentes ou combinado com monitoramento de limites"""
    try:
        import time
        import gc
        
        # CRITICAL: Disable automatic calculation mode temporarily to prevent array update conflicts
        try:
            import xlwings as xw
            app = xw.apps.active
            original_calculation = app.calculation
            app.calculation = 'manual'
        except:
            pass
        
        # Small delay to prevent rapid recalculation issues
        time.sleep(0.1)
        
        # Execute the analysis and get the FINAL result in one go
        # This prevents Excel from trying to update a dynamic array mid-calculation
        result = process_concentracao(arquivo_xlsx, pool, pl_total, tipo, top, limite, ignore_list)
        
        # Ensure result is a complete, final matrix
        if not isinstance(result, list) or not result:
            result = [["Erro", "Resultado inválido", "", "", ""]]
        
        # Force garbage collection to prevent memory issues
        gc.collect()
        
        # Restore original calculation mode
        try:
            app.calculation = original_calculation
        except:
            pass
        
        return result
        
    except MemoryError:
        # Handle memory errors that can cause UDF deletion
        import gc
        gc.collect()
        return [["Erro de Memória", "Função muito pesada - tente com menos dados", "", "", ""]]
    except Exception as e:
        # Log error details for debugging
        error_msg = str(e)
        if len(error_msg) > 100:
            error_msg = error_msg[:100] + "..."
        
        # Ensure we always return a properly formatted error
        return [["Erro", error_msg, "", "", ""]]

@xw.func  
def AmfiConcentracaoStatus() -> str:
    """Verifica se a função AmfiConcentracao está disponível"""
    return "Função AmfiConcentracao disponível"

@cache_udf_result(ttl_seconds=120)  
@xw.func
def AmfiConcentracaoSafe(arquivo_xlsx, pool, pl_total, tipo=None, top=None, limite=None, ignore_list=None, output_range=None):
    """
    Versão segura do AmfiConcentracao que escreve diretamente em um range específico
    ao invés de usar dynamic arrays para evitar conflitos de 'cannot change part of array'
    
    Args:
        output_range: Range de células onde escrever o resultado (ex: "A1:E20")
        Outros parâmetros iguais ao AmfiConcentracao
    
    Returns:
        String de status ao invés de array dinâmico
    """
    try:
        import time
        import gc
        
        # Small delay to prevent rapid recalculation issues
        time.sleep(0.1)
        
        # Execute the analysis
        result = process_concentracao(arquivo_xlsx, pool, pl_total, tipo, top, limite, ignore_list)
        
        # If output_range is specified, write directly to that range
        if output_range:
            try:
                import xlwings as xw
                wb = xw.books.active
                sheet = wb.sheets.active
                
                # Clear the target range first
                range_obj = sheet.range(output_range)
                range_obj.clear()
                
                # Write the result to the specified range
                if result and len(result) > 0:
                    # Adjust range size to fit the data
                    rows_needed = len(result)
                    cols_needed = len(result[0]) if result[0] else 5
                    
                    # Write data to range
                    target_range = range_obj.resize(rows_needed, cols_needed)
                    target_range.value = result
                    
                    gc.collect()
                    return f"Análise concluída: {rows_needed} linhas escritas em {output_range}"
                else:
                    gc.collect()
                    return "Erro: Nenhum resultado para escrever"
                    
            except Exception as e:
                gc.collect()
                return f"Erro ao escrever em {output_range}: {str(e)}"
        else:
            # If no output range specified, return row count as status
            if result and len(result) > 0:
                gc.collect()
                return f"Análise concluída: {len(result)} linhas (use output_range para escrever)"
            else:
                gc.collect()
                return "Erro: Nenhum resultado gerado"
        
    except Exception as e:
        import gc
        gc.collect()
        error_msg = str(e)
        if len(error_msg) > 100:
            error_msg = error_msg[:100] + "..."
        return f"Erro: {error_msg}"
    
    
@xw.func
@xw.ret(expand='table')
def AmfiMonitoringGaps():
    """
    Identifica eventos de monitoramento definidos nos JSONs mas não implementados no código.
    
    Retorna:
        DataFrame com colunas: Pool | Tipo Monitor | Categoria | Descrição | Status
    
    Exemplo:
        =AmfiMonitoringGaps()
    """
    try:
        from monitoring_gap_detector import find_monitoring_gaps
        import pandas as pd
        
        gaps = find_monitoring_gaps()
        
        if not gaps:
            return [["✅ Todos os monitores estão implementados!"]]
        
        # Criar lista para DataFrame
        data = []
        for pool_name, pool_gaps in gaps.items():
            for gap in pool_gaps:
                data.append([
                    pool_name,
                    gap["tipo"],
                    gap["categoria"],
                    gap["descricao"],
                    "❌ Não Implementado"
                ])
        
        # Criar DataFrame
        df = pd.DataFrame(data, columns=["Pool", "Tipo Monitor", "Categoria", "Descrição", "Status"])
        
        # Ordenar por Pool e Tipo
        df = df.sort_values(["Pool", "Tipo Monitor"])
        
        # Adicionar linha de resumo no topo
        summary = pd.DataFrame([
            ["RESUMO", f"{len(data)} monitores pendentes", f"{len(gaps)} pools afetados", "", "⚠️ ATENÇÃO"]
        ], columns=df.columns)
        
        df = pd.concat([summary, df], ignore_index=True)
        
        return df.values.tolist()
        
    except Exception as e:
        return [[f"Erro ao detectar gaps: {str(e)}"]]


@xw.func
@xw.arg('monitor_type', doc='Tipo do monitor para gerar template de implementação')
@xw.ret(expand='table')
def AmfiMonitorTemplate(monitor_type):
    """
    Gera template de código Python para implementar um monitor específico.
    
    Args:
        monitor_type: Nome do tipo de monitor (ex: "recovery_rate_mensal")
    
    Retorna:
        Template de código Python formatado
    
    Exemplo:
        =AmfiMonitorTemplate("recovery_rate_mensal")
    """
    try:
        from monitoring_gap_detector import get_implementation_template
        
        template = get_implementation_template(monitor_type)
        
        # Dividir em linhas para exibição no Excel
        lines = template.split('\n')
        return [[line] for line in lines]
        
    except Exception as e:
        return [[f"Erro ao gerar template: {str(e)}"]]
    
    
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
def AmfiDebugGrouping(pool_name: str, search_term: str = "AMFI") -> List[List]:
    """
    Debug function to test grouping functionality and search for specific entities
    """
    try:
        from xlsx_handler import EnhancedAmfiXLSXLogic
        
        # Get data without grouping
        result_no_group = EnhancedAmfiXLSXLogic.execute(pool_name, "", "", "exec", False)
        
        # Get data with grouping
        result_with_group = EnhancedAmfiXLSXLogic.execute(pool_name, "", "", "exec", True)
        
        # Search for the term in non-grouped data
        no_group_matches = []
        if len(result_no_group) > 1:  # Has data beyond header
            header = result_no_group[0]
            for i, row in enumerate(result_no_group[1:], 1):  # Skip header
                row_str = str(row).upper()
                if search_term.upper() in row_str:
                    no_group_matches.append((i, row))
        
        # Search for the term in grouped data
        group_matches = []
        if len(result_with_group) > 1:  # Has data beyond header
            header = result_with_group[0]
            for i, row in enumerate(result_with_group[1:], 1):  # Skip header
                row_str = str(row).upper()
                if search_term.upper() in row_str:
                    group_matches.append((i, row))
        
        debug_result = [
            ["Debug Grouping Search", ""],
            ["Pool", pool_name],
            ["Search Term", search_term],
            ["", ""],
            ["SUMMARY:", ""],
            ["Total rows without grouping", str(len(result_no_group) - 1)],
            ["Total rows with grouping", str(len(result_with_group) - 1)],
            ["Matches without grouping", str(len(no_group_matches))],
            ["Matches with grouping", str(len(group_matches))],
            ["", ""],
            ["MATCHES WITHOUT GROUPING:", ""]
        ]
        
        for i, (row_num, row) in enumerate(no_group_matches[:10]):  # First 10 matches
            debug_result.append([f"NoGroup {row_num}", str(row)])
        
        debug_result.extend([
            ["", ""],
            ["MATCHES WITH GROUPING:", ""]
        ])
        
        for i, (row_num, row) in enumerate(group_matches[:10]):  # First 10 matches
            debug_result.append([f"Grouped {row_num}", str(row)])
        
        if not group_matches and no_group_matches:
            debug_result.extend([
                ["", ""],
                ["⚠️ ISSUE:", f"'{search_term}' found in original data but MISSING in grouped data!"]
            ])
        
        return debug_result
        
    except Exception as e:
        return [["Erro", str(e)]]

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
def AmfiCheckPoolJSON(pool_name: str) -> str:
    """
    Verifica se existe arquivo JSON para o pool especificado
    
    Args:
        pool_name: Nome do pool para verificar
        
    Returns:
        "TRUE" se o arquivo JSON existe
        "FALSE" se o arquivo JSON não existe
        "ERRO: [mensagem]" em caso de erro
    """
    try:
        import os
        import glob
        
        if not pool_name or not pool_name.strip():
            return "ERRO: Nome do pool não fornecido"
        
        # Limpar nome do pool para formato de arquivo
        pool_name_clean = pool_name.strip().lower().replace(" ", "_").replace("#", "")
        
        # Diretório das escrituras
        escrituras_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'escrituras')
        
        # Procurar arquivo JSON correspondente
        json_pattern = os.path.join(escrituras_dir, f"{pool_name_clean}.json")
        json_files = glob.glob(json_pattern)
        
        if json_files:
            return "TRUE"
        else:
            # Tentar busca mais flexível
            all_json_files = glob.glob(os.path.join(escrituras_dir, "*.json"))
            for json_file in all_json_files:
                filename = os.path.basename(json_file).lower()
                if pool_name_clean in filename or filename in pool_name_clean:
                    return "TRUE"
            
            return "FALSE"
            
    except Exception as e:
        return f"ERRO: {str(e)}"

@xw.func
@xw.ret(expand='table')
def AmfiListPoolJSONs() -> List[List]:
    """
    Lista todos os pools que têm arquivo JSON disponível
    
    Returns:
        Lista com nomes dos pools com JSON
    """
    try:
        import os
        import glob
        
        # Diretório das escrituras
        escrituras_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'escrituras')
        
        # Buscar todos os arquivos JSON
        json_files = glob.glob(os.path.join(escrituras_dir, "*.json"))
        
        if not json_files:
            return [["Nenhum arquivo JSON encontrado"]]
        
        # Extrair nomes dos pools
        result = [["Pools com JSON"]]
        for json_file in json_files:
            filename = os.path.basename(json_file)
            pool_name = filename.replace(".json", "").replace("_", " ").title()
            result.append([pool_name])
        
        return result
        
    except Exception as e:
        return [["ERRO", str(e)]]

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