"""
CSV Handler - Processamento de arquivos CSV para AmfiDashboard e ListPools
"""
import pandas as pd
import numpy as np
from typing import List, Tuple, Any, Set
from cache_manager import load_csv_cached, auto_clear_daily_cache

def _normalize_pools(nomes_pool) -> List[str]:
    """
    Normaliza entrada de pools para lista de strings
    Handles Excel ranges, ensuring all values are captured correctly
    """
    if nomes_pool is None:
        return []
    
    # Handle string input (single pool name)
    if isinstance(nomes_pool, str):
        return [nomes_pool.strip()] if nomes_pool.strip() else []
    
    # Handle numeric input
    if isinstance(nomes_pool, (int, float)):
        return [str(nomes_pool).strip()]
    
    # Handle iterables (Excel ranges, lists, tuples)
    if hasattr(nomes_pool, '__iter__'):
        normalized = []
        for item in nomes_pool:
            if item is not None:
                # Handle nested lists/tuples from Excel ranges
                if hasattr(item, '__iter__') and not isinstance(item, str):
                    for sub_item in item:
                        if sub_item is not None and str(sub_item).strip():
                            normalized.append(str(sub_item).strip())
                else:
                    item_str = str(item).strip()
                    if item_str:
                        normalized.append(item_str)
        return normalized
    
    # Fallback for any other type
    return [str(nomes_pool).strip()] if nomes_pool else []

def _parse_ignore_list(ignore_list: Any) -> Set[str]:
    """
    Parser robusto para ignore_list com suporte a múltiplos formatos.
    Retorna um Set para eliminação automática de duplicatas e busca eficiente.
    
    Suporta:
    - Strings simples: "Pool A"
    - Strings com pipe: "Pool A|Pool B|Pool C"
    - Ranges Excel: células selecionadas
    - Listas Python
    """
    if not ignore_list:
        return set()
    
    pools_to_ignore = set()
    
    try:
        if isinstance(ignore_list, str):
            # String simples ou separada por pipe
            pools_to_ignore.update(item.strip() for item in ignore_list.split("|") if item.strip())
        
        elif hasattr(ignore_list, '__iter__'):
            # Range Excel ou lista Python
            for item in ignore_list:
                if item is not None:
                    # Handle nested lists/tuples from Excel ranges
                    if hasattr(item, '__iter__') and not isinstance(item, str):
                        for sub_item in item:
                            if sub_item is not None:
                                item_str = str(sub_item).strip()
                                if item_str:
                                    # Suporte a pipe dentro de células individuais
                                    pools_to_ignore.update(sub.strip() for sub in item_str.split("|") if sub.strip())
                    else:
                        item_str = str(item).strip()
                        if item_str:
                            # Suporte a pipe dentro de células individuais
                            pools_to_ignore.update(sub.strip() for sub in item_str.split("|") if sub.strip())
        else:
            # Valor único
            item_str = str(ignore_list).strip()
            if item_str:
                pools_to_ignore.add(item_str)
                
    except Exception as e:
        # Em caso de erro, retornar set vazio (não bloquear operação)
        return set()
    
    return pools_to_ignore

