"""
JSON Handler - Processamento de arquivos JSON para AmFiReadJSON
Versao completa com conversao de tipos numericos e datas
"""
import re
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
from functools import lru_cache
from cache_manager import load_json_cached

# Compilar regex uma vez para performance
DATE_PATTERNS = [
    (re.compile(r'^\d{4}-\d{2}-\d{2}$'), '%Y-%m-%d'),           # YYYY-MM-DD (ISO)
    (re.compile(r'^\d{2}/\d{2}/\d{4}$'), '%d/%m/%Y'),           # DD/MM/YYYY (BR)
    (re.compile(r'^\d{4}/\d{2}/\d{2}$'), '%Y/%m/%d'),           # YYYY/MM/DD
    (re.compile(r'^\d{2}-\d{2}-\d{4}$'), '%d-%m-%Y'),           # DD-MM-YYYY
    (re.compile(r'^\d{4}\.\d{2}\.\d{2}$'), '%Y.%m.%d'),         # YYYY.MM.DD
]

@lru_cache(maxsize=1000)
def _is_valid_date(value: str) -> Optional[str]:
    """
    Detecta e valida se string e data valida
    Retorna formato da data se valida, None caso contrario
    """
    if not isinstance(value, str) or len(value.strip()) not in (8, 10):
        return None
    
    value_clean = value.strip()
    
    for pattern, date_format in DATE_PATTERNS:
        if pattern.match(value_clean):
            try:
                datetime.strptime(value_clean, date_format)
                return date_format
            except ValueError:
                continue
    
    return None

def _convert_financial_value(value_str):
    """
    Converte valor financeiro brasileiro para numero
    15% -> 0.15, R$ 1.234,56 -> 1234.56
    """
    if pd.isna(value_str) or str(value_str).lower() in ['', 'nan', 'none', 'null']:
        return None
    
    try:
        # Converter para string e limpar
        clean_value = str(value_str).strip()
        original_clean = clean_value
        
        # Detectar percentual
        is_percentage = '%' in clean_value
        
        # Remover simbolos financeiros
        clean_value = clean_value.replace('R$', '').replace('$', '')
        clean_value = clean_value.replace('%', '').replace('€', '').replace('£', '')
        clean_value = clean_value.strip()
        
        if not clean_value:
            return None
        
        # Converter formato brasileiro para internacional
        if '.' in clean_value and ',' in clean_value:
            # Formato: 1.234,56 -> 1234.56
            clean_value = clean_value.replace('.', '').replace(',', '.')
        elif ',' in clean_value and '.' not in clean_value:
            # Formato: 1234,56 -> 1234.56
            clean_value = clean_value.replace(',', '.')
        
        # Tentar converter para numero
        numeric_val = float(clean_value)
        
        # Se era percentual, dividir por 100
        if is_percentage:
            numeric_val = numeric_val / 100
        
        return numeric_val
        
    except (ValueError, TypeError):
        return value_str  # Retorna string original se nao conseguir converter

def _convert_date_value(value_str):
    """
    Converte string de data para datetime do Python (melhorada)
    """
    if pd.isna(value_str) or str(value_str).lower() in ['', 'nan', 'none', 'null']:
        return None
    
    try:
        value_str = str(value_str).strip()
        
        # Formatos comuns (expandidos)
        date_formats = [
            '%Y-%m-%d %H:%M:%S',    # 2026-10-18 00:00:00 (ISO com hora)
            '%Y-%m-%d',             # 2026-10-18 (ISO)
            '%d/%m/%Y',             # 18/10/2026 (BR)
            '%d-%m-%Y',             # 18-10-2026 (BR)
            '%Y/%m/%d',             # 2026/10/18
            '%d/%m/%y',             # 18/10/26
            '%Y-%m-%dT%H:%M:%S',    # 2026-10-18T00:00:00 (ISO T)
            '%Y-%m-%dT%H:%M:%SZ',   # 2026-10-18T00:00:00Z (ISO Z)
        ]
        
        for date_format in date_formats:
            try:
                dt = datetime.strptime(value_str, date_format)
                return dt  # Retorna datetime do Python para Excel
            except ValueError:
                continue
        
        # Tentar com pandas para casos mais complexos
        try:
            dt = pd.to_datetime(value_str, errors='raise')
            return dt.to_pydatetime()  # Converter Timestamp para datetime
        except:
            pass
        
        # Se nao conseguiu converter, retorna string original
        return value_str
        
    except:
        return value_str


