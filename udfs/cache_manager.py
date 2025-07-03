# SOLU��O 1: Recriar cache_manager.py com codifica��o UTF-8 correta
# Copie este c�digo COMPLETO e substitua todo o conte�do do cache_manager.py

"""
Cache Manager - Gestao unificada de cache para CSV, JSON e XLSX
"""
import os
from typing import Dict, Any, Optional
import pandas as pd
import json

# Caches globais
_csv_cache: Dict[str, pd.DataFrame] = {}
_json_cache: Dict[str, Dict[str, Any]] = {}
_xlsx_cache: Dict[str, pd.DataFrame] = {}

# Cache para data de último clear automático
_last_auto_clear_date: Optional[str] = None

def _get_cache_key(file_path: str) -> str:
    """
    Gera chave de cache baseada no caminho e timestamp de modificacao
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Arquivo nao encontrado: {file_path}")
    
    mtime = os.path.getmtime(file_path)
    return f"{file_path}_{mtime}"

def _cleanup_old_cache(file_path: str, cache: Dict[str, Any]) -> None:
    """
    Remove entradas antigas do cache para o mesmo arquivo
    """
    old_keys = [k for k in cache.keys() if k.startswith(file_path)]
    for key in old_keys:
        del cache[key]

def load_csv_cached(file_path: str) -> pd.DataFrame:
    """
    Carrega CSV com cache preservando tipos de dados nativos
    """
    try:
        # Gerar chave de cache
        cache_key = _get_cache_key(file_path)
        
        # Verificar cache
        if cache_key in _csv_cache:
            return _csv_cache[cache_key]
        
        # Limpar cache antigo do mesmo arquivo
        _cleanup_old_cache(file_path, _csv_cache)
        
        # Carregar arquivo CSV preservando tipos nativos
        df = pd.read_csv(
            file_path,
            encoding='utf-8',
            sep=';'
            # REMOVIDO: dtype='string', na_filter=False
        )
        
        # Verificar coluna Nome
        if 'Nome' not in df.columns:
            raise ValueError("Coluna 'Nome' nao encontrada no arquivo")
        
        # Cache do resultado
        _csv_cache[cache_key] = df
        return df
        
    except Exception as e:
        raise Exception(f"Erro ao carregar arquivo CSV: {str(e)}")

def load_json_cached(file_path: str) -> Dict[str, Any]:
    """
    Carrega JSON com cache baseado na data de modificacao
    """
    try:
        # Gerar chave de cache
        cache_key = _get_cache_key(file_path)
        
        # Verificar cache
        if cache_key in _json_cache:
            return _json_cache[cache_key]
        
        # Limpar cache antigo do mesmo arquivo
        _cleanup_old_cache(file_path, _json_cache)
        
        # Carregar JSON
        with open(file_path, 'r', encoding='utf-8') as file:
            json_data = json.load(file)
        
        # Cache do resultado
        _json_cache[cache_key] = json_data
        return json_data
        
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON invalido: {str(e)}")
    except UnicodeDecodeError:
        raise ValueError("Erro de codificacao. Verifique se o arquivo esta em UTF-8")
    except Exception as e:
        raise Exception(f"Erro ao carregar arquivo JSON: {str(e)}")

def load_xlsx_cached(file_path: str) -> pd.DataFrame:
    """
    Carrega XLSX com cache baseado na data de modificacao do arquivo
    PRESERVANDO tipos de dados nativos (numeros, datas)
    """
    try:
        # Gerar chave de cache
        cache_key = _get_cache_key(file_path)
        
        # Verificar cache
        if cache_key in _xlsx_cache:
            return _xlsx_cache[cache_key]
        
        # Limpar cache antigo do mesmo arquivo
        _cleanup_old_cache(file_path, _xlsx_cache)
        
        # Carregar arquivo XLSX preservando tipos nativos
        df = pd.read_excel(
            file_path,
            # REMOVIDO: dtype='string' 
            # REMOVIDO: na_filter=False
            # Deixar pandas inferir tipos automaticamente
        )
        
        # Verificar coluna Pool
        if 'Pool' not in df.columns:
            raise ValueError("Coluna 'Pool' nao encontrada no arquivo")
        
        # Cache do resultado
        _xlsx_cache[cache_key] = df
        return df
        
    except Exception as e:
        raise Exception(f"Erro ao carregar arquivo XLSX: {str(e)}")

def clear_csv_cache() -> int:
    """
    Limpa cache de arquivos CSV
    """
    global _csv_cache
    count = len(_csv_cache)
    _csv_cache.clear()
    return count

def clear_json_cache() -> int:
    """
    Limpa cache de arquivos JSON
    """
    global _json_cache
    count = len(_json_cache)
    _json_cache.clear()
    return count

def clear_xlsx_cache() -> int:
    """
    Limpa cache de arquivos XLSX
    """
    global _xlsx_cache
    count = len(_xlsx_cache)
    _xlsx_cache.clear()
    return count

def clear_all_cache() -> str:
    """
    Limpa todos os caches
    """
    csv_count = clear_csv_cache()
    json_count = clear_json_cache()
    xlsx_count = clear_xlsx_cache()
    total = csv_count + json_count + xlsx_count
    return f"Cache limpo. {total} arquivos removidos (CSV: {csv_count}, JSON: {json_count}, XLSX: {xlsx_count})."

def get_cache_stats() -> Dict[str, int]:
    """
    Retorna estatisticas dos caches
    """
    return {
        'csv_files': len(_csv_cache),
        'json_files': len(_json_cache),
        'xlsx_files': len(_xlsx_cache),
        'total_files': len(_csv_cache) + len(_json_cache) + len(_xlsx_cache)
    }

def auto_clear_daily_cache() -> bool:
    """
    Limpa cache automaticamente se for um novo dia
    Retorna True se o cache foi limpo
    """
    global _last_auto_clear_date
    from datetime import datetime
    
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    if _last_auto_clear_date != current_date:
        # Limpar apenas caches de dados diários (CSV e XLSX)
        csv_count = clear_csv_cache()
        xlsx_count = clear_xlsx_cache()
        _last_auto_clear_date = current_date
        return True
    
    return False

def warm_cache_with_latest() -> Dict[str, str]:
    """
    Pré-carrega cache com arquivos mais recentes
    """
    from file_discovery import get_latest_csv, get_latest_xlsx
    
    results = {
        'csv': 'Not loaded',
        'xlsx': 'Not loaded'
    }
    
    # Tentar carregar CSV mais recente
    csv_path = get_latest_csv()
    if csv_path:
        try:
            load_csv_cached(csv_path)
            results['csv'] = f'Loaded: {os.path.basename(csv_path)}'
        except Exception as e:
            results['csv'] = f'Error: {str(e)}'
    
    # Tentar carregar XLSX mais recente
    xlsx_path = get_latest_xlsx()
    if xlsx_path:
        try:
            load_xlsx_cached(xlsx_path)
            results['xlsx'] = f'Loaded: {os.path.basename(xlsx_path)}'
        except Exception as e:
            results['xlsx'] = f'Error: {str(e)}'
    
    return results