def _format_data_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Formata colunas de números para padrão brasileiro (versão simplificada)
    """
    df_copy = df.copy()
    
    # Apenas converter números para formato brasileiro (sem mexer em datas)
    for col in df_copy.columns:
        try:
            # Tentar converter para numérico
            numeric_series = pd.to_numeric(df_copy[col], errors='coerce')
            
            # Se a conversão teve sucesso em pelo menos alguns valores
            if not numeric_series.isna().all():
                # Converter pontos para vírgulas apenas nos valores numéricos
                df_copy[col] = df_copy[col].astype(str).str.replace('.', ',', regex=False)
        except:
            # Se der qualquer erro, manter coluna original
            pass
    
    return df_copy

def _build_result_matrix(filtered_dfs: List[Tuple[str, pd.DataFrame]], columns: List[str]) -> List[List]:
    """
    Constroi matriz de resultado preservando tipos de dados
    """
    if not filtered_dfs:
        return [["Nenhum dado encontrado"]]
    
    result = [list(columns)]  # Cabecalho
    
    for pool_name, df in filtered_dfs:
        if df.empty:
            result.append([f"Pool '{pool_name}' nao encontrado"] + [''] * (len(columns) - 1))
            continue
        
        # Converter preservando tipos de dados
        excel_data = _convert_to_excel_format_csv(df, columns)
        result.extend(excel_data)
    
    return result


def _preserve_data_types_csv(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preserva tipos de dados nativos no CSV com limpeza de simbolos financeiros
    Converte percentuais para decimais (15% -> 0.15)
    """
    df_copy = df.copy()
    
    # Identificar colunas de data pelos nomes comuns
    date_columns = ['data', 'vencimento', 'prazo']
    
    for col in df_copy.columns:
        col_lower = col.lower()
        
        # Para colunas de data, tentar converter para datetime
        if any(date_word in col_lower for date_word in date_columns):
            try:
                df_copy[col] = pd.to_datetime(df_copy[col], errors='coerce')
            except:
                pass
        
        # Para colunas que podem ser numericas (com simbolos)
        else:
            try:
                # Verificar se a coluna tem simbolos financeiros
                sample_values = df_copy[col].astype(str).head(10)
                has_currency = sample_values.str.contains(r'R\$|€|\$|£', na=False).any()
                has_percentage = sample_values.str.contains('%', na=False).any()
                
                if has_currency or has_percentage:
                    # Limpar simbolos e converter para numerico
                    def clean_financial_value(value_str):
                        if pd.isna(value_str) or value_str == '' or str(value_str).lower() == 'nan':
                            return None
                        
                        value_str = str(value_str).strip()
                        original_value = value_str
                        
                        # Verificar se e percentual
                        is_percentage = '%' in value_str
                        
                        # Remover simbolos financeiros
                        value_str = value_str.replace('R$', '').replace('$', '').replace('€', '').replace('£', '')
                        value_str = value_str.replace('%', '')
                        value_str = value_str.strip()
                        
                        # Se valor ficou vazio apos limpeza
                        if not value_str:
                            return None
                        
                        # Padronizar separador decimal brasileiro
                        # Se tem ponto E virgula, assumir formato brasileiro (1.234,56)
                        if '.' in value_str and ',' in value_str:
                            # Remover pontos (separador de milhares) e trocar virgula por ponto
                            value_str = value_str.replace('.', '').replace(',', '.')
                        
                        # Se tem apenas virgula (formato brasileiro), trocar por ponto
                        elif ',' in value_str and '.' not in value_str:
                            value_str = value_str.replace(',', '.')
                        
                        # Tentar converter para float
                        try:
                            numeric_value = float(value_str)
                            
                            # Se era percentual, dividir por 100
                            if is_percentage:
                                numeric_value = numeric_value / 100
                            
                            return numeric_value
                            
                        except ValueError:
                            return None
                    
                    # Aplicar limpeza a toda a coluna
                    cleaned_series = df_copy[col].apply(clean_financial_value)
                    
                    # Verificar se conseguiu converter a maioria dos valores
                    valid_count = cleaned_series.notna().sum()
                    total_non_empty = df_copy[col].notna().sum()
                    
                    if valid_count > total_non_empty * 0.5:
                        df_copy[col] = cleaned_series
                
                else:
                    # Para colunas sem simbolos, tentar conversao numerica normal
                    def clean_plain_number(value_str):
                        if pd.isna(value_str) or value_str == '' or str(value_str).lower() == 'nan':
                            return None
                        
                        value_str = str(value_str).strip()
                        
                        # Tratar formato brasileiro sem simbolos
                        if '.' in value_str and ',' in value_str:
                            value_str = value_str.replace('.', '').replace(',', '.')
                        elif ',' in value_str and '.' not in value_str:
                            value_str = value_str.replace(',', '.')
                        
                        try:
                            return float(value_str)
                        except ValueError:
                            return None
                    
                    cleaned_series = df_copy[col].apply(clean_plain_number)
                    
                    # Se a maioria dos valores for numerica, usar como numerico
                    valid_count = cleaned_series.notna().sum()
                    total_non_empty = df_copy[col].notna().sum()
                    
                    if valid_count > total_non_empty * 0.3:
                        df_copy[col] = cleaned_series
                        
            except Exception as e:
                # Em caso de erro, manter coluna original
                pass
    
    return df_copy