def _smart_convert_value(value: Any) -> Any:
    """
    Conversao inteligente de valores para tipos apropriados (melhorada)
    """
    if isinstance(value, str) and value.strip():
        value_clean = value.strip()
        
        # Melhor detecção de datas
        # Verificar padrões específicos de data
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',           # YYYY-MM-DD
            r'\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}',  # YYYY-MM-DD HH:MM:SS
            r'\d{2}/\d{2}/\d{4}',           # DD/MM/YYYY
            r'\d{2}-\d{2}-\d{4}',           # DD-MM-YYYY
        ]
        
        is_likely_date = any(re.match(pattern, value_clean) for pattern in date_patterns)
        
        if is_likely_date:
            # Tentar converter como data primeiro
            date_result = _convert_date_value(value_clean)
            if isinstance(date_result, datetime):
                return date_result
        
        # Verificar se parece com valor financeiro
        if any(symbol in value_clean for symbol in ['R$', '%', '$', '€']) or value_clean.replace(',', '').replace('.', '').replace('-', '').isdigit():
            financial_result = _convert_financial_value(value_clean)
            if isinstance(financial_result, (int, float)):
                return financial_result
        
        # Se nao e nem data nem financeiro, retornar string
        return value_clean
    
    elif isinstance(value, (int, float)):
        return value
    
    elif value is None:
        return ""
    
    else:
        return str(value)

def _find_key_recursive(data: Any, target_key: str, max_depth: int = 50) -> Optional[Any]:
    """
    Busca recursiva otimizada com limite de profundidade
    """
    def _search(obj: Any, depth: int = 0) -> Optional[Any]:
        if depth > max_depth:
            return None
        
        if isinstance(obj, dict):
            # Busca direta primeiro (O(1))
            if target_key in obj:
                return obj[target_key]
            
            # Busca recursiva apenas em valores complexos
            for value in obj.values():
                if isinstance(value, (dict, list)):
                    result = _search(value, depth + 1)
                    if result is not None:
                        return result
        
        elif isinstance(obj, list):
            # Busca apenas em itens que podem conter a chave
            for item in obj:
                if isinstance(item, (dict, list)):
                    result = _search(item, depth + 1)
                    if result is not None:
                        return result
        
        return None
    
    return _search(data)

def _process_nested_structure_smart(obj: Any) -> Any:
    """
    Processa estruturas aninhadas preservando tipos (SEM reconversao)
    """
    if isinstance(obj, dict):
        # NAO aplicar smart_convert aqui, deixar para a tabela
        return {k: _process_nested_structure_smart(v) for k, v in obj.items()}
    
    elif isinstance(obj, list):
        if not obj:
            return obj
        
        # Para listas pequenas, NAO converter ainda
        if len(obj) <= 100:
            return [_process_nested_structure_smart(item) for item in obj]
        
        # Para listas grandes, verificar apenas primeiros elementos
        sample_size = min(3, len(obj))
        first_items = obj[:sample_size]
        
        # Se todos sao primitivos simples, converter para string
        if all(isinstance(item, (str, int, float, bool)) or item is None for item in first_items):
            return str(obj)
        
        # Caso contrario, processar recursivamente SEM converter
        return [_process_nested_structure_smart(item) for item in obj]
    
    else:
        # NAO converter aqui, deixar valores originais
        return obj

def _build_table_from_dict_list_smart(data_list: List[Dict[str, Any]]) -> List[List]:
    """
    Constroi tabela a partir de lista de dicionarios preservando tipos (DEBUG)
    """
    if not data_list:
        return [["Lista vazia"]]
    
    print(f"DEBUG: Construindo tabela com {len(data_list)} itens")
    
    # Coletar todas as chaves unicas
    all_keys = set()
    for item in data_list:
        if isinstance(item, dict):
            all_keys.update(item.keys())
    
    if not all_keys:
        return [["Dados invalidos"]]
    
    headers = sorted(all_keys)
    result = [headers]
    
    print(f"DEBUG: Headers: {headers}")
    
    # Construcao da tabela preservando tipos
    for i, item in enumerate(data_list):
        if isinstance(item, dict):
            row = []
            for header in headers:
                original_value = item.get(header)
                converted_value = _smart_convert_value(original_value)
                
                # Debug apenas primeira linha
                if i == 0:
                    print(f"DEBUG: '{header}': '{original_value}' -> {converted_value} (tipo: {type(converted_value)})")
                
                row.append(converted_value)
            
            result.append(row)
    
    return result