def _convert_to_excel_format_csv(df: pd.DataFrame, columns: List[str]) -> List[List]:
    """
    Converte DataFrame CSV para formato Excel preservando tipos
    """
    if df.empty:
        return []
    
    result = []
    
    for _, row in df.iterrows():
        excel_row = []
        for col in columns:
            value = row[col]
            
            # Preservar tipos nativos para o Excel
            if pd.isna(value):
                excel_row.append('')
            elif isinstance(value, pd.Timestamp):
                # Converter Timestamp para datetime do Python
                excel_row.append(value.to_pydatetime())
            elif isinstance(value, (int, float)):
                # Manter numeros como numeros
                excel_row.append(value)
            else:
                # Converter para string apenas se necessario
                excel_row.append(str(value))
        
        result.append(excel_row)
    
    return result

class AmfiDashboardLogic:
    """
    Lógica de negócio para AmfiDashboard
    """
    
    @staticmethod
    def _rename_columns_for_display(df: pd.DataFrame) -> pd.DataFrame:
        """
        Renomeia colunas para exibição conforme solicitado
        """
        df_renamed = df.copy()
        
        # Dicionário de mapeamento de nomes de colunas
        column_mapping = {
            'Data de vencimento': 'Dt. Venct',
            'Prazo até o vencimento': 'Dias',
            'Caixa Livre': 'Cash',
            'Saldo em Aplicações': 'Over',
            'Fundo de Reserva': 'Cx. Reserva'
        }
        
        # Aplicar renomeação
        df_renamed = df_renamed.rename(columns=column_mapping)
        
        return df_renamed
    
    @staticmethod
    def _add_calculated_columns(df: pd.DataFrame) -> pd.DataFrame:
        """
        Adiciona colunas calculadas ao DataFrame
        """
        df_calc = df.copy()
        
        # Adicionar coluna JSON availability
        try:
            import os
            import glob
            
            # Diretório das escrituras
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            escrituras_dir = os.path.join(base_path, 'data', 'escrituras')
            
            # Verificar JSON para cada pool
            json_status = []
            for _, row in df_calc.iterrows():
                pool_name = str(row['Nome']) if pd.notna(row['Nome']) else ""
                pool_name_clean = pool_name.strip().lower().replace(" ", "_").replace("#", "")
                
                # Procurar arquivo JSON
                json_pattern = os.path.join(escrituras_dir, f"{pool_name_clean}.json")
                json_files = glob.glob(json_pattern)
                
                if json_files:
                    json_status.append("✓")
                else:
                    # Busca flexível
                    found = False
                    all_json_files = glob.glob(os.path.join(escrituras_dir, "*.json"))
                    for json_file in all_json_files:
                        filename = os.path.basename(json_file).lower()
                        if pool_name_clean in filename or filename in pool_name_clean:
                            found = True
                            break
                    json_status.append("✓" if found else "✗")
            
            df_calc['JSON'] = json_status
        except Exception:
            df_calc['JSON'] = "?"
        
        # Calcular Cash+Over/PL
        try:
            # Verificar se as colunas necessárias existem
            if all(col in df_calc.columns for col in ['Cash', 'Over', 'PL']):
                # Converter para numérico se necessário e calcular
                cash_values = pd.to_numeric(df_calc['Cash'], errors='coerce').fillna(0)
                over_values = pd.to_numeric(df_calc['Over'], errors='coerce').fillna(0)
                pl_values = pd.to_numeric(df_calc['PL'], errors='coerce').fillna(1)  # Evitar divisão por zero
                
                # Calcular (Cash + Over) / PL
                df_calc['Cash+Over/PL'] = (cash_values + over_values) / pl_values
                
                # Substituir infinitos e NaN por 0
                df_calc['Cash+Over/PL'] = df_calc['Cash+Over/PL'].replace([float('inf'), float('-inf')], 0).fillna(0)
        
        except Exception:
            # Em caso de erro, criar coluna com zeros
            df_calc['Cash+Over/PL'] = 0
        
        return df_calc
    
    @staticmethod
    def _get_executive_columns(df: pd.DataFrame) -> List[str]:
        """
        Retorna colunas executivas que existem no DataFrame
        """
        colunas_exec = [
            'Nome', 'JSON', 'Dt. Venct', 'Dias',
            'PL', 'SR', 'JR', 'Carteira', 'Cash', 'Over', 'Cx. Reserva',
            'R.G.', 'I.S.', 'I.S. (Tranche)',
            '% de Atraso', '% de PDD', 'Rentabilidade Média', 'Ativos %', 'Cash+Over/PL'
        ]
        return [col for col in colunas_exec if col in df.columns]
    
    @staticmethod
    def execute(caminho_arquivo: str, nomes_pool, visao: str = 'exec', ignore_list: Any = None) -> List[List]:
        """
        Executa a logica do AmfiDashboard com conversao agressiva de tipos
        
        Args:
            caminho_arquivo: Caminho do arquivo CSV
            nomes_pool: Pool(s) a serem exibidos
            visao: 'exec' para visão executiva, 'full' para visão completa
            ignore_list: Pool(s) a serem ignorados (string, range Excel ou lista)
        """
        try:
            # Auto-clear cache if new day
            auto_clear_daily_cache()
            
            # Carregar dados com cache
            df = load_csv_cached(caminho_arquivo)
            
            # Parse ignore list
            pools_to_ignore = _parse_ignore_list(ignore_list)
            
            # CONVERSÃO AGRESSIVA DE TIPOS
            for col in df.columns:
                if col == 'Nome':  # Pular coluna de identificação
                    continue
                
                # Converter coluna para string primeiro
                col_as_string = df[col].astype(str)
                
                # Verificar se é coluna de data
                # Excluir "prazo até vencimento" que é um número (dias), não uma data
                col_lower = col.lower()
                if (('data' in col_lower or 'vencimento' in col_lower) and 
                    'prazo' not in col_lower and 'até' not in col_lower):
                    try:
                        df[col] = pd.to_datetime(df[col], errors='coerce')
                        continue
                    except:
                        pass
                
                # Para outras colunas, tentar conversão numérica agressiva
                converted_values = []
                for value in col_as_string:
                    try:
                        if pd.isna(value) or str(value).lower() in ['', 'nan', 'none']:
                            converted_values.append(None)
                            continue
                        
                        # Limpar valor
                        clean_value = str(value).strip()
                        
                        # Detectar percentual
                        is_percentage = '%' in clean_value
                        
                        # Remover símbolos
                        clean_value = clean_value.replace('R$', '').replace('$', '')
                        clean_value = clean_value.replace('%', '').replace('€', '').replace('£', '')
                        clean_value = clean_value.strip()
                        
                        if not clean_value:
                            converted_values.append(None)
                            continue
                        
                        # Converter formato brasileiro
                        if '.' in clean_value and ',' in clean_value:
                            # Formato: 1.234,56
                            clean_value = clean_value.replace('.', '').replace(',', '.')
                        elif ',' in clean_value and '.' not in clean_value:
                            # Formato: 1234,56
                            clean_value = clean_value.replace(',', '.')
                        
                        # Tentar converter
                        numeric_val = float(clean_value)
                        
                        # Se era percentual, dividir por 100
                        if is_percentage:
                            numeric_val = numeric_val / 100
                        
                        converted_values.append(numeric_val)
                    
                    except Exception:
                        # Se não conseguir converter, manter como string
                        converted_values.append(str(value))
                
                # Verificar quantos valores foram convertidos
                numeric_count = sum(1 for v in converted_values if isinstance(v, (int, float)))
                total_count = len([v for v in converted_values if v is not None])
                
                # Se a maioria foi convertida, usar valores numéricos
                if total_count > 0 and numeric_count / total_count > 0.5:
                    df[col] = converted_values
            
            # Normalizar pools
            pools_lista = _normalize_pools(nomes_pool)
            
            # Se nenhum pool específico foi fornecido, retornar todos os pools disponíveis
            if not pools_lista:
                # Obter todos os pools únicos do DataFrame
                all_pools = df['Nome'].dropna().unique()
                pools_lista = [str(pool) for pool in all_pools]
                if not pools_lista:
                    return [["ERRO: Nenhum pool encontrado no arquivo"]]
            
            # Aplicar ignore list aos pools selecionados
            if pools_to_ignore:
                # Filtrar pools_lista removendo os que estão na ignore list
                # Normalize pool names for comparison
                filtered_pools = []
                for pool in pools_lista:
                    pool_normalized = ' '.join(pool.strip().split()).lower()
                    should_include = True
                    
                    # Check against each ignored pool
                    for ignored in pools_to_ignore:
                        ignored_normalized = ' '.join(ignored.strip().split()).lower()
                        if pool_normalized == ignored_normalized:
                            should_include = False
                            break
                    
                    if should_include:
                        filtered_pools.append(pool)
                    
                pools_lista = filtered_pools
                
                if not pools_lista:
                    return [["AVISO: Todos os pools foram filtrados pela ignore list"]]
            
            # Renomear colunas para exibição
            df = AmfiDashboardLogic._rename_columns_for_display(df)
            
            # Adicionar colunas calculadas
            df = AmfiDashboardLogic._add_calculated_columns(df)
            
            # Definir colunas baseado na visao
            if visao.lower() == 'exec':
                colunas_target = AmfiDashboardLogic._get_executive_columns(df)
            else:
                colunas_target = list(df.columns)
            
            if not colunas_target:
                return [["ERRO: Nenhuma coluna valida encontrada"]]
            
            # Processar cada pool
            filtered_results = []
            for pool in pools_lista:
                # Normalize pool name for comparison (remove extra spaces, normalize whitespace)
                pool_normalized = ' '.join(pool.strip().split()).lower()
                
                # Create a normalized comparison for the dataframe column
                df['Nome_normalized'] = df['Nome'].astype(str).apply(
                    lambda x: ' '.join(x.strip().split()).lower()
                )
                
                # Filter using normalized names
                df_pool = df[df['Nome_normalized'] == pool_normalized].copy()
                
                # Remove the temporary normalized column from the result
                if 'Nome_normalized' in df_pool.columns:
                    df_pool = df_pool.drop(columns=['Nome_normalized'])
                
                if not df_pool.empty:  # Só adicionar se houver dados
                    filtered_results.append((pool, df_pool))
            
            # Clean up the temporary column from the main dataframe
            if 'Nome_normalized' in df.columns:
                df = df.drop(columns=['Nome_normalized'])
            
            # Construir resultado final
            result = _build_result_matrix(filtered_results, colunas_target)
            
            return result
            
        except Exception as e:
            return [[f"ERRO: {str(e)}"]]

class ListPoolsLogic:
    """
    Lógica de negócio para ListPools
    """
    
    @staticmethod
    def execute(caminho_arquivo: str, ignore_list: Any = None) -> List[List[str]]:
        """
        Executa a lógica do ListPools
        
        Args:
            caminho_arquivo: Caminho do arquivo CSV
            ignore_list: Pool(s) a serem ignorados (string, range Excel ou lista)
        """
        try:
            # Carregar dados com cache
            df = load_csv_cached(caminho_arquivo)
            
            # Obter pools únicos e ordenar
            pools_unicos = df['Nome'].dropna().unique()
            pools_ordenados = sorted(pools_unicos, key=str.lower)
            
            # Aplicar ignore list se fornecida
            if ignore_list:
                pools_to_ignore = _parse_ignore_list(ignore_list)
                
                if pools_to_ignore:
                    # Filtrar pools removendo os que estão na ignore list
                    # Normalizar nomes para comparação
                    filtered_pools = []
                    for pool in pools_ordenados:
                        pool_normalized = ' '.join(pool.strip().split()).lower()
                        should_include = True
                        
                        # Verificar contra cada pool ignorado
                        for ignored in pools_to_ignore:
                            ignored_normalized = ' '.join(ignored.strip().split()).lower()
                            if pool_normalized == ignored_normalized:
                                should_include = False
                                break
                        
                        if should_include:
                            filtered_pools.append(pool)
                    
                    pools_ordenados = filtered_pools
            
            return [[pool] for pool in pools_ordenados]
            
        except Exception as e:
            return [[f"ERRO: {str(e)}"]]