def _build_table_from_dict_smart(data_dict: Dict[str, Any]) -> List[List]:
    """
    Constroi tabela chave-valor preservando tipos (DEBUG)
    """
    result = [["Chave", "Valor"]]
    
    print(f"DEBUG DICT: Processando {len(data_dict)} chaves")
    
    for key, value in data_dict.items():
        converted_value = _smart_convert_value(value)
        print(f"DEBUG DICT: '{key}': '{value}' -> {converted_value} (tipo: {type(converted_value)})")
        result.append([str(key), converted_value])
    
    return result

def _build_table_from_list_smart(data_list: List[Any]) -> List[List]:
    """
    Constroi tabela a partir de lista preservando tipos
    """
    if not data_list:
        return [["Lista vazia"]]
    
    result = [["Valor"]]
    for item in data_list:
        converted_item = _smart_convert_value(item)
        result.append([converted_item])
    return result

def _convert_to_table(data: Any) -> List[List]:
    """
    Conversao principal para tabela com tipos preservados
    """
    if data is None:
        return [["Chave nao encontrada"]]
    
    # Processar estrutura aninhada com conversao inteligente
    processed_data = _process_nested_structure_smart(data)
    
    # Determinar estrategia de conversao baseada no tipo
    if isinstance(processed_data, list):
        if not processed_data:
            return [["Lista vazia"]]
        
        # Lista de dicionarios -> tabela estruturada
        if isinstance(processed_data[0], dict):
            return _build_table_from_dict_list_smart(processed_data)
        else:
            return _build_table_from_list_smart(processed_data)
    
    elif isinstance(processed_data, dict):
        return _build_table_from_dict_smart(processed_data)
    
    else:
        # Valor primitivo
        converted_value = _smart_convert_value(processed_data)
        return [["Resultado"], [converted_value]]

class AmFiReadJSONLogic:
    """
    Logica de negocio para AmFiReadJSON com conversao de tipos otimizada
    """
    
    @staticmethod
    def _validate_inputs(caminho_arquivo: str, chave: str) -> Optional[str]:
        """
        Valida entradas e retorna mensagem de erro se invalida
        """
        if not caminho_arquivo or not caminho_arquivo.strip():
            return "ERRO: Caminho do arquivo nao fornecido"
        
        if not chave or not chave.strip():
            return "ERRO: Nome da chave nao fornecido"
        
        return None
    
    @staticmethod
    def execute(caminho_arquivo: str, chave: str) -> List[List]:
        """
        Executa a logica do AmFiReadJSON com tratamento robusto de erros
        e conversao de tipos para numeros e datas
        """
        try:
            # Validacao de entrada
            validation_error = AmFiReadJSONLogic._validate_inputs(caminho_arquivo, chave)
            if validation_error:
                return [[validation_error]]
            
            # Carregar JSON com cache
            json_data = load_json_cached(caminho_arquivo.strip())
            
            # Busca otimizada
            found_data = _find_key_recursive(json_data, chave.strip())
            
            if found_data is None:
                return [[f"Chave '{chave}' nao encontrada"]]
            
            # Construir tabela com tipos preservados
            return _convert_to_table(found_data)
            
        except FileNotFoundError:
            return [["ERRO: Arquivo nao encontrado"]]
        except ValueError as e:
            return [[f"ERRO: {str(e)}"]]
        except MemoryError:
            return [["ERRO: Arquivo muito grande para processar"]]
        except (TypeError, AttributeError) as e:
            return [[f"ERRO: Estrutura de dados invalida - {str(e)}"]]
        except Exception as e:
            return [[f"ERRO: {type(e).__name__} - {str(e)}"]]